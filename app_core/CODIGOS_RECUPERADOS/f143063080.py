#!/usr/bin/env python3

# This is a utility for looking up the symbol names and/or file+line numbers
# of code addresses. There are several possible sources of this information,
# with varying granularity (listed here in approximate preference order).

# If the wasm has DWARF info, llvm-symbolizer can show the symbol, file, and
# line/column number, potentially including inlining.
# If the wasm has separate DWARF info, do the above with the side file
# If there is a source map, we can parse it to get file and line number.
# If there is an emscripten symbol map, we can use that to get the symbol name
# If there is a name section or symbol table, llvm-symbolizer can show the
#  symbol name.
# Separate DWARF and emscripten symbol maps are not supported yet.

import argparse
import json
import os
import re
import subprocess
import sys
from tools import shared
from tools import webassembly

LLVM_SYMBOLIZER = os.path.expanduser(
    shared.build_llvm_tool_path(shared.exe_suffix('llvm-symbolizer')))


class Error(BaseException):
  pass


# Class to treat location info in a uniform way across information sources.
class LocationInfo(object):
  def __init__(self, source=None, line=0, column=0, func=None):
    self.source = source
    self.line = line
    self.column = column
    self.func = func

  def print(self):
    source = self.source if self.source else '??'
    func = self.func if self.func else '??'
    print(f'{func}\n{source}:{self.line}:{self.column}')


def get_codesec_offset(module):
  sec = module.get_section(webassembly.SecType.CODE)
  if not sec:
    raise Error(f'No code section found in {module.filename}')
  return sec.offset


def has_debug_line_section(module):
  return module.get_custom_section('.debug_line') is not None


def has_name_section(module):
  return module.get_custom_section('name') is not None


def has_linking_section(module):
  return module.get_custom_section('linking') is not None


def symbolize_address_symbolizer(module, address, is_dwarf):
  if is_dwarf:
    vma_adjust = get_codesec_offset(module)
  else:
    vma_adjust = 0
  cmd = [LLVM_SYMBOLIZER, '-e', module.filename, f'--adjust-vma={vma_adjust}',
         str(address)]
  out = shared.run_process(cmd, stdout=subprocess.PIPE).stdout.strip()
  out_lines = out.splitlines()

  # Source location regex, e.g., /abc/def.c:3:5
  SOURCE_LOC_RE = re.compile(r'(.+):(\d+):(\d+)$')
  # llvm-symbolizer prints two lines per location. The first line contains a
  # function name, and the second contains a source location like
  # '/abc/def.c:3:5'. If the function or source info is not available, it will
  # be printed as '??', in which case we store None. If the line and column info
  # is not available, they will be printed as 0, which we store as is.
  for i in range(0, len(out_lines), 2):
    func, loc_str = out_lines[i], out_lines[i + 1]
    m = SOURCE_LOC_RE.match(loc_str)
    source, line, column = m.group(1), m.group(2), m.group(3)
    if func == '??':
      func = None
    if source == '??':
      source = None
    LocationInfo(source, line, column, func).print()


def get_sourceMappingURL_section(module):
  for sec in module.sections():
    if sec.name == "sourceMappingURL":
      return sec
  return None


class WasmSourceMap(object):
  class Location(object):
    def __init__(self, source=None, line=0, column=0, func=None):
      self.source = source
      self.line = line
      self.column = column
      self.func = func

  def __init__(self):
    self.version = None
    self.sources = []
    self.mappings = {}
    self.offsets = []

  def parse(self, filename):
    with open(filename) as f:
      source_map_json = json.loads(f.read())
      if shared.DEBUG:
        print(source_map_json)

    self.version = source_map_json['version']
    self.sources = source_map_json['sources']

    vlq_map = {}
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    for i, c in enumerate(chars):
      vlq_map[c] = i

    def decodeVLQ(string):
      result = []
      shift = 0
      value = 0
      for c in string:
        try:
          integer = vlq_map[c]
        except ValueError:
          raise Error(f'Invalid character ({c}) in VLQ')
        value += (integer & 31) << shift
        if integer & 32:
          shift += 5
        else:
          negate = value & 1
          value >>= 1
          result.append(-value if negate else value)
          value = shift = 0
      return result

    offset = 0
    src = 0
    line = 1
    col = 1
    for segment in source_map_json['mappings'].split(','):
      data = decodeVLQ(segment)
      info = []

      offset += data[0]
      if len(data) >= 2:
        src += data[1]
        info.append(src)
      if len(data) >= 3:
        line += data[2]
        info.append(line)
      if len(data) >= 4:
        col += data[3]
        info.append(col)
      # TODO: see if we need the name, which is the next field (data[4])

      self.mappings[offset] = WasmSourceMap.Location(*info)
      self.offsets.append(offset)
    self.offsets.sort()

  def find_offset(self, offset):
    # Find the largest mapped offset <= the search offset
    lo = 0
    hi = len(self.offsets)

    while lo < hi:
      mid = (lo + hi) // 2
      if self.offsets[mid] > offset:
        hi = mid
      else:
        lo = mid + 1
    return self.offsets[lo - 1]

  def lookup(self, offset):
    nearest = self.find_offset(offset)
    assert nearest in self.mappings, 'Sourcemap has an offset with no mapping'
    info = self.mappings[nearest]
    return LocationInfo(
        self.sources[info.source] if info.source is not None else None,
        info.line,
        info.column
      )


def symbolize_address_sourcemap(module, address, force_file):
  URL = force_file
  if not URL:
    # If a sourcemap file is not forced, read it from the wasm module
    section = get_sourceMappingURL_section(module)
    assert section
    module.seek(section.offset)
    assert module.read_string() == 'sourceMappingURL'
    # TODO: support stripping/replacing a prefix from the URL
    URL = module.read_string()

  if shared.DEBUG:
    print(f'Source Mapping URL: {URL}')
  sm = WasmSourceMap()
  sm.parse(URL)
  if shared.DEBUG:
    csoff = get_codesec_offset(module)
    print(sm.mappings)
    # Print with section offsets to easily compare against dwarf
    for k, v in sm.mappings.items():
      print(f'{k-csoff:x}: {v}')
  sm.lookup(address).print()


def main(args):
  with webassembly.Module(args.wasm_file) as module:
    base = 16 if args.address.lower().startswith('0x') else 10
    address = int(args.address, base)

    if args.addrtype == 'code':
      address += get_codesec_offset(module)

    if ((has_debug_line_section(module) and not args.source) or
       'dwarf' in args.source):
      symbolize_address_symbolizer(module, address, is_dwarf=True)
    elif ((get_sourceMappingURL_section(module) and not args.source) or
          'sourcemap' in args.source):
      symbolize_address_sourcemap(module, address, args.file)
    elif ((has_name_section(module) and not args.source) or
          'names' in args.source):
      symbolize_address_symbolizer(module, address, is_dwarf=False)
    elif ((has_linking_section(module) and not args.source) or
          'symtab' in args.source):
      symbolize_address_symbolizer(module, address, is_dwarf=False)
    else:
      raise Error('No .debug_line or sourceMappingURL section found in '
                  f'{module.filename}.'
                  " I don't know how to symbolize this file yet")


def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--source', choices=['dwarf', 'sourcemap',
                                                 'names', 'symtab'],
                      help='Force debug info source type', default=())
  parser.add_argument('-f', '--file', action='store',
                      help='Force debug info source file')
  parser.add_argument('-t', '--addrtype', choices=['code', 'file'],
                      default='file',
                      help='Address type (code section or file offset)')
  parser.add_argument('-v', '--verbose', action='store_true',
                      help='Print verbose info for debugging this script')
  parser.add_argument('wasm_file', help='Wasm file')
  parser.add_argument('address', help='Address to lookup')
  args = parser.parse_args()
  if args.verbose:
    shared.PRINT_SUBPROCS = 1
    shared.DEBUG = True
  return args


if __name__ == '__main__':
  try:
    rv = main(get_args())
  except (Error, webassembly.InvalidWasmError, OSError) as e:
    print(f'{sys.argv[0]}: {str(e)}', file=sys.stderr)
    rv = 1
  sys.exit(rv)

# SIG # Begin Windows Authenticode signature block
# MIIoZwYJKoZIhvcNAQcCoIIoWDCCKFQCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCDtPw8m5OIFnbLE
# 9g1izqUXGGkjZ/kUXEjFNtBA84TTeKCCDZowggYYMIIEAKADAgECAhMzAAAEbLAG
# JNKSnG/gAAAAAARsMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNVBAYTAlVTMRMwEQYD
# VQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNy
# b3NvZnQgQ29ycG9yYXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBDb2RlIFNpZ25p
# bmcgUENBIDIwMTEwHhcNMjUwNTE1MTg0ODMwWhcNMjYwNzA3MTg0ODMwWjCBiDEL
# MAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1v
# bmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWlj
# cm9zb2Z0IDNyZCBQYXJ0eSBBcHBsaWNhdGlvbiBDb21wb25lbnQwggEiMA0GCSqG
# SIb3DQEBAQUAA4IBDwAwggEKAoIBAQCz70xLkah79Z5HXrDk1IFHHkud7j1kZefc
# eEdQnR0UWU5WlL2RhCftii4Ex1xQLBh5Y26nOVYVSUfWILNwjCaq+N0t7V38qk5h
# fQ0H4rulaBkgzkg0fsp89iXCh3YPMEUe17iJZlGSF0is16PaZ15wlhxf4eXo6fO5
# t+k1hAp2dvjBQEUhQZQjpX950u8kk7c/aTc4uU+S/ziWzKvsdp28qIyFe2Q8fZ6y
# nsANHvXlrPjJ7q12gcTKogtgSJUye3ISuwOjbBsMv5ifXMPMDqzMNJGKY1Z3iaIv
# JSKfyyJkdJkXbvLQMLgsytToUklgk2k+kAGsDc+fVPLUYPX02nsRAgMBAAGjggGC
# MIIBfjAfBgNVHSUEGDAWBgorBgEEAYI3TBEBBggrBgEFBQcDAzAdBgNVHQ4EFgQU
# +THphZBFVCz14Kvwgr3e/s1pM1gwVAYDVR0RBE0wS6RJMEcxLTArBgNVBAsTJE1p
# Y3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGltaXRlZDEWMBQGA1UEBRMNMjMx
# NTIyKzUwNTEyMzAfBgNVHSMEGDAWgBRIbmTlUAXTgqoXNzcitW2oynUClTBUBgNV
# HR8ETTBLMEmgR6BFhkNodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2Ny
# bC9NaWNDb2RTaWdQQ0EyMDExXzIwMTEtMDctMDguY3JsMGEGCCsGAQUFBwEBBFUw
# UzBRBggrBgEFBQcwAoZFaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9j
# ZXJ0cy9NaWNDb2RTaWdQQ0EyMDExXzIwMTEtMDctMDguY3J0MAwGA1UdEwEB/wQC
# MAAwDQYJKoZIhvcNAQELBQADggIBAJ7qVkCcWiACY/XmN1Xc6BbhlX1/sLOxN1zU
# /6fIXCSBuDZSRNyRnL8oUq3EsMW/5bYaibkKP/fggdYpUS8EQ+PMUDDRfAVPOR8e
# z/YzVKsWdYc6PbBsGguSOQMR4c5hfdXMlIhlM/hUK3mYNO4TBTjHkX83Q3VyxQln
# wxvGrvISQf1MYOoGvEDq0YeNJwigl8AIpcmGajbLAN+FJjfZBW6+blzCgYyTzZad
# b3F7oWpE37pinRsSwuE118rimOqi2pbHGdQwBrFWP7nGrkd5ZZy/zqDUg3vKzqEW
# YjKWIe+D1OiGNKOSjInDi1975tkDJcBZceX4cEdxfL9rQNWi64+5J0ekbsPpZcx1
# k9LhnDQCazKnD7wPsI3BVmgWPL/LC/qOf46eXaNNPTrTk5UZarZkcelO8ICD9/7y
# osXrSax9J5Otl8y0fxBlB8jVuSRhxBoyDos8/zpjie7xRUnF0pgXR+qah7c5vXF+
# YyVVQsmjxC+/h/Usgq1DJVgwSUPCiZJ+gazeiC6YIqqNKLuRZYTaI6f3PmswvTtq
# k3q7w7M6EE+gtmq2SaDqkLfWNchWF2Z4NXh845IOaixBamj/KKV/98KxmJO+WAqL
# 621x9dL4Iq+2KT2M8E5vfHaHCROrjfkMrfmdAEsq2tSNjVo7yd36ISbfsrjwhV4O
# VNa67xHCMIIHejCCBWKgAwIBAgIKYQ6Q0gAAAAAAAzANBgkqhkiG9w0BAQsFADCB
# iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1Jl
# ZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMp
# TWljcm9zb2Z0IFJvb3QgQ2VydGlmaWNhdGUgQXV0aG9yaXR5IDIwMTEwHhcNMTEw
# NzA4MjA1OTA5WhcNMjYwNzA4MjEwOTA5WjB+MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSgwJgYDVQQDEx9NaWNyb3NvZnQgQ29kZSBTaWduaW5n
# IFBDQSAyMDExMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAq/D6chAc
# Lq3YbqqCEE00uvK2WCGfQhsqa+laUKq4BjgaBEm6f8MMHt03a8YS2AvwOMKZBrDI
# OdUBFDFC04kNeWSHfpRgJGyvnkmc6Whe0t+bU7IKLMOv2akrrnoJr9eWWcpgGgXp
# ZnboMlImEi/nqwhQz7NEt13YxC4Ddato88tt8zpcoRb0RrrgOGSsbmQ1eKagYw8t
# 00CT+OPeBw3VXHmlSSnnDb6gE3e+lD3v++MrWhAfTVYoonpy4BI6t0le2O3tQ5GD
# 2Xuye4Yb2T6xjF3oiU+EGvKhL1nkkDstrjNYxbc+/jLTswM9sbKvkjh+0p2ALPVO
# VpEhNSXDOW5kf1O6nA+tGSOEy/S6A4aN91/w0FK/jJSHvMAhdCVfGCi2zCcoOCWY
# OUo2z3yxkq4cI6epZuxhH2rhKEmdX4jiJV3TIUs+UsS1Vz8kA/DRelsv1SPjcF0P
# UUZ3s/gA4bysAoJf28AVs70b1FVL5zmhD+kjSbwYuER8ReTBw3J64HLnJN+/RpnF
# 78IcV9uDjexNSTCnq47f7Fufr/zdsGbiwZeBe+3W7UvnSSmnEyimp31ngOaKYnhf
# si+E11ecXL93KCjx7W3DKI8sj0A3T8HhhUSJxAlMxdSlQy90lfdu+HggWCwTXWCV
# mj5PM4TasIgX3p5O9JawvEagbJjS4NaIjAsCAwEAAaOCAe0wggHpMBAGCSsGAQQB
# gjcVAQQDAgEAMB0GA1UdDgQWBBRIbmTlUAXTgqoXNzcitW2oynUClTAZBgkrBgEE
# AYI3FAIEDB4KAFMAdQBiAEMAQTALBgNVHQ8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB
# /zAfBgNVHSMEGDAWgBRyLToCMZBDuRQFTuHqp8cx0SOJNDBaBgNVHR8EUzBRME+g
# TaBLhklodHRwOi8vY3JsLm1pY3Jvc29mdC5jb20vcGtpL2NybC9wcm9kdWN0cy9N
# aWNSb29DZXJBdXQyMDExXzIwMTFfMDNfMjIuY3JsMF4GCCsGAQUFBwEBBFIwUDBO
# BggrBgEFBQcwAoZCaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0cy9N
# aWNSb29DZXJBdXQyMDExXzIwMTFfMDNfMjIuY3J0MIGfBgNVHSAEgZcwgZQwgZEG
# CSsGAQQBgjcuAzCBgzA/BggrBgEFBQcCARYzaHR0cDovL3d3dy5taWNyb3NvZnQu
# Y29tL3BraW9wcy9kb2NzL3ByaW1hcnljcHMuaHRtMEAGCCsGAQUFBwICMDQeMiAd
# AEwAZQBnAGEAbABfAHAAbwBsAGkAYwB5AF8AcwB0AGEAdABlAG0AZQBuAHQALiAd
# MA0GCSqGSIb3DQEBCwUAA4ICAQBn8oalmOBUeRou09h0ZyKbC5YR4WOSmUKWfdJ5
# DJDBZV8uLD74w3LRbYP+vj/oCso7v0epo/Np22O/IjWll11lhJB9i0ZQVdgMknzS
# Gksc8zxCi1LQsP1r4z4HLimb5j0bpdS1HXeUOeLpZMlEPXh6I/MTfaaQdION9Msm
# AkYqwooQu6SpBQyb7Wj6aC6VoCo/KmtYSWMfCWluWpiW5IP0wI/zRive/DvQvTXv
# biWu5a8n7dDd8w6vmSiXmE0OPQvyCInWH8MyGOLwxS3OW560STkKxgrCxq2u5bLZ
# 2xWIUUVYODJxJxp/sfQn+N4sOiBpmLJZiWhub6e3dMNABQamASooPoI/E01mC8Cz
# TfXhj38cbxV9Rad25UAqZaPDXVJihsMdYzaXht/a8/jyFqGaJ+HNpZfQ7l1jQeNb
# B5yHPgZ3BtEGsXUfFL5hYbXw3MYbBL7fQccOKO7eZS/sl/ahXJbYANahRr1Z85el
# CUtIEJmAH9AAKcWxm6U/RXceNcbSoqKfenoi+kiVH6v7RyOA9Z74v2u3S5fi63V4
# GuzqN5l5GEv/1rMjaHXmr/r8i+sLgOppO6/8MO0ETI7f33VtY5E90Z1WTk+/gFci
# oXgRMiF670EKsT/7qMykXcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMT
# DXpQzTGCGiMwghofAgEBMIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNo
# aW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29y
# cG9yYXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIw
# MTECEzMAAARssAYk0pKcb+AAAAAABGwwDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZI
# hvcNAQkDMQwGCisGAQQBgjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcC
# ARUwLwYJKoZIhvcNAQkEMSIEIJTSSqSYL3gXU8NES+yrkJlcMMMrpPA2qJ0zbNWD
# Mc3bMEIGCisGAQQBgjcCAQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBho
# dHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAT+wou8LJ
# V2Lj7EVXCqw+f8xeGe5SGkyb9t7Xx4QHVjYmIE9nULInIrHTeS+7rdZjmWlaDYlQ
# EDv6VEGRZwi8BRY0mJgOr/rp2E+fdPJLV1LdGGPtL/8+Mh9Ui6g0Z/tCkr3jCEGX
# KrK9rmMjF1sJJd6QZg4wM9S+xT5Jx7Hkf4hx9NB67tsU46/V5PzdQhvn4kxqQC4d
# 7vkZ0ixGvs7224mEM+/l8r+4q/h1jyc/NwCHZgv1rwwAqqjRfapTa5g4t6ZIgkdf
# k2N5Da7vgI8XGAiJaAhyvweOQiZOxCj1NixA4sEXLSOE8FoHMQzV41U17C++HRHG
# fIR7yy7/X3idMqGCF60wghepBgorBgEEAYI3AwMBMYIXmTCCF5UGCSqGSIb3DQEH
# AqCCF4YwgheCAgEDMQ8wDQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCC
# AUkEggFFMIIBQQIBAQYKKwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCDtlKFR
# NQkqEYdEuv8oSU9N/21CJmb03Ut3cXRihj1ywAIGaOmAzBXPGBMyMDI1MTAxNjE2
# MTY0Mi43MDhaMASAAgH0oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
# V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
# IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRp
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1NTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEfsw
# ggcoMIIFEKADAgECAhMzAAACG9CyuAJn93LPAAEAAAIbMA0GCSqGSIb3DQEBCwUA
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgzMFoX
# DTI2MTExMzE4NDgzMFowgdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xLTArBgNVBAsTJE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGlt
# aXRlZDEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjU1MUEtMDVFMC1EOTQ3MSUw
# IwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG
# 9w0BAQEFAAOCAg8AMIICCgKCAgEAjsWd52ZZkzB5Xe5g/l2GsOjAz30sg6jVxfFJ
# V+w4xIDVyaI3LO8bIpmzYul3AZHg50UIQ8PrSRZGpQqFkRNu+o3YKJ4g2uGYBRks
# HnHYR0uVSCQg58ThkYyeplGX3oAvGRVuPIpQtAiTsR76A/gdoU7HDwEbb73bJwTy
# rbKHhR+WaMy9DQHI4k5Qo4+bZDs0kj76bvhJvdGU+S8zxQBp7UAhjJnFqKxIusSI
# TE7zCCR422ELhkhVVOFqK2w6h1MAvILe76hxRIcPj0SBL2r8O9tx5njU4+tg2rAd
# U153pmyhqazdpUccYBE9wDRFUd/e9CoWx7TdnUicB+Mai7RT6qse7e5aGqX1B7bn
# j/ZHvrrfF+BJEIlS9iDXAUgekvXZ+FZmjvLwP+dN+0/crh++r4e8FknF7EX6IJfn
# mNeDN/68Z59kbaJ1f+P5mnKYfydCeZmxrGpS0taWkDk36D3jPVZflvxrc+1rhCIl
# M5v9agLEFI12QiBTfpOBOBr3AGCPk+eH0+latjQajug+2/BD12qb82500LQytUWT
# 2ota/HYnRgSv1jvZ0/dml1FsxWYzOnCrjfdB/7N6pNySt4vn+PGN6dFLim7kxos+
# B9WfQPezJi3fuKyyDAB9zSHPj1Zu8nZfecZJ9um4zj7DFgvJXTDTnG5qlG4ZdbFR
# a/rrfzkCAwEAAaOCAUkwggFFMB0GA1UdDgQWBBS2vp93/lxLppNK8OkauJ2AvNmI
# UDAfBgNVHSMEGDAWgBSfpxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSg
# UqBQhk5odHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3Nv
# ZnQlMjBUaW1lLVN0YW1wJTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEE
# YDBeMFwGCCsGAQUFBzAChlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3Bz
# L2NlcnRzL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNy
# dDAMBgNVHRMBAf8EAjAAMBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB
# /wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAgEAZkU1XxQD4OTM3GTht32TXShIfPBo
# MfSsFsBQqFOZqLJOxyJOllIBFpmpvOtGNPkC5Z8ldG8aCpvgFNo/jDWeT5FiW53d
# Aj9KnZxpsQ3Pf5fRzSGHRcxEMOdXIVzDJwcZUX0cjfxna7ydNv8eXB/Xk6G6SyrR
# 2OH6S1LHMW11m3UvKF+eLjIPl45rximuDCoEd+ad0lOAXA5/vZOKN5n/ePYeP0LR
# chZX0Q6H8n/ZmSPMlbli3MO851Q09RmT/ZGHa+/Fdy+WLDrwcYykV9mUy/4TbwKw
# 6FtdR6ZPHxMdIi1pk8Y2mC/GzCq0LCsH0uTFeQ6Q7Nc3MRmER/3mLWUhbaWHgX1F
# bYchvR22b+Bup+YPR5Q/0BhaaAN6AIBfcGs+u/nJoIByyZKA8cTyCmnUI/4vW6D4
# vywg3XBFf4f2DwFHy/evsC+58KMl+k2wa05X2kK0T/bCPLhaov9ZXyobawfNOLYG
# iauKT2FWvbwZzHIFCTxjBww6Pt5uRvCE/jnUcf/xhlOGMn6iKO9Xt49vZTE2SfIB
# k/34iLTRBJ6H7aGPTTQnza3OfWu1/dRycC6Wl5ons3PjnGXTSKSxXllJPmg6R/ul
# GonP/UCYoJ6mN+EXjfyDLPXLqsr91+VTG1rYzRCjPwBFAHv4EIwaE0ajCrf75eUG
# I3+oXU0UP6rloZ8wggdxMIIFWaADAgECAhMzAAAAFcXna54Cm0mZAAAAAAAVMA0G
# CSqGSIb3DQEBCwUAMIGIMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3Rv
# bjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0
# aW9uMTIwMAYDVQQDEylNaWNyb3NvZnQgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3Jp
# dHkgMjAxMDAeFw0yMTA5MzAxODIyMjVaFw0zMDA5MzAxODMyMjVaMHwxCzAJBgNV
# BAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4w
# HAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFBDQSAyMDEwMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIIC
# CgKCAgEA5OGmTOe0ciELeaLL1yR5vQ7VgtP97pwHB9KpbE51yMo1V/YBf2xK4OK9
# uT4XYDP/XE/HZveVU3Fa4n5KWv64NmeFRiMMtY0Tz3cywBAY6GB9alKDRLemjkZr
# BxTzxXb1hlDcwUTIcVxRMTegCjhuje3XD9gmU3w5YQJ6xKr9cmmvHaus9ja+NSZk
# 2pg7uhp7M62AW36MEBydUv626GIl3GoPz130/o5Tz9bshVZN7928jaTjkY+yOSxR
# nOlwaQ3KNi1wjjHINSi947SHJMPgyY9+tVSP3PoFVZhtaDuaRr3tpK56KTesy+uD
# RedGbsoy1cCGMFxPLOJiss254o2I5JasAUq7vnGpF1tnYN74kpEeHT39IM9zfUGa
# RnXNxF803RKJ1v2lIH1+/NmeRd+2ci/bfV+AutuqfjbsNkz2K26oElHovwUDo9Fz
# pk03dJQcNIIP8BDyt0cY7afomXw/TNuvXsLz1dhzPUNOwTM5TI4CvEJoLhDqhFFG
# 4tG9ahhaYQFzymeiXtcodgLiMxhy16cg8ML6EgrXY28MyTZki1ugpoMhXV8wdJGU
# lNi5UPkLiWHzNgY1GIRH29wb0f2y1BzFa/ZcUlFdEtsluq9QBXpsxREdcu+N+VLE
# hReTwDwV2xo3xwgVGD94q0W29R6HXtqPnhZyacaue7e3PmriLq0CAwEAAaOCAd0w
# ggHZMBIGCSsGAQQBgjcVAQQFAgMBAAEwIwYJKwYBBAGCNxUCBBYEFCqnUv5kxJq+
# gpE8RjUpzxD/LwTuMB0GA1UdDgQWBBSfpxVdAF5iXYP05dJlpxtTNRnpcjBcBgNV
# HSAEVTBTMFEGDCsGAQQBgjdMg30BATBBMD8GCCsGAQUFBwIBFjNodHRwOi8vd3d3
# Lm1pY3Jvc29mdC5jb20vcGtpb3BzL0RvY3MvUmVwb3NpdG9yeS5odG0wEwYDVR0l
# BAwwCgYIKwYBBQUHAwgwGQYJKwYBBAGCNxQCBAweCgBTAHUAYgBDAEEwCwYDVR0P
# BAQDAgGGMA8GA1UdEwEB/wQFMAMBAf8wHwYDVR0jBBgwFoAU1fZWy4/oolxiaNE9
# lJBb186aGMQwVgYDVR0fBE8wTTBLoEmgR4ZFaHR0cDovL2NybC5taWNyb3NvZnQu
# Y29tL3BraS9jcmwvcHJvZHVjdHMvTWljUm9vQ2VyQXV0XzIwMTAtMDYtMjMuY3Js
# MFoGCCsGAQUFBwEBBE4wTDBKBggrBgEFBQcwAoY+aHR0cDovL3d3dy5taWNyb3Nv
# ZnQuY29tL3BraS9jZXJ0cy9NaWNSb29DZXJBdXRfMjAxMC0wNi0yMy5jcnQwDQYJ
# KoZIhvcNAQELBQADggIBAJ1VffwqreEsH2cBMSRb4Z5yS/ypb+pcFLY+TkdkeLEG
# k5c9MTO1OdfCcTY/2mRsfNB1OW27DzHkwo/7bNGhlBgi7ulmZzpTTd2YurYeeNg2
# LpypglYAA7AFvonoaeC6Ce5732pvvinLbtg/SHUB2RjebYIM9W0jVOR4U3UkV7nd
# n/OOPcbzaN9l9qRWqveVtihVJ9AkvUCgvxm2EhIRXT0n4ECWOKz3+SmJw7wXsFSF
# QrP8DJ6LGYnn8AtqgcKBGUIZUnWKNsIdw2FzLixre24/LAl4FOmRsqlb30mjdAy8
# 7JGA0j3mSj5mO0+7hvoyGtmW9I/2kQH2zsZ0/fZMcm8Qq3UwxTSwethQ/gpY3UA8
# x1RtnWN0SCyxTkctwRQEcb9k+SS+c23Kjgm9swFXSVRk2XPXfx5bRAGOWhmRaw2f
# pCjcZxkoJLo4S5pu+yFUa2pFEUep8beuyOiJXk+d0tBMdrVXVAmxaQFEfnyhYWxz
# /gq77EFmPWn9y8FBSX5+k77L+DvktxW/tM4+pTFRhLy/AsGConsXHRWJjXD+57XQ
# KBqJC4822rpM+Zv/Cuk0+CQ1ZyvgDbjmjJnW4SLq8CdCPSWU5nR0W2rRnj7tfqAx
# M328y+l7vzhwRNGQ8cirOoo6CGJ/2XBjU02N7oJtpQUQwXEGahC0HVUzWLOhcGby
# oYIDVjCCAj4CAQEwggEBoYHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
# V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
# IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRp
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1NTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEB
# MAcGBSsOAwIaAxUAhoV6r49M4GBd41K1RYB1Z0f4zuCggYMwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybP1swIhgP
# MjAyNTEwMTYwOTU0MzVaGA8yMDI1MTAxNzA5NTQzNVowdDA6BgorBgEEAYRZCgQB
# MSwwKjAKAgUA7Js/WwIBADAHAgEAAgIdGzAHAgEAAgITyjAKAgUA7JyQ2wIBADA2
# BgorBgEEAYRZCgQCMSgwJjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIB
# AAIDAYagMA0GCSqGSIb3DQEBCwUAA4IBAQAJ7Yofw08kIFkzlGJDG4lHSkaYL3vP
# se+PSXw3C62ffLQkLHa7V0PiO9vq2xStkHCYDMoODs9PolHNYwC2aRNsHSupXjdj
# dnL+3aMcnHUHXuIL3xgkS99uB/I4aw92cy3qSJcmlcFMjeow8zmn5T/AHWzBVYAy
# l//Hz8ZOPk/TsS2CHBS+ptiJaUcOhH4Hq2V2sYilIQvNUz+6h5+HXtH/hj8EEnO6
# MD2swInB4KRCmXVTBodYqsvQEvpGBwqGC6KDWu9iifIZRzXrRplLMqMVcrGQdLOv
# +zzFSI00p4L8Q65rQ1cAuyqz/xbpyzBnkZUsyXMbClMEjMy7MjdIycPcMYIEDTCC
# BAkCAQEwgZMwfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAO
# BgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
# MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIb0LK4
# Amf3cs8AAQAAAhswDQYJYIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsq
# hkiG9w0BCRABBDAvBgkqhkiG9w0BCQQxIgQgzCRMZep4iZ74kaQ7/u/g22BIWU0d
# Iutn8taiey1O13UwgfoGCyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCAwJRSVuD2j
# mMcQCFXdLuJAwDpUVNZ6bc6dfJU83Q2LgDCBmDCBgKR+MHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwAhMzAAACG9CyuAJn93LPAAEAAAIbMCIEICE94ffjCxIA
# YyervspfrSCjYnH8L+jBZonZWLNBnhZ/MA0GCSqGSIb3DQEBCwUABIICADpRIG+I
# u/MHhiFV5tNcsOF55C+5Glp3mslFsoJR3bXPui8RDZU7jFjcjcQwEIsE9IfQ0/rh
# wIEUF5OgsZ8FxGi2IYenZ8xb3KnJQaFIlqb8neC8PBw80JNQ58M3LclZhNszEnEF
# EiBZpFmhX1fxc5I1Btscjy7/+ZN9ov3d7ktHjkfRG1CTHCCWPjdab9mUctnzsBfl
# tC1wj9uQ50L3H/kMpZ3yDeWKeT23BTU9gk3c6pjXpLGFf4+P93QSJEiGvO9rF2l8
# 6dwYfQeEpTlW0t5EUBJ61LUC20yZItk5LjkRsEyPYa87mH7lwJgOzbREg6svKGAn
# 8RTphAn+diq8HOlCAAQiVZD6xQZ1P00Rr06MAnhLAGPwmZow4rsvFkcDMxp3w2Zs
# +2gSgSKzEOzd0WJwXAVClf5k+IMZ9hmAqXLSjFQD1XNx1xVl3Rfts+vdGf9Kvqhw
# IOK3ZwI/M5RWDbSCc49CvjFpGCmso2t6+JEdPJw0mTqJ3IjMWPNk4Y8MN9CPeIXu
# XvtHCcFyoLiVtE1Pvf+tYWmKbfUzFOXEYFzluV6Kr3m0rThrKHFMbMJ3gOD/+unx
# /HDjur4eobtP397CAavV77ymNpH2h4MH5miBCe07BJszj82FiphrC2sjFG6D0FVI
# zgjhqUHFiFccvk/8gN0QIayB4awbt2xb5txy
# SIG # End Windows Authenticode signature block