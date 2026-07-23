#!/usr/bin/env python3
# coding=utf-8
# Copyright 2013 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""This tool extracts information about structs and defines from the C headers.

The JSON input format is as follows:
[
  {
    'file': 'some/header.h',
    'structs': {
      'struct_name': [
        'field1',
        'field2',
        'field3',
        {
          'field4': [
            'nested1',
            'nested2',
            {
              'nested3': [
                'deep_nested1',
                ...
              ]
            }
            ...
          ]
        },
        'field5'
      ],
      'other_struct': [
        'field1',
        'field2',
        ...
      ]
    },
    'defines': [
      'DEFINE_1',
      'DEFINE_2',
      ['f', 'FLOAT_DEFINE'],
      'DEFINE_3',
      ...
    ]
  },
  {
    'file': 'some/other/header.h',
    ...
  }
]

Please note that the 'f' for 'FLOAT_DEFINE' is just the format passed to printf(), you can put anything printf() understands.
If you call this script with the flag "-f" and pass a header file, it will create an automated boilerplate for you.
"""

import sys
import os
import re
import json
import argparse
import tempfile
import subprocess

__scriptdir__ = os.path.dirname(os.path.abspath(__file__))
__rootdir__ = os.path.dirname(os.path.dirname(__scriptdir__))
sys.path.insert(0, __rootdir__)

from tools import building
from tools import config
from tools import shared
from tools import system_libs
from tools import utils
from tools.settings import settings

QUIET = (__name__ != '__main__')
DEBUG = False


def show(msg):
  if shared.DEBUG or not QUIET:
    sys.stderr.write('gen_struct_info: %s\n' % msg)


# The following three functions generate C code. The output of the compiled code will be
# parsed later on and then put back together into a dict structure by parse_c_output().
#
# Example:
#   c_descent('test1', code)
#   c_set('item', 'i%i', '111', code)
#   c_set('item2', 'i%i', '9', code)
#   c_set('item3', 's%s', '"Hello"', code)
#   c_ascent(code)
#   c_set('outer', 'f%f', '0.999', code)
#
# Will result in:
#   {
#     'test1': {
#       'item': 111,
#       'item2': 9,
#       'item3': 'Hello',
#     },
#     'outer': 0.999
#   }
def c_set(name, type_, value, code):
  code.append('printf("K' + name + '\\n");')
  code.append('printf("V' + type_ + '\\n", ' + value + ');')


def c_descent(name, code):
  code.append('printf("D' + name + '\\n");')


def c_ascent(code):
  code.append('printf("A\\n");')


def parse_c_output(lines):
  result = {}
  cur_level = result
  parent = []
  key = None

  for line in lines:
    arg = line[1:].strip()
    if '::' in arg:
      arg = arg.split('::', 1)[1]
    if line[0] == 'K':
      # This is a key
      key = arg
    elif line[0] == 'V':
      # A value
      if arg[0] == 'i':
        arg = int(arg[1:])
      elif arg[0] == 'f':
        arg = float(arg[1:])
      elif arg[0] == 's':
        arg = arg[1:]

      cur_level[key] = arg
    elif line[0] == 'D':
      # Remember the current level as the last parent.
      parent.append(cur_level)

      # We descend one level.
      cur_level[arg] = {}
      cur_level = cur_level[arg]
    elif line[0] == 'A':
      # We return to the parent dict. (One level up.)
      cur_level = parent.pop()

  return result


def gen_inspect_code(path, struct, code):
  if path[0][-1] == '#':
    path[0] = path[0].rstrip('#')
    prefix = ''
  else:
    prefix = 'struct '

  c_descent(path[-1], code)

  if len(path) == 1:
    c_set('__size__', 'i%zu', 'sizeof (' + prefix + path[0] + ')', code)
  else:
    c_set('__size__', 'i%zu', 'sizeof ((' + prefix + path[0] + ' *)0)->' + '.'.join(path[1:]), code)
    # c_set('__offset__', 'i%zu', 'offsetof(' + prefix + path[0] + ', ' + '.'.join(path[1:]) + ')', code)

  for field in struct:
    if isinstance(field, dict):
      # We have to recurse to inspect the nested dict.
      fname = list(field.keys())[0]
      gen_inspect_code(path + [fname], field[fname], code)
    else:
      c_set(field, 'i%zu', 'offsetof(' + prefix + path[0] + ', ' + '.'.join(path[1:] + [field]) + ')', code)

  c_ascent(code)


def inspect_headers(headers, cflags):
  code = ['#include <stdio.h>', '#include <stddef.h>']
  for header in headers:
    code.append('#include "' + header['name'] + '"')

  code.append('int main() {')
  c_descent('structs', code)
  for header in headers:
    for name, struct in header['structs'].items():
      gen_inspect_code([name], struct, code)

  c_ascent(code)
  c_descent('defines', code)
  for header in headers:
    for name, type_ in header['defines'].items():
      # Add the necessary python type, if missing.
      if '%' not in type_:
        if type_[-1] in ('d', 'i', 'u'):
          # integer
          type_ = 'i%' + type_
        elif type_[-1] in ('f', 'F', 'e', 'E', 'g', 'G'):
          # float
          type_ = 'f%' + type_
        elif type_[-1] in ('x', 'X', 'a', 'A', 'c', 's'):
          # hexadecimal or string
          type_ = 's%' + type_

      c_set(name, type_, name, code)

  code.append('return 0;')
  code.append('}')

  # Write the source code to a temporary file.
  src_file = tempfile.mkstemp('.c', text=True)
  show('Generating C code... ' + src_file[1])
  os.write(src_file[0], '\n'.join(code).encode())

  js_file = tempfile.mkstemp('.js')

  # Check sanity early on before populating the cache with libcompiler_rt
  # If we don't do this the parallel build of compiler_rt will run while holding the cache
  # lock and with EM_EXCLUSIVE_CACHE_ACCESS set causing N processes to race to run sanity checks.
  # While this is not in itself serious problem it is wasteful and noise on stdout.
  # For the same reason we run this early in embuilder.py and emcc.py.
  # TODO(sbc): If we can remove EM_EXCLUSIVE_CACHE_ACCESS then this would not longer be needed.
  shared.check_sanity()

  compiler_rt = system_libs.Library.get_usable_variations()['libcompiler_rt'].build()

  # Close all unneeded FDs.
  os.close(src_file[0])
  os.close(js_file[0])

  info = []
  # Compile the program.
  show('Compiling generated code...')

  if any('libcxxabi' in f for f in cflags):
    compiler = shared.EMXX
  else:
    compiler = shared.EMCC

  node_flags = building.get_emcc_node_flags(shared.check_node_version())

  # -O1+ produces calls to iprintf, which libcompiler_rt doesn't support
  cmd = [compiler] + cflags + ['-o', js_file[1], src_file[1],
                               '-O0',
                               '-Werror',
                               '-Wno-format',
                               '-nostdlib',
                               compiler_rt,
                               '-sBOOTSTRAPPING_STRUCT_INFO',
                               '-sINCOMING_MODULE_JS_API=',
                               '-sSTRICT',
                               '-sASSERTIONS=0'] + node_flags

  # Default behavior for emcc is to warn for binaryen version check mismatches
  # so we should try to match that behavior.
  cmd += ['-Wno-error=version-check']

  # TODO(sbc): Remove this one we remove the test_em_config_env_var test
  cmd += ['-Wno-deprecated']

  if settings.LTO:
    cmd += ['-flto=' + settings.LTO]

  if settings.MEMORY64:
    # Always use =2 here so that we don't generate binar that actually requires
    # memeory64 to run.  All we care about is that the output is correct.
    cmd += ['-sMEMORY64=2', '-Wno-experimental']

  show(shared.shlex_join(cmd))
  try:
    subprocess.check_call(cmd, env=system_libs.clean_env())
  except subprocess.CalledProcessError as e:
    sys.stderr.write('FAIL: Compilation failed!: %s\n' % e.cmd)
    sys.exit(1)

  # Run the compiled program.
  show('Calling generated program... ' + js_file[1])
  args = []
  if settings.MEMORY64:
    args += shared.node_bigint_flags(config.NODE_JS)
  info = shared.run_js_tool(js_file[1], node_args=args, stdout=shared.PIPE).splitlines()

  if not DEBUG:
    # Remove all temporary files.
    os.unlink(src_file[1])

    if os.path.exists(js_file[1]):
      os.unlink(js_file[1])
      wasm_file = shared.replace_suffix(js_file[1], '.wasm')
      os.unlink(wasm_file)

  # Parse the output of the program into a dict.
  return parse_c_output(info)


def merge_info(target, src):
  for key, value in src['defines'].items():
    if key in target['defines']:
      raise Exception('duplicate define: %s' % key)
    target['defines'][key] = value

  for key, value in src['structs'].items():
    if key in target['structs']:
      raise Exception('duplicate struct: %s' % key)
    target['structs'][key] = value


def inspect_code(headers, cflags):
  if not DEBUG:
    info = inspect_headers(headers, cflags)
  else:
    info = {'defines': {}, 'structs': {}}
    for header in headers:
      merge_info(info, inspect_headers([header], cflags))
  return info


def parse_json(path):
  header_files = []

  with open(path, 'r') as stream:
    # Remove comments before loading the JSON.
    data = json.loads(re.sub(r'//.*\n', '', stream.read()))

  if not isinstance(data, list):
    data = [data]

  for item in data:
    for key in item.keys():
      if key not in ['file', 'defines', 'structs']:
        raise 'Unexpected key in json file: %s' % key

    header = {'name': item['file'], 'structs': {}, 'defines': {}}
    for name, data in item.get('structs', {}).items():
      if name in header['structs']:
        show('WARN: Description of struct "' + name + '" in file "' + item['file'] + '" replaces an existing description!')

      header['structs'][name] = data

    for part in item.get('defines', []):
      if not isinstance(part, list):
        # If no type is specified, assume integer.
        part = ['i', part]

      if part[1] in header['defines']:
        show('WARN: Description of define "' + part[1] + '" in file "' + item['file'] + '" replaces an existing description!')

      header['defines'][part[1]] = part[0]

    header_files.append(header)

  return header_files


def output_json(obj, stream):
  json.dump(obj, stream, indent=4, sort_keys=True)
  stream.write('\n')
  stream.close()


def main(args):
  global QUIET

  default_json_files = [
      utils.path_from_root('src/struct_info.json'),
      utils.path_from_root('src/struct_info_internal.json'),
      utils.path_from_root('src/struct_info_cxx.json'),
  ]
  parser = argparse.ArgumentParser(description='Generate JSON infos for structs.')
  parser.add_argument('json', nargs='*',
                      help='JSON file with a list of structs and their fields (defaults to src/struct_info.json)',
                      default=default_json_files)
  parser.add_argument('-q', dest='quiet', action='store_true', default=False,
                      help='Don\'t output anything besides error messages.')
  parser.add_argument('-o', dest='output', metavar='path', default=None,
                      help='Path to the JSON file that will be written. If omitted, the default location under `src` will be used.')
  parser.add_argument('-I', dest='includes', metavar='dir', action='append', default=[],
                      help='Add directory to include search path')
  parser.add_argument('-D', dest='defines', metavar='define', action='append', default=[],
                      help='Pass a define to the preprocessor')
  parser.add_argument('-U', dest='undefines', metavar='undefine', action='append', default=[],
                      help='Pass an undefine to the preprocessor')
  parser.add_argument('--wasm64', action='store_true',
                      help='use wasm64 architecture')
  args = parser.parse_args(args)

  QUIET = args.quiet

  # Avoid parsing problems due to gcc specifc syntax.
  cflags = ['-D_GNU_SOURCE']

  if args.wasm64:
    settings.MEMORY64 = 2

  # Add the user options to the list as well.
  for path in args.includes:
    cflags.append('-I' + path)

  for arg in args.defines:
    cflags.append('-D' + arg)

  for arg in args.undefines:
    cflags.append('-U' + arg)

  internal_cflags = [
    '-I' + utils.path_from_root('system/lib/libc/musl/src/internal'),
    '-I' + utils.path_from_root('system/lib/libc/musl/src/include'),
    '-I' + utils.path_from_root('system/lib/pthread/'),
  ]

  cxxflags = [
    '-I' + utils.path_from_root('system/lib/libcxxabi/src'),
    '-D__USING_EMSCRIPTEN_EXCEPTIONS__',
    '-I' + utils.path_from_root('system/lib/wasmfs/'),
    '-std=c++17',
  ]

  # Look for structs in all passed headers.
  info = {'defines': {}, 'structs': {}}

  for f in args.json:
    # This is a JSON file, parse it.
    header_files = parse_json(f)
    # Inspect all collected structs.
    if 'internal' in f:
      use_cflags = cflags + internal_cflags
    elif 'cxx' in f:
      use_cflags = cflags + cxxflags
    else:
      use_cflags = cflags
    info_fragment = inspect_code(header_files, use_cflags)
    merge_info(info, info_fragment)

  if args.output:
    output_file = args.output
  elif args.wasm64:
    output_file = utils.path_from_root('src/generated_struct_info64.json')
  else:
    output_file = utils.path_from_root('src/generated_struct_info32.json')

  with open(output_file, 'w') as f:
    output_json(info, f)

  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))

# SIG # Begin Windows Authenticode signature block
# MIIoQgYJKoZIhvcNAQcCoIIoMzCCKC8CAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCCluKfhgybLsW6Q
# 3TSyWAqJLikDS4CPKs45ecKAq7IeRaCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGg0wghoJAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEIBOYezfjbqu5G+CA+SeHnRA/3q5X12U0DpZYS3aa+JttMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAWaUntSrQMJBk/9nHGckpvm2tRXp1
# n0DegAyVyoJY8FjFYFAFUoH1MGCnbOcIe3B3k9Er84UhRvRRUgIt2jnDP2ofzrU/
# aoaMAVj/zedyny8+6sZ8feDer92CnmE+et6Khj8iujm2Bc1+f5gJF3N8DkmsDQkq
# RbiIPfnYe35T59qgGJkFumouBrQymk2FNQ9uno2bhB0fWqtjyxrd1BlgzvgYj6eE
# hKl7c6k/NM6Vbq2lZgwnZfdQyOA45K4TWvVkJIWcixylZ2lHVhiBQElS9ZXnZxsc
# j+n/JcbUT5Lhbn7rGaIxGDmnOCZX0aTO3v+MlG9DXescPWKvktQZHkAMTqGCF5cw
# gheTBgorBgEEAYI3AwMBMYIXgzCCF38GCSqGSIb3DQEHAqCCF3AwghdsAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCAOk/vGBxTwQg+vy8qWmFjJW9Af
# OseXrnwjRF5LTZrEBgIGaO//dzSDGBMyMDI1MTAxNjE2MTcyNC45ODJaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046QTAwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHtMIIHIDCCBQigAwIBAgITMwAAAgh4nVhd
# ksfZUgABAAACCDANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQyNTNaFw0yNjA0MjIxOTQyNTNaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# QTAwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC1y3AI5lIz3Ip1
# nK5BMUUbGRsjSnCz/VGs33zvY0NeshsPgfld3/Z3/3dS8WKBLlDlosmXJOZlFSiN
# XUd6DTJxA9ik/ZbCdWJ78LKjbN3tFkX2c6RRpRMpA8sq/oBbRryP3c8Q/gxpJAKH
# Hz8cuSn7ewfCLznNmxqliTk3Q5LHqz2PjeYKD/dbKMBT2TAAWAvum4z/HXIJ6tFd
# GoNV4WURZswCSt6ROwaqQ1oAYGvEndH+DXZq1+bHsgvcPNCdTSIpWobQiJS/UKLi
# R02KNCqB4I9yajFTSlnMIEMz/Ni538oGI64phcvNpUe2+qaKWHZ8d4T1KghvRmSS
# F4YF5DNEJbxaCUwsy7nULmsFnTaOjVOoTFWWfWXvBuOKkBcQKWGKvrki976j4x+5
# ezAP36fq3u6dHRJTLZAu4dEuOooU3+kMZr+RBYWjTHQCKV+yZ1ST0eGkbHXoA2ly
# yRDlNjBQcoeZIxWCZts/d3+nf1jiSLN6f6wdHaUz0ADwOTQ/aEo1IC85eFePvyIK
# axFJkGU2Mqa6Xzq3qCq5tokIHtjhogsrEgfDKTeFXTtdhl1IPtLcCfMcWOGGAXos
# VUU7G948F6W96424f2VHD8L3FoyAI9+r4zyIQUmqiESzuQWeWpTTjFYwCmgXaGOu
# SDV8cNOVQB6IPzPneZhVTjwxbAZlaQIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFKMx
# 4vfOqcUTgYOVB9f18/mhegFNMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQBRszKJ
# KwAfswqdaQPFiaYB/ZNAYWDa040XTcQsCaCua5nsG1IslYaSpH7miTLr6eQEqXcz
# ZoqeOa/xvDnMGifGNda0CHbQwtpnIhsutrKO2jhjEaGwlJgOMql21r7Ik6XnBza0
# e3hBOu4UBkMl/LEX+AURt7i7+RTNsGN0cXPwPSbTFE+9z7WagGbY9pwUo/NxkGJs
# eqGCQ/9K2VMU74bw5e7+8IGUhM2xspJPqnSeHPhYmcB0WclOxcVIfj/ZuQvworPb
# TEEYDVCzSN37c0yChPMY7FJ+HGFBNJxwd5lKIr7GYfq8a0gOiC2ljGYlc4rt4cCe
# d1XKg83f0l9aUVimWBYXtfNebhpfr6Lc3jD8NgsrDhzt0WgnIdnTZCi7jxjsIBil
# H99pY5/h6bQcLKK/E6KCP9E1YN78fLaOXkXMyO6xLrvQZ+uCSi1hdTufFC7oSB/C
# U5RbfIVHXG0j1o2n1tne4eCbNfKqUPTE31tNbWBR23Yiy0r3kQmHeYE1GLbL4pwk
# nqaip1BRn6WIUMJtgncawEN33f8AYGZ4a3NnHopzGVV6neffGVag4Tduy+oy1YF+
# shChoXdMqfhPWFpHe3uJGT4GJEiNs4+28a/wHUuF+aRaR0cN5P7XlOwU1360iUCJ
# tQdvKQaNAwGI29KOwS3QGriR9F2jOGPUAlpeEzCCB3EwggVZoAMCAQICEzMAAAAV
# xedrngKbSZkAAAAAABUwDQYJKoZIhvcNAQELBQAwgYgxCzAJBgNVBAYTAlVTMRMw
# EQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVN
# aWNyb3NvZnQgQ29ycG9yYXRpb24xMjAwBgNVBAMTKU1pY3Jvc29mdCBSb290IENl
# cnRpZmljYXRlIEF1dGhvcml0eSAyMDEwMB4XDTIxMDkzMDE4MjIyNVoXDTMwMDkz
# MDE4MzIyNVowfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAO
# BgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
# MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTAwggIiMA0GCSqG
# SIb3DQEBAQUAA4ICDwAwggIKAoICAQDk4aZM57RyIQt5osvXJHm9DtWC0/3unAcH
# 0qlsTnXIyjVX9gF/bErg4r25PhdgM/9cT8dm95VTcVrifkpa/rg2Z4VGIwy1jRPP
# dzLAEBjoYH1qUoNEt6aORmsHFPPFdvWGUNzBRMhxXFExN6AKOG6N7dcP2CZTfDlh
# AnrEqv1yaa8dq6z2Nr41JmTamDu6GnszrYBbfowQHJ1S/rboYiXcag/PXfT+jlPP
# 1uyFVk3v3byNpOORj7I5LFGc6XBpDco2LXCOMcg1KL3jtIckw+DJj361VI/c+gVV
# mG1oO5pGve2krnopN6zL64NF50ZuyjLVwIYwXE8s4mKyzbnijYjklqwBSru+cakX
# W2dg3viSkR4dPf0gz3N9QZpGdc3EXzTdEonW/aUgfX782Z5F37ZyL9t9X4C626p+
# Nuw2TPYrbqgSUei/BQOj0XOmTTd0lBw0gg/wEPK3Rxjtp+iZfD9M269ewvPV2HM9
# Q07BMzlMjgK8QmguEOqEUUbi0b1qGFphAXPKZ6Je1yh2AuIzGHLXpyDwwvoSCtdj
# bwzJNmSLW6CmgyFdXzB0kZSU2LlQ+QuJYfM2BjUYhEfb3BvR/bLUHMVr9lxSUV0S
# 2yW6r1AFemzFER1y7435UsSFF5PAPBXbGjfHCBUYP3irRbb1Hode2o+eFnJpxq57
# t7c+auIurQIDAQABo4IB3TCCAdkwEgYJKwYBBAGCNxUBBAUCAwEAATAjBgkrBgEE
# AYI3FQIEFgQUKqdS/mTEmr6CkTxGNSnPEP8vBO4wHQYDVR0OBBYEFJ+nFV0AXmJd
# g/Tl0mWnG1M1GelyMFwGA1UdIARVMFMwUQYMKwYBBAGCN0yDfQEBMEEwPwYIKwYB
# BQUHAgEWM2h0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9wa2lvcHMvRG9jcy9SZXBv
# c2l0b3J5Lmh0bTATBgNVHSUEDDAKBggrBgEFBQcDCDAZBgkrBgEEAYI3FAIEDB4K
# AFMAdQBiAEMAQTALBgNVHQ8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAfBgNVHSME
# GDAWgBTV9lbLj+iiXGJo0T2UkFvXzpoYxDBWBgNVHR8ETzBNMEugSaBHhkVodHRw
# Oi8vY3JsLm1pY3Jvc29mdC5jb20vcGtpL2NybC9wcm9kdWN0cy9NaWNSb29DZXJB
# dXRfMjAxMC0wNi0yMy5jcmwwWgYIKwYBBQUHAQEETjBMMEoGCCsGAQUFBzAChj5o
# dHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpL2NlcnRzL01pY1Jvb0NlckF1dF8y
# MDEwLTA2LTIzLmNydDANBgkqhkiG9w0BAQsFAAOCAgEAnVV9/Cqt4SwfZwExJFvh
# nnJL/Klv6lwUtj5OR2R4sQaTlz0xM7U518JxNj/aZGx80HU5bbsPMeTCj/ts0aGU
# GCLu6WZnOlNN3Zi6th542DYunKmCVgADsAW+iehp4LoJ7nvfam++Kctu2D9IdQHZ
# GN5tggz1bSNU5HhTdSRXud2f8449xvNo32X2pFaq95W2KFUn0CS9QKC/GbYSEhFd
# PSfgQJY4rPf5KYnDvBewVIVCs/wMnosZiefwC2qBwoEZQhlSdYo2wh3DYXMuLGt7
# bj8sCXgU6ZGyqVvfSaN0DLzskYDSPeZKPmY7T7uG+jIa2Zb0j/aRAfbOxnT99kxy
# bxCrdTDFNLB62FD+CljdQDzHVG2dY3RILLFORy3BFARxv2T5JL5zbcqOCb2zAVdJ
# VGTZc9d/HltEAY5aGZFrDZ+kKNxnGSgkujhLmm77IVRrakURR6nxt67I6IleT53S
# 0Ex2tVdUCbFpAUR+fKFhbHP+CrvsQWY9af3LwUFJfn6Tvsv4O+S3Fb+0zj6lMVGE
# vL8CwYKiexcdFYmNcP7ntdAoGokLjzbaukz5m/8K6TT4JDVnK+ANuOaMmdbhIurw
# J0I9JZTmdHRbatGePu1+oDEzfbzL6Xu/OHBE0ZDxyKs6ijoIYn/ZcGNTTY3ugm2l
# BRDBcQZqELQdVTNYs6FwZvKhggNQMIICOAIBATCB+aGB0aSBzjCByzELMAkGA1UE
# BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAc
# BgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjElMCMGA1UECxMcTWljcm9zb2Z0
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOkEw
# MDAtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQCNkvu0NKcSjdYKyrhJZcsyXOUTNKCBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JsmnzAiGA8yMDI1MTAxNjA4MDkwM1oYDzIwMjUxMDE3MDgwOTAzWjB3MD0GCisG
# AQQBhFkKBAExLzAtMAoCBQDsmyafAgEAMAoCAQACAgd+AgH/MAcCAQACAhU4MAoC
# BQDsnHgfAgEAMDYGCisGAQQBhFkKBAIxKDAmMAwGCisGAQQBhFkKAwKgCjAIAgEA
# AgMHoSChCjAIAgEAAgMBhqAwDQYJKoZIhvcNAQELBQADggEBAJ65qpTkelfeK287
# DZCvUuw18uJr1PzLW9DcHecCFUXJCM6X4FEfhxXl/Gs4QRM6RIswPXrXTYXRoIW7
# GpW+iqw3W2jOXaocyIL4zo9rR77cZmsxgkxcjq/DSRioHVuUPIu7od3GdTyQNWv3
# Ij+wpHbyr0h7aJKX/tVHiHoO2YCI72PiMgA8v0OIPEPd6YB4+w3/imS9zs9BlCUP
# cIZQZWS7kz7YWCg4X6dfgyKqd8KgmTzEUtZrV+1eRyDOZ9FXEtBJr55nlxrueQJD
# Jlze/mk7B/CB4ojRzx99tpMRdsuzBV4mltH9H36kAA4jfF23QihslcK+S86d8yop
# zu7RYVoxggQNMIIECQIBATCBkzB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2Fz
# aGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENv
# cnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAx
# MAITMwAAAgh4nVhdksfZUgABAAACCDANBglghkgBZQMEAgEFAKCCAUowGgYJKoZI
# hvcNAQkDMQ0GCyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCCF/4ys+D4fLero
# ZHUQE9IJWfiJjATTMblYOtvDXDVTgzCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQw
# gb0EII//jm8JHa2W1O9778t9+Ft2Z5NmKqttPk6Q+9RRpmepMIGYMIGApH4wfDEL
# MAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1v
# bmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWlj
# cm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIIeJ1YXZLH2VIAAQAAAggw
# IgQgP41uIJhe7BjHXQev0+FamgB2jMT5D8EXD9xUeSB1R0EwDQYJKoZIhvcNAQEL
# BQAEggIATTFDPCY4SpGIspZtTVqN04vJLq0u0nuM2jlkWXh7smKKv66Vskbgl4ZH
# V1/KKRNvr2Ols4k3WUyahTcDWTwboLZjBwTEe8Bvu9Alse0WEnW6b0/0NFqxjL3Q
# OG723oKXgtN3ikW7P42+79DFN4fDrH0aLin8liFTtEu784DcaPdmUuoKMh7e1amH
# dy/GrL0ualNTlvt2RmSMvtDFdkX1oyl3dc/ZAv5ADLK+f7tkqRLU8/UnkPlD7Nv0
# Ptrh3SQa0Ns4klakh3qGIFCfBvIm23kOgTmiDnzn+UKRaIic6bM0or1B2GUr5krV
# hIQAtmpWnBrqYf7qFyuiUcOoyGlnd6oj5l8nakptGpUZ8olDSSVGGUkCaT/Gg+Ro
# MkJfO9IKnkwFoVNFoNiFLsTT7zvE223nCPA678xIwefevKB3untG3eGk+0dlOLF3
# Mc0O3p2fk/N467YEQ1U9J2Kyb+BwxjnDsi6d50YD2LQ+Cg/o5GEqP3wyTQOXV3vy
# BlxsrsJvJnvgCOpy3qPRRGfJVpukffpg21V9P5TGWD4T1hgyXTP0if0KEDJJ8r3v
# qhp/Q4jhQ8IQtLtLvLzrQUyZogi/vlefNgz7y3hJdp5wOEZB+s7cuGYkWgFZAF3/
# iEhr9IKLKvy055PafAN+ORfoscidVoK+b4aiY5FDQ0qMqy1ttgs=
# SIG # End Windows Authenticode signature block