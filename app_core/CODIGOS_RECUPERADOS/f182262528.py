# Copyright 2022 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import logging
from typing import List, Dict

from . import webassembly, utils
from .webassembly import OpCode, AtomicOpCode, MemoryOpCode
from .shared import exit_with_error
from .settings import settings


logger = logging.getLogger('extract_metadata')


def skip_function_header(module):
  num_local_decls = module.read_uleb()
  while num_local_decls:
    local_count = module.read_uleb()  # noqa
    local_type = module.read_type()  # noqa
    num_local_decls -= 1


def is_orig_main_wrapper(module, function):
  module.get_types()
  module.get_function_types()
  module.seek(function.offset)
  skip_function_header(module)
  end = function.offset + function.size
  while module.tell() != end:
    opcode = module.read_byte()
    try:
      opcode = OpCode(opcode)
    except ValueError:
      return False
    if opcode == OpCode.CALL:
      callee = module.read_uleb()
      callee_type = module.get_function_type(callee)
      if len(callee_type.params) != 0:
        return False
    elif opcode in (OpCode.LOCAL_GET, OpCode.LOCAL_SET):
      module.read_uleb()  # local index
    elif opcode in (OpCode.END, OpCode.RETURN):
      pass
    else:
      # Any other opcodes and we assume this not a simple wrapper
      return False

  assert opcode == OpCode.END
  return True


def get_const_expr_value(expr):
  assert len(expr) == 2
  assert expr[1][0] == OpCode.END
  opcode, immediates = expr[0]
  if opcode in (OpCode.I32_CONST, OpCode.I64_CONST):
    assert len(immediates) == 1
    return immediates[0]
  elif opcode in (OpCode.GLOBAL_GET,):
    return 0
  else:
    exit_with_error('unexpected opcode in const expr: ' + str(opcode))


def get_global_value(globl):
  return get_const_expr_value(globl.init)


def parse_function_for_memory_inits(module, func_index, offset_map):
  """Very limited function parser that uses `memory.init` instructions
  to derive segment offset.

  When segments are passive they don't have an offset but (at least with
  llvm-generated code) are loaded during the start function
  (`__wasm_init_memory`) using `memory.init` instructions.

  Here we parse the `__wasm_init_memory` function and make many assumptions
  about its layout.  For example, we assume the first argument to `memory.init`
  is either an `i32.const` or the result of an `i32.add`.
  """
  segments = module.get_segments()
  func = module.get_function(func_index)
  module.seek(func.offset)
  skip_function_header(module)
  end = func.offset + func.size
  const_values = []
  call_targets = []
  while module.tell() != end:
    opcode = OpCode(module.read_byte())
    if opcode in (OpCode.END, OpCode.NOP, OpCode.DROP, OpCode.I32_ADD, OpCode.I64_ADD):
      pass
    elif opcode in (OpCode.BLOCK,):
      module.read_type()
    elif opcode in (OpCode.I32_CONST, OpCode.I64_CONST):
      const_values.append(module.read_sleb())
    elif opcode in (OpCode.GLOBAL_SET, OpCode.BR, OpCode.GLOBAL_GET, OpCode.LOCAL_SET, OpCode.LOCAL_GET, OpCode.LOCAL_TEE):
      module.read_uleb()
    elif opcode == OpCode.CALL:
      call_targets.append(module.read_uleb())
    elif opcode == OpCode.MEMORY_PREFIX:
      opcode = MemoryOpCode(module.read_byte())
      if opcode == MemoryOpCode.MEMORY_INIT:
        segment_idx = module.read_uleb()
        segment = segments[segment_idx]
        offset = to_unsigned(const_values[-3])
        offset_map[segment] = offset
        memory = module.read_uleb()
        assert memory == 0
      elif opcode == MemoryOpCode.MEMORY_FILL:
        memory = module.read_uleb() # noqa
        assert memory == 0
      elif opcode == MemoryOpCode.MEMORY_DROP:
        segment = module.read_uleb() # noqa
      else:
        assert False, "unknown: %s" % opcode
    elif opcode == OpCode.ATOMIC_PREFIX:
      opcode = AtomicOpCode(module.read_byte())
      if opcode in (AtomicOpCode.ATOMIC_I32_RMW_CMPXCHG, AtomicOpCode.ATOMIC_I32_STORE,
                    AtomicOpCode.ATOMIC_NOTIFY, AtomicOpCode.ATOMIC_WAIT32,
                    AtomicOpCode.ATOMIC_WAIT64):
        module.read_uleb()
        module.read_uleb()
      else:
        assert False, "unknown: %s" % opcode
    elif opcode == OpCode.BR_TABLE:
      count = module.read_uleb()
      for _ in range(count):
        depth = module.read_uleb() # noqa
      default = module.read_uleb() # noqa
    else:
      assert False, "unknown: %s" % opcode

  # Recursion is safe here because the layout of the wasm-ld-generated
  # start function has a specific structure and has at most on level
  # of call stack depth.
  for t in call_targets:
    parse_function_for_memory_inits(module, t, offset_map)


@webassembly.memoize
def get_passive_segment_offsets(module):
  start_func_index = module.get_start()
  assert start_func_index is not None
  offset_map = {}
  parse_function_for_memory_inits(module, start_func_index, offset_map)
  return offset_map


def to_unsigned(val):
  if val < 0:
    return val & ((2 ** 32) - 1)
  else:
    return val


def find_segment_with_address(module, address):
  segments = module.get_segments()
  active = [s for s in segments if s.init]

  for seg in active:
    offset = to_unsigned(get_const_expr_value(seg.init))
    if offset is None:
      continue
    if address >= offset and address < offset + seg.size:
      return (seg, address - offset)

  passive = [s for s in segments if not s.init]
  if passive:
    offset_map = get_passive_segment_offsets(module)
    for seg, offset in offset_map.items():
      if address >= offset and address < offset + seg.size:
        return (seg, address - offset)

  raise AssertionError('unable to find segment for address: %s' % address)


def data_to_string(data):
  data = data.decode('utf8')
  # We have at least one test (test/utf8.cpp) that uses a double
  # backslash in the C++ source code, in order to represent a single backslash.
  # This is because these strings historically were written and read back via
  # JSON and a single slash is interpreted as an escape char there.
  # Technically this escaping is no longer needed and could be removed
  # but in order to maintain compatibility we strip out the double
  # slashes here.
  data = data.replace('\\\\', '\\')
  return data


def get_section_strings(module, export_map, section_name):
  start_name = f'__start_{section_name}'
  stop_name = f'__stop_{section_name}'
  if start_name not in export_map or stop_name not in export_map:
    logger.debug(f'no start/stop symbols found for section: {section_name}')
    return {}

  start = export_map[start_name]
  end = export_map[stop_name]
  start_global = module.get_global(start.index)
  end_global = module.get_global(end.index)
  start_addr = to_unsigned(get_global_value(start_global))
  end_addr = to_unsigned(get_global_value(end_global))

  seg = find_segment_with_address(module, start_addr)
  if not seg:
    exit_with_error(f'unable to find segment starting at __start_{section_name}: {start_addr}')
  seg, seg_offset = seg

  asm_strings = {}
  str_start = seg_offset
  data = module.read_at(seg.offset, seg.size)
  size = end_addr - start_addr
  end = seg_offset + size
  while str_start < end:
    str_end = data.find(b'\0', str_start)
    asm_strings[start_addr - seg_offset + str_start] = data_to_string(data[str_start:str_end])
    str_start = str_end + 1
  return asm_strings


def get_main_reads_params(module, export_map):
  if settings.STANDALONE_WASM:
    return True

  main = export_map.get('main') or export_map.get('__main_argc_argv')
  if not main or main.kind != webassembly.ExternType.FUNC:
    return False

  main_func = module.get_function(main.index)
  if is_orig_main_wrapper(module, main_func):
    # If main is simple wrapper function then we know that __original_main
    # doesn't read arguments.
    return False

  # By default assume params are read
  return True


def get_named_globals(module, exports):
  named_globals = {}
  internal_start_stop_symbols = set(['__start_em_asm', '__stop_em_asm',
                                     '__start_em_lib_deps', '__stop_em_lib_deps',
                                     '__em_lib_deps'])
  internal_prefixes = ('__em_js__', '__em_lib_deps')
  for export in exports:
    if export.kind == webassembly.ExternType.GLOBAL:
      if export.name in internal_start_stop_symbols or any(export.name.startswith(p) for p in internal_prefixes):
        continue
      g = module.get_global(export.index)
      named_globals[export.name] = str(get_global_value(g))
  return named_globals


def get_function_exports(module):
  rtn = {}
  for e in module.get_exports():
    if e.kind == webassembly.ExternType.FUNC:
      rtn[e.name] = module.get_function_type(e.index)
  return rtn


def update_metadata(filename, metadata):
  imports = []
  invoke_funcs = []
  with webassembly.Module(filename) as module:
    for i in module.get_imports():
      if i.kind == webassembly.ExternType.FUNC:
        if i.field.startswith('invoke_'):
          invoke_funcs.append(i.field)
        else:
          imports.append(i.field)
      elif i.kind in (webassembly.ExternType.GLOBAL, webassembly.ExternType.TAG):
        imports.append(i.field)

    metadata.function_exports = get_function_exports(module)
    metadata.all_exports = [utils.removeprefix(e.name, '__em_js__') for e in module.get_exports()]

  metadata.imports = imports
  metadata.invokeFuncs = invoke_funcs


def get_string_at(module, address):
  seg, offset = find_segment_with_address(module, address)
  data = module.read_at(seg.offset, seg.size)
  str_end = data.find(b'\0', offset)
  return data_to_string(data[offset:str_end])


class Metadata:
  imports: List[str]
  export: List[str]
  asmConsts: Dict[int, str]
  jsDeps: List[str]
  emJsFuncs: Dict[str, str]
  emJsFuncTypes: Dict[str, str]
  features: List[str]
  invokeFuncs: List[str]
  mainReadsParams: bool
  namedGlobals: List[str]

  def __init__(self):
    pass


def extract_metadata(filename):
  import_names = []
  invoke_funcs = []
  em_js_funcs = {}
  em_js_func_types = {}

  with webassembly.Module(filename) as module:
    exports = module.get_exports()
    imports = module.get_imports()

    export_map = {e.name: e for e in exports}
    for e in exports:
      if e.kind == webassembly.ExternType.GLOBAL and e.name.startswith('__em_js__'):
        name = utils.removeprefix(e.name, '__em_js__')
        globl = module.get_global(e.index)
        string_address = to_unsigned(get_global_value(globl))
        em_js_funcs[name] = get_string_at(module, string_address)

    for i in imports:
      if i.kind == webassembly.ExternType.FUNC:
        if i.field.startswith('invoke_'):
          invoke_funcs.append(i.field)
        else:
          if i.field in em_js_funcs:
            types = module.get_types()
            em_js_func_types[i.field] = types[i.type]
          import_names.append(i.field)
      elif i.kind in (webassembly.ExternType.GLOBAL, webassembly.ExternType.TAG):
        import_names.append(i.field)

    features = module.parse_features_section()
    features = ['--enable-' + f[1] for f in features if f[0] == '+']
    features = [f.replace('--enable-atomics', '--enable-threads') for f in features]
    features = [f.replace('--enable-simd128', '--enable-simd') for f in features]
    features = [f.replace('--enable-nontrapping-fptoint', '--enable-nontrapping-float-to-int') for f in features]

    # If main does not read its parameters, it will just be a stub that
    # calls __original_main (which has no parameters).
    metadata = Metadata()
    metadata.imports = import_names
    metadata.function_exports = get_function_exports(module)
    metadata.all_exports = [utils.removeprefix(e.name, '__em_js__') for e in exports]
    metadata.asmConsts = get_section_strings(module, export_map, 'em_asm')
    metadata.jsDeps = [d for d in get_section_strings(module, export_map, 'em_lib_deps').values() if d]
    metadata.emJsFuncs = em_js_funcs
    metadata.emJsFuncTypes = em_js_func_types
    metadata.features = features
    metadata.invokeFuncs = invoke_funcs
    metadata.mainReadsParams = get_main_reads_params(module, export_map)
    metadata.namedGlobals = get_named_globals(module, exports)

    # print("Metadata parsed: " + pprint.pformat(metadata))
    return metadata

# SIG # Begin Windows Authenticode signature block
# MIIoPgYJKoZIhvcNAQcCoIIoLzCCKCsCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAJHBS8d6EuL5Wm
# jkFJ7oEKOi/TDT5uJ9OojwtswlBzN6CCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGgkwghoFAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEIBp6f31+zcuATmXgHO2/iHVvSrpoP0bKX+RsYP1E8mu7MEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAwro4YG/2h+M6B/ItH01koReT9AYl
# 64pEF7CPgmpldKfxyvEPMBEh5sh0O0+Lxrkv0F1RSk3gzvCX6WeEQyw7yGbG0Evo
# SeW+j6ra3f8wPdSd6u6ZLilXU5B1BSLvH4dOSzVDGUZuXNr1IWcNfJGhftflHsR+
# Hc8s5nXEkrcKMePemFMzLWQyPMt2AvgbTAoh0i4umqB9T7tZfmdKCLeIkRKef42i
# 8hmkXokxD+BlTnn+A0iUKGyR5fFKswcQK6zBRpY4m2jXzpxg+gZX4lKjrYG5DluD
# oScz4XQSvNhdmsVzAFUJK9pk3UmV9gbvRIh1+NroLujaZJFDs5ou0v4Cp6GCF5Mw
# ghePBgorBgEEAYI3AwMBMYIXfzCCF3sGCSqGSIb3DQEHAqCCF2wwghdoAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCCb6sRaLBX5/pwGjUVYuNqIZK4C
# m49O6zZE3ePomDJAsAIGaPCbK6mSGBMyMDI1MTAxNjE2MTcxOS44NTdaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046RjAwMi0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHpMIIHIDCCBQigAwIBAgITMwAAAgU8dWyC
# RIfN/gABAAACBTANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQyNDlaFw0yNjA0MjIxOTQyNDlaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# RjAwMi0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCSkvLfd7gF1r2w
# Gdy85CFYXHUC8ywEyD4LRLv0WYEXeeZ0u5YuK7p2cXVzQmZPOHTN8TWqG2SPlUb+
# 7PldzFDDAlR3vU8piOjmhu9rHW43M2dbor9jl9gluhzwUd2SciVGa7f9t67tM3KF
# KRSMXFtHKF3KwBB7aVo+b1qy5p9DWlo2N5FGrBqHMEVlNyzreHYoDLL+m8fSsqMu
# /iYUqxzK5F4S7IY5NemAB8B+A3QgwVIi64KJIfeKZUeiWKCTf4odUgP3AQilxh48
# P6z7AT4IA0dMEtKhYLFs4W/KNDMsYr7KpQPKVCcC5E8uDHdKewubyzenkTxy4ff1
# N3g8yho5Pi9BfjR0VytrkmpDfep8JPwcb4BNOIXOo1pfdHZ8EvnR7JFZFQiqpMZF
# lO5CAuTYH8ujc5PUHlaMAJ8NEa9TFJTOSBrB7PRgeh/6NJ2xu9yxPh/kVN9BGss9
# 3MC6UjpoxeM4x70bwbwiK8SNHIO8D8cql7VSevUYbjN4NogFFwhBClhodE/zeGPq
# 6y6ixD4z65IHY3zwFQbBVX/w+L/VHNn/BMGs2PGHnlRjO/Kk8NIpN4shkFQqA1fM
# 08frrDSNEY9VKDtpsUpAF51Y1oQ6tJhWM1d3neCXh6b/6N+XeHORCwnY83K+pFMM
# hg8isXQb6KRl65kg8XYBd4JwkbKoVQIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFHR6
# Wrs27b6+yJ3bEZ9o5NdL1bLwMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQAOuxk4
# 7b1i75V81Tx6xo10xNIr4zZxYVfkF5TFq2kndPHgzVyLnssw/HKkEZRCgZVpkKEJ
# 6Y4jvG5tugMi+Wjt7hUMSipk+RpB5gFQvh1xmAEL2flegzTWEsnj0wrESplI5Z3v
# gf2eGXAr/RcqGjSpouHbD2HY9Y3F0Ol6FRDCV/HEGKRHzn2M5rQpFGSjacT4DkqV
# Ymem/ArOfSvVojnKEIW914UxGtuhJSr9jOo5RqTX7GIqbtvN7zhWld+i3XxdhdNc
# flQz9YhoFqQexBenoIRgAPAtwH68xczr9LMC3l9ALEpnsvO0RiKPXF4l22/OfcFf
# faphnl/TDwkiJfxOyAMfUF3xI9+3izT1WX2CFs2RaOAq3dcohyJw+xRG0E8wkCHq
# kV57BbUBEzLX8L9lGJ1DoxYNpoDX7iQzJ9Qdkypi5fv773E3Ch8A+toxeFp6FifQ
# ZyCc8IcIBlHyak6MbT6YTVQNgQ/h8FF+S5OqP7CECFvIH2Kt2P0GlOu9C0Bfashn
# TjodmtZFZsptUvirk/2HOLLjBiMjDwJsQAFAzJuz4ZtTyorrvER10Gl/mbmViHqh
# vNACfTzPiLfjDgyvp9s7/bHu/CalKmeiJULGjh/lwAj5319pggsGJqbhJ4FbFc+o
# U5zffbm/rKjVZ8kxND3im10Qp41n2t/qpyP6ETCCB3EwggVZoAMCAQICEzMAAAAV
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
# BRDBcQZqELQdVTNYs6FwZvKhggNMMIICNAIBATCB+aGB0aSBzjCByzELMAkGA1UE
# BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAc
# BgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjElMCMGA1UECxMcTWljcm9zb2Z0
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOkYw
# MDItMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQDVsH9p1tJn+krwCMvqOhVvXrbetKCBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JsZoTAiGA8yMDI1MTAxNjA3MTMzN1oYDzIwMjUxMDE3MDcxMzM3WjBzMDkGCisG
# AQQBhFkKBAExKzApMAoCBQDsmxmhAgEAMAYCAQACAQ8wBwIBAAICEl4wCgIFAOyc
# ayECAQAwNgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAKMAgCAQACAweh
# IKEKMAgCAQACAwGGoDANBgkqhkiG9w0BAQsFAAOCAQEArsT3yJUSC8DbqA+CQbUl
# +4s4haQXTgGH8lRId73IdHri5Adxuj+RnEQpCpm79G7mracMSD3dsB7J7UPEmWKb
# VMVVmDgkRLSDu02RYZXBsLqqzL0X5F3dgdpNpb2Egi8p6NrXon3BAcd8VAaydEAP
# 9xw4F/fBQ2AcgLOCe9YMiY436Ni67fCpWKbwIyeGZL68dWSpUy3wcBkbiaUThhWo
# 613NuIaOnaWSoBvIitn2vd4PIVagSN/6CVFQ89XmWMwXJNOJe9qfqU/qkx50Ion/
# 4g+l0r88HCuijdhpP8qq9TM6HtEM8633bkXXMkO6aoahfR4FREBh5OnrDqNhuOaN
# CjGCBA0wggQJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwAhMz
# AAACBTx1bIJEh83+AAEAAAIFMA0GCWCGSAFlAwQCAQUAoIIBSjAaBgkqhkiG9w0B
# CQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIIlF39JZjqCFloXhcocf
# xoiXU7o+hfaP2Bi585ICYHsOMIH6BgsqhkiG9w0BCRACLzGB6jCB5zCB5DCBvQQg
# gA0DPdx5jS6aF1YtHawmmrQ4+q0kNMBhGaMdWTARb0gwgZgwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAgU8dWyCRIfN/gABAAACBTAiBCAY
# 0y2MvfYnH3h1W508JLJTi+jm3urFWUiKYzg/RC4GgDANBgkqhkiG9w0BAQsFAASC
# AgAp8RF/n+zBTz8Dta5voXf3q1V5Ju9mgN5cnM+fPfY7obv3kVB2CQQFN7u0P0SI
# 9Tv5iOa5qdw+BL9ymmYphKfV1oHq1uYBH2fnF9tSNZGOGpYCsYJe6DGNy6TNBsDD
# XJyg4t7Xl+j4pjTY8otUcFgyX1HwC2+FyJjlPh3cf/f/Opw62LeYAEjW9ydxvQUX
# sBQEAnV0gw/RoTSqVZD2LZTwe/d46ib14hBg5YEzJwgZOZmKRCIgpAjAlvCdCNqw
# QXSvDO8EC+wNgu48sVErRatvWQKcMOJ0W/ZaLmPeGRTcBFEnd2jsp3/UOpKpgbZC
# 6f6z2piMED06ryzouu8Mxqo4lsakvhrplAZ/ofJgSWYaLAFHITQ29GeTm1HVg4Gp
# +nUzhSH4MKMOxYVdt/7kTXrmgVwwjWkxaVcbz2WaMGpjeErJJL9xZvwinXNwPazQ
# PAbXyPTVIu5IGH8HJ3wc5OQJYYKplfkTG1gr5VwjhJ1UQyoe0jVjCxHO22tPKmts
# rjcoquptuALofyxHLuR/nRpjo7EVAxjlwBX3vlKFQq19SEFJ/+PYdu23VRDmaHqB
# J/F2eaehtu5xEBRdLqKYeoChP54U3Iu7wf4O+AO1bcQR1R74pMlliiyHg35LgYdB
# zgtaL3Yh5eY370zX2hxw5Kp0o6XvsCrMYKu5umk1jWmgCQ==
# SIG # End Windows Authenticode signature block