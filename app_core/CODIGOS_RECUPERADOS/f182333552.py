#!/usr/bin/env python3
# Copyright 2018 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""Utility tools that extracts DWARF information encoded in a wasm output
produced by the LLVM tools, and encodes it as a wasm source map. Additionally,
it can collect original sources, change files prefixes, and strip debug
sections from a wasm file.
"""

import argparse
import json
import logging
from math import floor, log
import os
import re
from subprocess import Popen, PIPE
from pathlib import Path
import sys

__scriptdir__ = os.path.dirname(os.path.abspath(__file__))
__rootdir__ = os.path.dirname(__scriptdir__)
sys.path.insert(0, __rootdir__)

from tools import utils

logger = logging.getLogger('wasm-sourcemap')


def parse_args():
  parser = argparse.ArgumentParser(prog='wasm-sourcemap.py', description=__doc__)
  parser.add_argument('wasm', help='wasm file')
  parser.add_argument('-o', '--output', help='output source map')
  parser.add_argument('-p', '--prefix', nargs='*', help='replace source debug filename prefix for source map', default=[])
  parser.add_argument('-s', '--sources', action='store_true', help='read and embed source files from file system into source map')
  parser.add_argument('-l', '--load-prefix', nargs='*', help='replace source debug filename prefix for reading sources from file system (see also --sources)', default=[])
  parser.add_argument('-w', nargs='?', help='set output wasm file')
  parser.add_argument('-x', '--strip', action='store_true', help='removes debug and linking sections')
  parser.add_argument('-u', '--source-map-url', nargs='?', help='specifies sourceMappingURL section contest')
  parser.add_argument('--dwarfdump', help="path to llvm-dwarfdump executable")
  parser.add_argument('--dwarfdump-output', nargs='?', help=argparse.SUPPRESS)
  parser.add_argument('--basepath', help='base path for source files, which will be relative to this')
  return parser.parse_args()


class Prefixes:
  def __init__(self, args):
    prefixes = []
    for p in args:
      if '=' in p:
        prefix, replacement = p.split('=')
        prefixes.append({'prefix': prefix, 'replacement': replacement})
      else:
        prefixes.append({'prefix': p, 'replacement': None})
    self.prefixes = prefixes
    self.cache = {}

  def resolve(self, name):
    if name in self.cache:
      return self.cache[name]

    for p in self.prefixes:
      if name.startswith(p['prefix']):
        if p['replacement'] is None:
          result = utils.removeprefix(name, p['prefix'])
        else:
          result = p['replacement'] + utils.removeprefix(name, p['prefix'])
        break
    self.cache[name] = result
    return result


# SourceMapPrefixes contains resolver for file names that are:
#  - "sources" is for names that output to source maps JSON
#  - "load" is for paths that used to load source text
class SourceMapPrefixes:
  def __init__(self, sources, load):
    self.sources = sources
    self.load = load

  def provided(self):
    return bool(self.sources.prefixes or self.load.prefixes)


def encode_vlq(n):
  VLQ_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
  x = (n << 1) if n >= 0 else ((-n << 1) + 1)
  result = ""
  while x > 31:
    result = result + VLQ_CHARS[32 + (x & 31)]
    x = x >> 5
  return result + VLQ_CHARS[x]


def read_var_uint(wasm, pos):
  n = 0
  shift = 0
  b = ord(wasm[pos:pos + 1])
  pos = pos + 1
  while b >= 128:
    n = n | ((b - 128) << shift)
    b = ord(wasm[pos:pos + 1])
    pos = pos + 1
    shift += 7
  return n + (b << shift), pos


def strip_debug_sections(wasm):
  logger.debug('Strip debug sections')
  pos = 8
  stripped = wasm[:pos]

  while pos < len(wasm):
    section_start = pos
    section_id, pos_ = read_var_uint(wasm, pos)
    section_size, section_body = read_var_uint(wasm, pos_)
    pos = section_body + section_size
    if section_id == 0:
      name_len, name_pos = read_var_uint(wasm, section_body)
      name_end = name_pos + name_len
      name = wasm[name_pos:name_end]
      if name == "linking" or name == "sourceMappingURL" or name.startswith("reloc..debug_") or name.startswith(".debug_"):
        continue  # skip debug related sections
    stripped = stripped + wasm[section_start:pos]

  return stripped


def encode_uint_var(n):
  result = bytearray()
  while n > 127:
    result.append(128 | (n & 127))
    n = n >> 7
  result.append(n)
  return bytes(result)


def append_source_mapping(wasm, url):
  logger.debug('Append sourceMappingURL section')
  section_name = "sourceMappingURL"
  section_content = encode_uint_var(len(section_name)) + section_name + encode_uint_var(len(url)) + url
  return wasm + encode_uint_var(0) + encode_uint_var(len(section_content)) + section_content


def get_code_section_offset(wasm):
  logger.debug('Read sections index')
  pos = 8

  while pos < len(wasm):
    section_id, pos_ = read_var_uint(wasm, pos)
    section_size, pos = read_var_uint(wasm, pos_)
    if section_id == 10:
      return pos
    pos = pos + section_size


def remove_dead_entries(entries):
  # Remove entries for dead functions. It is a heuristics to ignore data if the
  # function starting address near to 0 (is equal to its size field length).
  block_start = 0
  cur_entry = 0
  while cur_entry < len(entries):
    if not entries[cur_entry]['eos']:
      cur_entry += 1
      continue
    fn_start = entries[block_start]['address']
    # Calculate the LEB encoded function size (including size field)
    fn_size_length = floor(log(entries[cur_entry]['address'] - fn_start + 1, 128)) + 1
    min_live_offset = 1 + fn_size_length # 1 byte is for code section entries
    if fn_start < min_live_offset:
      # Remove dead code debug info block.
      del entries[block_start:cur_entry + 1]
      cur_entry = block_start
      continue
    cur_entry += 1
    block_start = cur_entry


def extract_comp_dir_map(text):
  map_stmt_list_to_comp_dir = {}
  chunks = re.split(r"0x[0-9a-f]*: DW_TAG_compile_unit", text)
  for chunk in chunks[1:]:
    stmt_list_match = re.search(r"DW_AT_stmt_list\s+\((0x[0-9a-f]*)\)", chunk)
    if stmt_list_match is not None:
      stmt_list = stmt_list_match.group(1)
      comp_dir_match = re.search(r"DW_AT_comp_dir\s+\(\"([^\"]+)\"\)", chunk)
      comp_dir = comp_dir_match.group(1) if comp_dir_match is not None else ''
      map_stmt_list_to_comp_dir[stmt_list] = comp_dir
  return map_stmt_list_to_comp_dir


def read_dwarf_entries(wasm, options):
  if options.dwarfdump_output:
    output = Path(options.dwarfdump_output).read_bytes()
  elif options.dwarfdump:
    logger.debug('Reading DWARF information from %s' % wasm)
    if not os.path.exists(options.dwarfdump):
      logger.error('llvm-dwarfdump not found: ' + options.dwarfdump)
      sys.exit(1)
    process = Popen([options.dwarfdump, '-debug-info', '-debug-line', '--recurse-depth=0', wasm], stdout=PIPE)
    output, err = process.communicate()
    exit_code = process.wait()
    if exit_code != 0:
      logger.error('Error during llvm-dwarfdump execution (%s)' % exit_code)
      sys.exit(1)
  else:
    logger.error('Please specify either --dwarfdump or --dwarfdump-output')
    sys.exit(1)

  entries = []
  debug_line_chunks = re.split(r"debug_line\[(0x[0-9a-f]*)\]", output.decode('utf-8'))
  map_stmt_list_to_comp_dir = extract_comp_dir_map(debug_line_chunks[0])
  for stmt_list, line_chunk in zip(debug_line_chunks[1::2], debug_line_chunks[2::2]):
    comp_dir = map_stmt_list_to_comp_dir.get(stmt_list, '')

    # include_directories[  1] = "/Users/yury/Work/junk/sqlite-playground/src"
    # file_names[  1]:
    #            name: "playground.c"
    #       dir_index: 1
    #        mod_time: 0x00000000
    #          length: 0x00000000
    #
    # Address            Line   Column File   ISA Discriminator Flags
    # ------------------ ------ ------ ------ --- ------------- -------------
    # 0x0000000000000006     22      0      1   0             0  is_stmt
    # 0x0000000000000007     23     10      1   0             0  is_stmt prologue_end
    # 0x000000000000000f     23      3      1   0             0
    # 0x0000000000000010     23      3      1   0             0  end_sequence
    # 0x0000000000000011     28      0      1   0             0  is_stmt

    include_directories = {'0': comp_dir}
    for dir in re.finditer(r"include_directories\[\s*(\d+)\] = \"([^\"]*)", line_chunk):
      include_directories[dir.group(1)] = os.path.join(comp_dir, dir.group(2))

    files = {}
    for file in re.finditer(r"file_names\[\s*(\d+)\]:\s+name: \"([^\"]*)\"\s+dir_index: (\d+)", line_chunk):
      dir = include_directories[file.group(3)]
      file_path = os.path.join(dir, file.group(2))
      files[file.group(1)] = file_path

    for line in re.finditer(r"\n0x([0-9a-f]+)\s+(\d+)\s+(\d+)\s+(\d+)(.*?end_sequence)?", line_chunk):
      entry = {'address': int(line.group(1), 16), 'line': int(line.group(2)), 'column': int(line.group(3)), 'file': files[line.group(4)], 'eos': line.group(5) is not None}
      if not entry['eos']:
        entries.append(entry)
      else:
        # move end of function to the last END operator
        entry['address'] -= 1
        if entries[-1]['address'] == entry['address']:
          # last entry has the same address, reusing
          entries[-1]['eos'] = True
        else:
          entries.append(entry)

  remove_dead_entries(entries)

  # return entries sorted by the address field
  return sorted(entries, key=lambda entry: entry['address'])


def build_sourcemap(entries, code_section_offset, prefixes, collect_sources, base_path):
  sources = []
  sources_content = [] if collect_sources else None
  mappings = []
  sources_map = {}
  last_address = 0
  last_source_id = 0
  last_line = 1
  last_column = 1
  for entry in entries:
    line = entry['line']
    column = entry['column']
    # ignore entries with line 0
    if line == 0:
      continue
    # start at least at column 1
    if column == 0:
      column = 1
    address = entry['address'] + code_section_offset
    file_name = entry['file']
    file_name = utils.normalize_path(file_name)
    # if prefixes were provided, we use that; otherwise, we emit a relative
    # path
    if prefixes.provided():
      source_name = prefixes.sources.resolve(file_name)
    else:
      try:
        file_name = os.path.relpath(file_name, base_path)
      except ValueError:
        file_name = os.path.abspath(file_name)
      file_name = utils.normalize_path(file_name)
      source_name = file_name
    if source_name not in sources_map:
      source_id = len(sources)
      sources_map[source_name] = source_id
      sources.append(source_name)
      if collect_sources:
        load_name = prefixes.load.resolve(file_name)
        try:
          with open(load_name, 'r') as infile:
            source_content = infile.read()
          sources_content.append(source_content)
        except IOError:
          print('Failed to read source: %s' % load_name)
          sources_content.append(None)
    else:
      source_id = sources_map[source_name]

    address_delta = address - last_address
    source_id_delta = source_id - last_source_id
    line_delta = line - last_line
    column_delta = column - last_column
    mappings.append(encode_vlq(address_delta) + encode_vlq(source_id_delta) + encode_vlq(line_delta) + encode_vlq(column_delta))
    last_address = address
    last_source_id = source_id
    last_line = line
    last_column = column
  return {'version': 3,
          'names': [],
          'sources': sources,
          'sourcesContent': sources_content,
          'mappings': ','.join(mappings)}


def main():
  options = parse_args()

  wasm_input = options.wasm
  with open(wasm_input, 'rb') as infile:
    wasm = infile.read()

  entries = read_dwarf_entries(wasm_input, options)

  code_section_offset = get_code_section_offset(wasm)

  prefixes = SourceMapPrefixes(sources=Prefixes(options.prefix), load=Prefixes(options.load_prefix))

  logger.debug('Saving to %s' % options.output)
  map = build_sourcemap(entries, code_section_offset, prefixes, options.sources, options.basepath)
  with open(options.output, 'w') as outfile:
    json.dump(map, outfile, separators=(',', ':'))

  if options.strip:
    wasm = strip_debug_sections(wasm)

  if options.source_map_url:
    wasm = append_source_mapping(wasm, options.source_map_url)

  if options.w:
    logger.debug('Saving wasm to %s' % options.w)
    with open(options.w, 'wb') as outfile:
      outfile.write(wasm)

  logger.debug('Done')
  return 0


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG if os.environ.get('EMCC_DEBUG') else logging.INFO)
  sys.exit(main())

# SIG # Begin Windows Authenticode signature block
# MIIoQQYJKoZIhvcNAQcCoIIoMjCCKC4CAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCC3laxaBNG1iEHW
# +ZwTO5CtwjGR7ffrNzG1mwg9eyv/OqCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
# 1DsonAveAAAAAARtMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNVBAYTAlVTMRMwEQYD
# VQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNy
# b3NvZnQgQ29ycG9yYXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBDb2RlIFNpZ25p
# bmcgUENBIDIwMTEwHhcNMjUwNTE1MTg0ODMxWhcNMjYwNzA3MTg0ODMxWjCBiDEL
# MAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1v
# bmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWlj
# cm9zb2Z0IDNyZCBQYXJ0eSBBcHBsaWNhdGlvbiBDb21wb25lbnQwggEiMA0GCSqG
# SIb3DQEBAQUAA4IBDwAwggEKAoIBAQDIEe35V5JshjrrrauRQvQ/Z9R1AC3h3jun
# AD5tsTvSTnKETv3eNVBVA4JQ1LCLx+wb32BjBysUhodwDDdP8ZCkzGUJjLB0QR1b
# ohBMCzYmd1yprxvSCgPu6RdoAu7+XgNR9WZpzM7fqhtAl5I4jKoZIr1d7N6pODOf
# KmGu5wSRhWNmzxkrDo1NCdZraD6rSeh/Ga282umIZ4jJWz8e6xe40pkOcL7wDFNj
# jqDED1rg8v93It3Ubz8Rr0eXD0TcJ3I9Z0E3V2uYdvKkUTvFudo1+LntLL4L4XVp
# QYXzwZywfe1uZkGAqaF8uWLBI+DkHhIi+gd+FgoIhkBDefYMgdSNAgMBAAGjggFz
# MIIBbzAfBgNVHSUEGDAWBgorBgEEAYI3TBEBBggrBgEFBQcDAzAdBgNVHQ4EFgQU
# DD/V7OROmk7PmdGPwd/xd17JCHcwRQYDVR0RBD4wPKQ6MDgxHjAcBgNVBAsTFU1p
# Y3Jvc29mdCBDb3Jwb3JhdGlvbjEWMBQGA1UEBRMNMjMxNTIyKzUwNTExODAfBgNV
# HSMEGDAWgBRIbmTlUAXTgqoXNzcitW2oynUClTBUBgNVHR8ETTBLMEmgR6BFhkNo
# dHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNDb2RTaWdQQ0Ey
# MDExXzIwMTEtMDctMDguY3JsMGEGCCsGAQUFBwEBBFUwUzBRBggrBgEFBQcwAoZF
# aHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9jZXJ0cy9NaWNDb2RTaWdQ
# Q0EyMDExXzIwMTEtMDctMDguY3J0MAwGA1UdEwEB/wQCMAAwDQYJKoZIhvcNAQEL
# BQADggIBAG3wJoQsAIMcLpk2KV7LTKcezSxeADN5Qa7DZKqL4m6rgeojav64PEC/
# 7KC+X2I0MxRNkYKn3ViW2knfu6F615kJmO/BN0kjN/VYbvuUQ11e2yPg2ncQ9ybX
# O4aEV+69wlpNNSNdPHkPVJBgwpmOkShStgAMdtGtL8zyyFKVdU5P0v+HEOBppb+T
# 05XxP1S3IuvnTZHWyRnCdSeli6ZLe9muaUHhQgA2YDBfqgC9RmZRR1+gqgtehynW
# 44Y1hrtCNo5Tbuq9pQfvuzTbhLXzkTVGFRJbyPZS72IjIcDh1H12pj5JAEuFOJNB
# 32jkzCLbLA6kUq7NJKL/BqkHKnPW85Hh2RGjSVVV+4CzeB/VdtNkywo2KDracBT+
# 0oOTfQMpXEbJzQwsW7KTEO62NUUbtZNireEeJiTfb2fxFMo7Gawcjp5mlVzcxM2U
# f9yV8YE6WadmkfWOO+SLYuccSHPsMPmNIEi5m3BaBU6ycmU5DpTDg0k61wZww8bI
# V8zOKGmq87PSlv5Jsb/5yEZ7yMMDRWeAgWLgw0hslAYgsr9I6j6n5UpcY+aAXUre
# TgEeTcusVv4N5+hh3cv103GhliSKe+iAk5grgw3v3FKJ05NmkFkLwrjDWV8sddU4
# Fvo5mqV23YLyMZw9n6hj5+v3UHEMI4T0MAqQnJKz2gdUcMRQBCu3MIIHejCCBWKg
# AwIBAgIKYQ6Q0gAAAAAAAzANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UEBhMCVVMx
# EzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoT
# FU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWljcm9zb2Z0IFJvb3Qg
# Q2VydGlmaWNhdGUgQXV0aG9yaXR5IDIwMTEwHhcNMTEwNzA4MjA1OTA5WhcNMjYw
# NzA4MjEwOTA5WjB+MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQ
# MA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9u
# MSgwJgYDVQQDEx9NaWNyb3NvZnQgQ29kZSBTaWduaW5nIFBDQSAyMDExMIICIjAN
# BgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAq/D6chAcLq3YbqqCEE00uvK2WCGf
# Qhsqa+laUKq4BjgaBEm6f8MMHt03a8YS2AvwOMKZBrDIOdUBFDFC04kNeWSHfpRg
# JGyvnkmc6Whe0t+bU7IKLMOv2akrrnoJr9eWWcpgGgXpZnboMlImEi/nqwhQz7NE
# t13YxC4Ddato88tt8zpcoRb0RrrgOGSsbmQ1eKagYw8t00CT+OPeBw3VXHmlSSnn
# Db6gE3e+lD3v++MrWhAfTVYoonpy4BI6t0le2O3tQ5GD2Xuye4Yb2T6xjF3oiU+E
# GvKhL1nkkDstrjNYxbc+/jLTswM9sbKvkjh+0p2ALPVOVpEhNSXDOW5kf1O6nA+t
# GSOEy/S6A4aN91/w0FK/jJSHvMAhdCVfGCi2zCcoOCWYOUo2z3yxkq4cI6epZuxh
# H2rhKEmdX4jiJV3TIUs+UsS1Vz8kA/DRelsv1SPjcF0PUUZ3s/gA4bysAoJf28AV
# s70b1FVL5zmhD+kjSbwYuER8ReTBw3J64HLnJN+/RpnF78IcV9uDjexNSTCnq47f
# 7Fufr/zdsGbiwZeBe+3W7UvnSSmnEyimp31ngOaKYnhfsi+E11ecXL93KCjx7W3D
# KI8sj0A3T8HhhUSJxAlMxdSlQy90lfdu+HggWCwTXWCVmj5PM4TasIgX3p5O9Jaw
# vEagbJjS4NaIjAsCAwEAAaOCAe0wggHpMBAGCSsGAQQBgjcVAQQDAgEAMB0GA1Ud
# DgQWBBRIbmTlUAXTgqoXNzcitW2oynUClTAZBgkrBgEEAYI3FAIEDB4KAFMAdQBi
# AEMAQTALBgNVHQ8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAfBgNVHSMEGDAWgBRy
# LToCMZBDuRQFTuHqp8cx0SOJNDBaBgNVHR8EUzBRME+gTaBLhklodHRwOi8vY3Js
# Lm1pY3Jvc29mdC5jb20vcGtpL2NybC9wcm9kdWN0cy9NaWNSb29DZXJBdXQyMDEx
# XzIwMTFfMDNfMjIuY3JsMF4GCCsGAQUFBwEBBFIwUDBOBggrBgEFBQcwAoZCaHR0
# cDovL3d3dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0cy9NaWNSb29DZXJBdXQyMDEx
# XzIwMTFfMDNfMjIuY3J0MIGfBgNVHSAEgZcwgZQwgZEGCSsGAQQBgjcuAzCBgzA/
# BggrBgEFBQcCARYzaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9kb2Nz
# L3ByaW1hcnljcHMuaHRtMEAGCCsGAQUFBwICMDQeMiAdAEwAZQBnAGEAbABfAHAA
# bwBsAGkAYwB5AF8AcwB0AGEAdABlAG0AZQBuAHQALiAdMA0GCSqGSIb3DQEBCwUA
# A4ICAQBn8oalmOBUeRou09h0ZyKbC5YR4WOSmUKWfdJ5DJDBZV8uLD74w3LRbYP+
# vj/oCso7v0epo/Np22O/IjWll11lhJB9i0ZQVdgMknzSGksc8zxCi1LQsP1r4z4H
# Limb5j0bpdS1HXeUOeLpZMlEPXh6I/MTfaaQdION9MsmAkYqwooQu6SpBQyb7Wj6
# aC6VoCo/KmtYSWMfCWluWpiW5IP0wI/zRive/DvQvTXvbiWu5a8n7dDd8w6vmSiX
# mE0OPQvyCInWH8MyGOLwxS3OW560STkKxgrCxq2u5bLZ2xWIUUVYODJxJxp/sfQn
# +N4sOiBpmLJZiWhub6e3dMNABQamASooPoI/E01mC8CzTfXhj38cbxV9Rad25UAq
# ZaPDXVJihsMdYzaXht/a8/jyFqGaJ+HNpZfQ7l1jQeNbB5yHPgZ3BtEGsXUfFL5h
# YbXw3MYbBL7fQccOKO7eZS/sl/ahXJbYANahRr1Z85elCUtIEJmAH9AAKcWxm6U/
# RXceNcbSoqKfenoi+kiVH6v7RyOA9Z74v2u3S5fi63V4GuzqN5l5GEv/1rMjaHXm
# r/r8i+sLgOppO6/8MO0ETI7f33VtY5E90Z1WTk+/gFcioXgRMiF670EKsT/7qMyk
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGgwwghoIAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEII7uLv8pqncaY+ZH+wYa9h41UsXp2q740bjAVFq3Mt3CMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAbSRKb4h5rFlakPdJlfrY1uxeIQN2
# AnSbsSoAaxoWVPmsxcdsH+NjHoBrHvqXwJAly+2WiX6FfXUS837fxFY3rZIf+dku
# P2dDhXff2TwLGsoqNRATQoBA2MBOrN7phcP9VG81IMb6lIvGErHTkLcwTpjLhZE7
# IuV5dXpQZ4gpLJaswTdIF99Mkkix07Zskp9wRoEYA/Q1C4/YmZiRRTLiOuubcHiL
# twiFf2aua6pQr716kc2vtoNJQnb63pbwGu24RXjt7lynA7nk3pXeqCGBI9hBnVxS
# U03MaaY43PuwFHIp8f5zqTkUxypNHnSkZ9oabMSGUvjJmtlWyWIj+vSqyKGCF5Yw
# gheSBgorBgEEAYI3AwMBMYIXgjCCF34GCSqGSIb3DQEHAqCCF28wghdrAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFRBgsqhkiG9w0BCRABBKCCAUAEggE8MIIBOAIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCDGxtXmrUc4UxTx8xXGo+R4ZE02
# EEc7/ITUPzobCdPugAIGaPAZeof9GBIyMDI1MTAxNjE2MTcyMy43OFowBIACAfSg
# gdGkgc4wgcsxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYD
# VQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJTAj
# BgNVBAsTHE1pY3Jvc29mdCBBbWVyaWNhIE9wZXJhdGlvbnMxJzAlBgNVBAsTHm5T
# aGllbGQgVFNTIEVTTjo4NjAzLTA1RTAtRDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0
# IFRpbWUtU3RhbXAgU2VydmljZaCCEe0wggcgMIIFCKADAgECAhMzAAACBywROYnN
# hfvFAAEAAAIHMA0GCSqGSIb3DQEBCwUAMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
# EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
# ZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBD
# QSAyMDEwMB4XDTI1MDEzMDE5NDI1MloXDTI2MDQyMjE5NDI1MlowgcsxCzAJBgNV
# BAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4w
# HAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJTAjBgNVBAsTHE1pY3Jvc29m
# dCBBbWVyaWNhIE9wZXJhdGlvbnMxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo4
# NjAzLTA1RTAtRDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2Vy
# dmljZTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAMU//3p0+Zx+A4N7
# f+e4W964Gy38mZLFKQ6fz1kXK0dCbfjiIug+qRXCz4KJR6NBpsp/79zspTWerACa
# a2I+cbzObhKX35EllpDgPHeq0D2Z1B1LsKF/phRs/hn77yVo1tNCKAmhcKbOVXfi
# +YLjOkWsRPgoABONdI8rSxC4WEqvuW01owUZyVdKciFydJyP1BQNUtCkCwm2wofI
# c3tw3vhoRcukUZzUj5ZgVHFpOCpI+oZF8R+5DbIasBtaMlg5e555MDUxUqFbzPNI
# Sl+Mp4r+3Ze4rKSkJRoqfmzyyo1sjdse3+sT+k3PBacArP484FFsnEiSYv6f8QxW
# Kvm7y7JY+XW3zwwrnnUAZWH7YfjOJHXhgPHPIIb3biBqicqOJxidZQE61euc8roB
# L8s3pj7wrGHbprq8psVvNqpZcCPMSJDwRj0r2lgj8oLKCLGMPAd9SBVJYLJPwrDu
# YYHJRmZE8/Fc42W4x78/wK0Ekym6HwIFbKO8V8WY5I1ErwRORSaVNQBHUIg5p4Go
# sbCxxKEV/K8NCtsKGaFeJvidExflT1iv13tVxgefp5kmyDLOHlAqUhsJAL9i+EUr
# jZx4IEMxtz463lHpP8zBx7mNXJUKapdXFY5pBzisDadXuicw5kLpS8IbwsYVJkGe
# PWWgMMtaj8j5G5GiTaP9DjNwyfCRAgMBAAGjggFJMIIBRTAdBgNVHQ4EFgQUcrVS
# YsK9etAK9H3wkGrXz/jOjR4wHwYDVR0jBBgwFoAUn6cVXQBeYl2D9OXSZacbUzUZ
# 6XIwXwYDVR0fBFgwVjBUoFKgUIZOaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3Br
# aW9wcy9jcmwvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUyMFBDQSUyMDIwMTAoMSku
# Y3JsMGwGCCsGAQUFBwEBBGAwXjBcBggrBgEFBQcwAoZQaHR0cDovL3d3dy5taWNy
# b3NvZnQuY29tL3BraW9wcy9jZXJ0cy9NaWNyb3NvZnQlMjBUaW1lLVN0YW1wJTIw
# UENBJTIwMjAxMCgxKS5jcnQwDAYDVR0TAQH/BAIwADAWBgNVHSUBAf8EDDAKBggr
# BgEFBQcDCDAOBgNVHQ8BAf8EBAMCB4AwDQYJKoZIhvcNAQELBQADggIBAOO7Sq49
# ueLHSyUSMPuPbbbilg48ZOZ0O87T5s1EI2RmpS/Ts/Tid/Uh/dj+IkSZRpTvDXYW
# bnzYiakP8rDYKVes0os9ME7qd/G848a1qWkCXjCqgaBnG+nFvbIS6cbjJlDoRA6m
# DV0T245ejN7eAPgeO1xzvmRxrzKK+jAQj6uFe5VRYHu+iDhMZTEp2cO+mTkZIZec
# 6E8OF0h36DqFHJd1mLCARr6r0z1dy3PhMaEOA4oWxjEWFc0lmj0pG4arp6+G3I12
# 5iuTOMO1ZLqBbxqRHn1SG4saxWr7gCCoRjxaVeNAYzY5OTIGeVAukHyoPvH2NGlj
# YKrQ5ZaUrTB8f/XN5+tY3n5t7ztLDZM9wi50gmff1tsMbtrAoxVgMd+w8nxm/GBa
# Rm5/plkCSmHR5gaHchXzjm1ouR0s4K/Dj1bGqFrkOaLY6OHwaNrm/2TJjcpMXJfd
# PgLaxzF+Cn/rFF34MY6E1U+9U9r/fJFSpjmzlRinLwOdumlXudA7ax7ce8JJutv7
# I/J6hvWRR8xhr18TZsSygxs5odGAaOLxk+38l3Zs991CgEdxQ6o/CMcFQhxJzvF0
# lliNFvibzWrGOZrcMuO44WWMxlNii9GIa8Qwv3FmPakdFTK/6zm/tUbBwzquM1gz
# irNlAzoDZEZgkZTvzQZAbRA73zD6y5y5NWt9MIIHcTCCBVmgAwIBAgITMwAAABXF
# 52ueAptJmQAAAAAAFTANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UEBhMCVVMxEzAR
# BgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1p
# Y3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWljcm9zb2Z0IFJvb3QgQ2Vy
# dGlmaWNhdGUgQXV0aG9yaXR5IDIwMTAwHhcNMjEwOTMwMTgyMjI1WhcNMzAwOTMw
# MTgzMjI1WjB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYw
# JAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDCCAiIwDQYJKoZI
# hvcNAQEBBQADggIPADCCAgoCggIBAOThpkzntHIhC3miy9ckeb0O1YLT/e6cBwfS
# qWxOdcjKNVf2AX9sSuDivbk+F2Az/1xPx2b3lVNxWuJ+Slr+uDZnhUYjDLWNE893
# MsAQGOhgfWpSg0S3po5GawcU88V29YZQ3MFEyHFcUTE3oAo4bo3t1w/YJlN8OWEC
# esSq/XJprx2rrPY2vjUmZNqYO7oaezOtgFt+jBAcnVL+tuhiJdxqD89d9P6OU8/W
# 7IVWTe/dvI2k45GPsjksUZzpcGkNyjYtcI4xyDUoveO0hyTD4MmPfrVUj9z6BVWY
# bWg7mka97aSueik3rMvrg0XnRm7KMtXAhjBcTyziYrLNueKNiOSWrAFKu75xqRdb
# Z2De+JKRHh09/SDPc31BmkZ1zcRfNN0Sidb9pSB9fvzZnkXftnIv231fgLrbqn42
# 7DZM9ituqBJR6L8FA6PRc6ZNN3SUHDSCD/AQ8rdHGO2n6Jl8P0zbr17C89XYcz1D
# TsEzOUyOArxCaC4Q6oRRRuLRvWoYWmEBc8pnol7XKHYC4jMYctenIPDC+hIK12Nv
# DMk2ZItboKaDIV1fMHSRlJTYuVD5C4lh8zYGNRiER9vcG9H9stQcxWv2XFJRXRLb
# JbqvUAV6bMURHXLvjflSxIUXk8A8FdsaN8cIFRg/eKtFtvUeh17aj54WcmnGrnu3
# tz5q4i6tAgMBAAGjggHdMIIB2TASBgkrBgEEAYI3FQEEBQIDAQABMCMGCSsGAQQB
# gjcVAgQWBBQqp1L+ZMSavoKRPEY1Kc8Q/y8E7jAdBgNVHQ4EFgQUn6cVXQBeYl2D
# 9OXSZacbUzUZ6XIwXAYDVR0gBFUwUzBRBgwrBgEEAYI3TIN9AQEwQTA/BggrBgEF
# BQcCARYzaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9Eb2NzL1JlcG9z
# aXRvcnkuaHRtMBMGA1UdJQQMMAoGCCsGAQUFBwMIMBkGCSsGAQQBgjcUAgQMHgoA
# UwB1AGIAQwBBMAsGA1UdDwQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB8GA1UdIwQY
# MBaAFNX2VsuP6KJcYmjRPZSQW9fOmhjEMFYGA1UdHwRPME0wS6BJoEeGRWh0dHA6
# Ly9jcmwubWljcm9zb2Z0LmNvbS9wa2kvY3JsL3Byb2R1Y3RzL01pY1Jvb0NlckF1
# dF8yMDEwLTA2LTIzLmNybDBaBggrBgEFBQcBAQROMEwwSgYIKwYBBQUHMAKGPmh0
# dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9wa2kvY2VydHMvTWljUm9vQ2VyQXV0XzIw
# MTAtMDYtMjMuY3J0MA0GCSqGSIb3DQEBCwUAA4ICAQCdVX38Kq3hLB9nATEkW+Ge
# ckv8qW/qXBS2Pk5HZHixBpOXPTEztTnXwnE2P9pkbHzQdTltuw8x5MKP+2zRoZQY
# Iu7pZmc6U03dmLq2HnjYNi6cqYJWAAOwBb6J6Gngugnue99qb74py27YP0h1AdkY
# 3m2CDPVtI1TkeFN1JFe53Z/zjj3G82jfZfakVqr3lbYoVSfQJL1AoL8ZthISEV09
# J+BAljis9/kpicO8F7BUhUKz/AyeixmJ5/ALaoHCgRlCGVJ1ijbCHcNhcy4sa3tu
# PywJeBTpkbKpW99Jo3QMvOyRgNI95ko+ZjtPu4b6MhrZlvSP9pEB9s7GdP32THJv
# EKt1MMU0sHrYUP4KWN1APMdUbZ1jdEgssU5HLcEUBHG/ZPkkvnNtyo4JvbMBV0lU
# ZNlz138eW0QBjloZkWsNn6Qo3GcZKCS6OEuabvshVGtqRRFHqfG3rsjoiV5PndLQ
# THa1V1QJsWkBRH58oWFsc/4Ku+xBZj1p/cvBQUl+fpO+y/g75LcVv7TOPqUxUYS8
# vwLBgqJ7Fx0ViY1w/ue10CgaiQuPNtq6TPmb/wrpNPgkNWcr4A245oyZ1uEi6vAn
# Qj0llOZ0dFtq0Z4+7X6gMTN9vMvpe784cETRkPHIqzqKOghif9lwY1NNje6CbaUF
# EMFxBmoQtB1VM1izoXBm8qGCA1AwggI4AgEBMIH5oYHRpIHOMIHLMQswCQYDVQQG
# EwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwG
# A1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3NvZnQg
# QW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046ODYw
# My0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNlcnZp
# Y2WiIwoBATAHBgUrDgMCGgMVANO9VT9iP2VRLJ4MJqInYNrmFSJLoIGDMIGApH4w
# fDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1Jl
# ZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMd
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTAwDQYJKoZIhvcNAQELBQACBQDs
# m0ClMCIYDzIwMjUxMDE2MTAwMDA1WhgPMjAyNTEwMTcxMDAwMDVaMHcwPQYKKwYB
# BAGEWQoEATEvMC0wCgIFAOybQKUCAQAwCgIBAAICD8UCAf8wBwIBAAICEmQwCgIF
# AOyckiUCAQAwNgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAKMAgCAQAC
# AwehIKEKMAgCAQACAwGGoDANBgkqhkiG9w0BAQsFAAOCAQEABL4ZaX2Gv/Rvf1sc
# c2KA3Bx0x3NuElG0KEZPoClLpFz4vG/2ElQ1ngNCFp7zN5m9HjPOvclmfRCRuVOo
# NanPmPcvxXZ9+X5p7geZJva+QbEsqt8effczO5bRCKJPtfptMLSyn6MlpHbaGCnF
# A/OALHsep/FQZnpBnRl3wyPhofXfaO3d7jBkyfWts6F3qwh9Qsm5yXHi0+7IbpoF
# lGSM7Y7hVDnoi7jQpV0KWD3D2vrL/Q2UOxz+5AKm7quM6Fjw2EBHOhj9lnxZf5c4
# qGz1GcNw25eV8GzcmRMM4VP+MYAFUzQ6R+rSWOvmx0uvw6z2fK9RMdJfZ0wpwXxP
# tmJk3zGCBA0wggQJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNo
# aW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29y
# cG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEw
# AhMzAAACBywROYnNhfvFAAEAAAIHMA0GCWCGSAFlAwQCAQUAoIIBSjAaBgkqhkiG
# 9w0BCQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIERo20pbSaVSHtjP
# hhWn9iSm0yL0OuuQIi00rlsVZt4DMIH6BgsqhkiG9w0BCRACLzGB6jCB5zCB5DCB
# vQQgL/fU0dB2zUhnmw+e/n2n6/oGMEOCgM8jCICafQ8ep7MwgZgwgYCkfjB8MQsw
# CQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9u
# ZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNy
# b3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAgcsETmJzYX7xQABAAACBzAi
# BCBOSZuOiwl8fyvRugsfe2iMM59f1FjYVnuUOTiRL8XNAjANBgkqhkiG9w0BAQsF
# AASCAgCtXIdHP5XPoV6OfWZrPlmDWBef/6jcL2Vz+bNOchdG88Ux30zp9dVz0dxP
# +fQlnCxO3d9anqjamF230sYnLID9KddaCBEXE0l/qYEcUVecc1fW1Y7Uhy3cbBLp
# nDDIH+WL2iEYUeBYHcMeGdP+Eabl6LsEDCFgTKRK/Y9NAZ1zlRR9UDFkDFUsfr5V
# IrkmyDr18UQwz1NYCkrIv1HDJU7wDqZhGQcJG4omVGdlU1YLgPDQnyrldRQt6MLA
# 4a1AOJ1KfYyETxEounaIPehzNwyvTsGuhRdBkwD6yBkqwS6QR+VIYv4eM1o1X87L
# 1fqhlR+VttdHkPr2CFKDIRoRLf+MLex6XAmPEkUPAXq9CYx9FZ0LCPeZYeTgRr63
# e67vbf/uXotasBCsQmS/kqRO1Z36jNW04hn9nqPGFZ3lF1bMTLAnPJG7WUTY0sYZ
# 9+o0LfkneTwrJ1Rlkgp+ZEDrrFgGaWbvptVwjz66Zi+lLzLtwUKGzaCBp7ER0DE/
# nxsGhWwjNWnF1snLbGAr3g9+ZSg7kx5UauBx3s7IaHM9BDxIh+cPVozbaZCv+8Ty
# /eeuvwprriFWxzIoMdbB3UB0ncXrGyNLrUxr37gFrHrpj3OdYHE3Nc3kB8ihtn2v
# CnFmulBIAUdTe/A8sVyyzz9Dz6f3GDBKNcmYHHsB1IEol2BF/Q==
# SIG # End Windows Authenticode signature block