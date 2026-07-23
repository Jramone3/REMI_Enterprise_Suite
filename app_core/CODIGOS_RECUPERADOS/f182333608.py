# Copyright 2011 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""Utilties for manipulating WebAssembly binaries from python.
"""

from collections import namedtuple
from enum import IntEnum
from functools import wraps
import logging
import os
import sys

from . import utils

sys.path.append(utils.path_from_root('third_party'))

import leb128

logger = logging.getLogger('webassembly')

WASM_PAGE_SIZE = 65536

MAGIC = b'\0asm'

VERSION = b'\x01\0\0\0'

HEADER_SIZE = 8

LIMITS_HAS_MAX = 0x1

SEG_PASSIVE = 0x1

PREFIX_MATH = 0xfc
PREFIX_THREADS = 0xfe
PREFIX_SIMD = 0xfd

SYMBOL_BINDING_MASK = 0x3
SYMBOL_BINDING_GLOBAL = 0x0
SYMBOL_BINDING_WEAK = 0x1
SYMBOL_BINDING_LOCAL = 0x2


def to_leb(num):
  return leb128.u.encode(num)


def read_uleb(iobuf):
  return leb128.u.decode_reader(iobuf)[0]


def read_sleb(iobuf):
  return leb128.i.decode_reader(iobuf)[0]


def memoize(method):

  @wraps(method)
  def wrapper(self, *args, **kwargs):
    assert not kwargs
    key = (method.__name__, args)
    if key not in self._cache:
      self._cache[key] = method(self, *args, **kwargs)
    return self._cache[key]

  return wrapper


def once(method):

  @wraps(method)
  def helper(self, *args, **kwargs):
    key = method
    if key not in self._cache:
      self._cache[key] = method(self, *args, **kwargs)

  return helper


class Type(IntEnum):
  I32 = 0x7f # -0x1
  I64 = 0x7e # -0x2
  F32 = 0x7d # -0x3
  F64 = 0x7c # -0x4
  V128 = 0x7b # -0x5
  FUNCREF = 0x70 # -0x10
  EXTERNREF = 0x6f # -0x11
  VOID = 0x40 # -0x40


class OpCode(IntEnum):
  NOP = 0x01
  BLOCK = 0x02
  END = 0x0b
  BR = 0x0c
  BR_TABLE = 0x0e
  CALL = 0x10
  DROP = 0x1a
  LOCAL_GET = 0x20
  LOCAL_SET = 0x21
  LOCAL_TEE = 0x22
  GLOBAL_GET = 0x23
  GLOBAL_SET = 0x24
  RETURN = 0x0f
  I32_CONST = 0x41
  I64_CONST = 0x42
  F32_CONST = 0x43
  F64_CONST = 0x44
  I32_ADD = 0x6a
  I64_ADD = 0x7c
  REF_NULL = 0xd0
  ATOMIC_PREFIX = 0xfe
  MEMORY_PREFIX = 0xfc


class MemoryOpCode(IntEnum):
  MEMORY_INIT = 0x08
  MEMORY_DROP = 0x09
  MEMORY_COPY = 0x0a
  MEMORY_FILL = 0x0b


class AtomicOpCode(IntEnum):
  ATOMIC_NOTIFY = 0x00
  ATOMIC_WAIT32 = 0x01
  ATOMIC_WAIT64 = 0x02
  ATOMIC_I32_STORE = 0x17
  ATOMIC_I32_RMW_CMPXCHG = 0x48


class SecType(IntEnum):
  CUSTOM = 0
  TYPE = 1
  IMPORT = 2
  FUNCTION = 3
  TABLE = 4
  MEMORY = 5
  TAG = 13
  GLOBAL = 6
  EXPORT = 7
  START = 8
  ELEM = 9
  DATACOUNT = 12
  CODE = 10
  DATA = 11


class ExternType(IntEnum):
  FUNC = 0
  TABLE = 1
  MEMORY = 2
  GLOBAL = 3
  TAG = 4


class DylinkType(IntEnum):
  MEM_INFO = 1
  NEEDED = 2
  EXPORT_INFO = 3
  IMPORT_INFO = 4


class InvalidWasmError(BaseException):
  pass


Section = namedtuple('Section', ['type', 'size', 'offset', 'name'])
Limits = namedtuple('Limits', ['flags', 'initial', 'maximum'])
Import = namedtuple('Import', ['kind', 'module', 'field', 'type'])
Export = namedtuple('Export', ['name', 'kind', 'index'])
Global = namedtuple('Global', ['type', 'mutable', 'init'])
Dylink = namedtuple('Dylink', ['mem_size', 'mem_align', 'table_size', 'table_align', 'needed', 'export_info', 'import_info'])
Table = namedtuple('Table', ['elem_type', 'limits'])
FunctionBody = namedtuple('FunctionBody', ['offset', 'size'])
DataSegment = namedtuple('DataSegment', ['flags', 'init', 'offset', 'size'])
FuncType = namedtuple('FuncType', ['params', 'returns'])


class Module:
  """Extremely minimal wasm module reader.  Currently only used
  for parsing the dylink section."""
  def __init__(self, filename):
    self.buf = None # Set this before FS calls below in case they throw.
    self.filename = filename
    self.size = os.path.getsize(filename)
    self.buf = open(filename, 'rb')
    magic = self.buf.read(4)
    version = self.buf.read(4)
    if magic != MAGIC or version != VERSION:
      raise InvalidWasmError(f'{filename} is not a valid wasm file')
    self._cache = {}

  def __del__(self):
    assert not self.buf, '`__exit__` should have already been called, please use context manager'

  def __enter__(self):
    return self

  def __exit__(self, _exc_type, _exc_val, _exc_tb):
    if self.buf:
      self.buf.close()
      self.buf = None

  def read_at(self, offset, count):
    self.buf.seek(offset)
    return self.buf.read(count)

  def read_byte(self):
    return self.buf.read(1)[0]

  def read_uleb(self):
    return read_uleb(self.buf)

  def read_sleb(self):
    return read_sleb(self.buf)

  def read_string(self):
    size = self.read_uleb()
    return self.buf.read(size).decode('utf-8')

  def read_limits(self):
    flags = self.read_byte()
    initial = self.read_uleb()
    maximum = 0
    if flags & LIMITS_HAS_MAX:
      maximum = self.read_uleb()
    return Limits(flags, initial, maximum)

  def read_type(self):
    return Type(self.read_uleb())

  def read_init(self):
    code = []
    while 1:
      opcode = OpCode(self.read_byte())
      args = []
      if opcode == OpCode.GLOBAL_GET:
        args.append(self.read_uleb())
      elif opcode in (OpCode.I32_CONST, OpCode.I64_CONST):
        args.append(self.read_sleb())
      elif opcode in (OpCode.REF_NULL,):
        args.append(self.read_type())
      elif opcode in (OpCode.END, OpCode.I32_ADD, OpCode.I64_ADD):
        pass
      else:
        raise Exception('unexpected opcode %s' % opcode)
      code.append((opcode, args))
      if opcode == OpCode.END:
        break
    return code

  def seek(self, offset):
    return self.buf.seek(offset)

  def tell(self):
    return self.buf.tell()

  def skip(self, count):
    self.buf.seek(count, os.SEEK_CUR)

  def sections(self):
    """Generator that lazily returns sections from the wasm file."""
    offset = HEADER_SIZE
    while offset < self.size:
      self.seek(offset)
      section_type = SecType(self.read_byte())
      section_size = self.read_uleb()
      section_offset = self.buf.tell()
      name = None
      if section_type == SecType.CUSTOM:
        name = self.read_string()

      yield Section(section_type, section_size, section_offset, name)
      offset = section_offset + section_size

  @memoize
  def get_types(self):
    type_section = self.get_section(SecType.TYPE)
    if not type_section:
      return []
    self.seek(type_section.offset)
    num_types = self.read_uleb()
    types = []
    for _ in range(num_types):
      type_form = self.read_byte()
      assert type_form == 0x60

      params = []
      num_params = self.read_uleb()
      for _ in range(num_params):
        params.append(self.read_type())

      returns = []
      num_returns = self.read_uleb()
      for _ in range(num_returns):
        returns.append(self.read_type())

      types.append(FuncType(params, returns))

    return types

  def parse_features_section(self):
    features = []
    sec = self.get_custom_section('target_features')
    if sec:
      self.seek(sec.offset)
      self.read_string()  # name
      feature_count = self.read_uleb()
      while feature_count:
        prefix = self.read_byte()
        features.append((chr(prefix), self.read_string()))
        feature_count -= 1
    return features

  @memoize
  def parse_dylink_section(self):
    dylink_section = next(self.sections())
    assert dylink_section.type == SecType.CUSTOM
    self.seek(dylink_section.offset)
    # section name
    needed = []
    export_info = {}
    import_info = {}
    self.read_string()  # name

    if dylink_section.name == 'dylink':
      mem_size = self.read_uleb()
      mem_align = self.read_uleb()
      table_size = self.read_uleb()
      table_align = self.read_uleb()

      needed_count = self.read_uleb()
      while needed_count:
        libname = self.read_string()
        needed.append(libname)
        needed_count -= 1
    elif dylink_section.name == 'dylink.0':
      section_end = dylink_section.offset + dylink_section.size
      while self.tell() < section_end:
        subsection_type = self.read_uleb()
        subsection_size = self.read_uleb()
        end = self.tell() + subsection_size
        if subsection_type == DylinkType.MEM_INFO:
          mem_size = self.read_uleb()
          mem_align = self.read_uleb()
          table_size = self.read_uleb()
          table_align = self.read_uleb()
        elif subsection_type == DylinkType.NEEDED:
          needed_count = self.read_uleb()
          while needed_count:
            libname = self.read_string()
            needed.append(libname)
            needed_count -= 1
        elif subsection_type == DylinkType.EXPORT_INFO:
          count = self.read_uleb()
          while count:
            sym = self.read_string()
            flags = self.read_uleb()
            export_info[sym] = flags
            count -= 1
        elif subsection_type == DylinkType.IMPORT_INFO:
          count = self.read_uleb()
          while count:
            module = self.read_string()
            field = self.read_string()
            flags = self.read_uleb()
            import_info.setdefault(module, {})
            import_info[module][field] = flags
            count -= 1
        else:
          print(f'unknown subsection: {subsection_type}')
          # ignore unknown subsections
          self.skip(subsection_size)
        assert self.tell() == end
    else:
      utils.exit_with_error('error parsing shared library')

    return Dylink(mem_size, mem_align, table_size, table_align, needed, export_info, import_info)

  @memoize
  def get_exports(self):
    export_section = self.get_section(SecType.EXPORT)
    if not export_section:
      return []

    self.seek(export_section.offset)
    num_exports = self.read_uleb()
    exports = []
    for _ in range(num_exports):
      name = self.read_string()
      kind = ExternType(self.read_byte())
      index = self.read_uleb()
      exports.append(Export(name, kind, index))

    return exports

  @memoize
  def get_imports(self):
    import_section = self.get_section(SecType.IMPORT)
    if not import_section:
      return []

    self.seek(import_section.offset)
    num_imports = self.read_uleb()
    imports = []
    for _ in range(num_imports):
      mod = self.read_string()
      field = self.read_string()
      kind = ExternType(self.read_byte())
      type_ = None
      if kind == ExternType.FUNC:
        type_ = self.read_uleb()
      elif kind == ExternType.GLOBAL:
        type_ = self.read_sleb()
        self.read_byte()  # mutable
      elif kind == ExternType.MEMORY:
        self.read_limits()  # limits
      elif kind == ExternType.TABLE:
        type_ = self.read_sleb()
        self.read_limits()  # limits
      elif kind == ExternType.TAG:
        self.read_byte()  # attribute
        type_ = self.read_uleb()
      else:
        raise AssertionError()
      imports.append(Import(kind, mod, field, type_))

    return imports

  @memoize
  def get_globals(self):
    global_section = self.get_section(SecType.GLOBAL)
    if not global_section:
      return []
    globls = []
    self.seek(global_section.offset)
    num_globals = self.read_uleb()
    for _ in range(num_globals):
      global_type = self.read_type()
      mutable = self.read_byte()
      init = self.read_init()
      globls.append(Global(global_type, mutable, init))
    return globls

  @memoize
  def get_start(self):
    start_section = self.get_section(SecType.START)
    if not start_section:
      return None
    self.seek(start_section.offset)
    return self.read_uleb()

  @memoize
  def get_functions(self):
    code_section = self.get_section(SecType.CODE)
    if not code_section:
      return []
    functions = []
    self.seek(code_section.offset)
    num_functions = self.read_uleb()
    for _ in range(num_functions):
      body_size = self.read_uleb()
      start = self.tell()
      functions.append(FunctionBody(start, body_size))
      self.seek(start + body_size)
    return functions

  def get_section(self, section_code):
    return next((s for s in self.sections() if s.type == section_code), None)

  @memoize
  def get_custom_section(self, name):
    for section in self.sections():
      if section.type == SecType.CUSTOM and section.name == name:
        return section
    return None

  @memoize
  def get_segments(self):
    segments = []
    data_section = self.get_section(SecType.DATA)
    self.seek(data_section.offset)
    num_segments = self.read_uleb()
    for _ in range(num_segments):
      flags = self.read_uleb()
      if (flags & SEG_PASSIVE):
        init = None
      else:
        init = self.read_init()
      size = self.read_uleb()
      offset = self.tell()
      segments.append(DataSegment(flags, init, offset, size))
      self.seek(offset + size)
    return segments

  @memoize
  def get_tables(self):
    table_section = self.get_section(SecType.TABLE)
    if not table_section:
      return []

    self.seek(table_section.offset)
    num_tables = self.read_uleb()
    tables = []
    for _ in range(num_tables):
      elem_type = self.read_type()
      limits = self.read_limits()
      tables.append(Table(elem_type, limits))

    return tables

  @memoize
  def get_function_types(self):
    function_section = self.get_section(SecType.FUNCTION)
    if not function_section:
      return []

    self.seek(function_section.offset)
    num_types = self.read_uleb()
    func_types = []
    for _ in range(num_types):
      func_types.append(self.read_uleb())
    return func_types

  def has_name_section(self):
    return self.get_custom_section('name') is not None

  @once
  def _calc_indexes(self):
    self.imports_by_kind = {}
    for i in self.get_imports():
      self.imports_by_kind.setdefault(i.kind, [])
      self.imports_by_kind[i.kind].append(i)

  def num_imported_funcs(self):
    self._calc_indexes()
    return len(self.imports_by_kind.get(ExternType.FUNC, []))

  def num_imported_globals(self):
    self._calc_indexes()
    return len(self.imports_by_kind.get(ExternType.GLOBAL, []))

  def get_function(self, idx):
    self._calc_indexes()
    assert idx >= self.num_imported_funcs()
    return self.get_functions()[idx - self.num_imported_funcs()]

  def get_global(self, idx):
    self._calc_indexes()
    assert idx >= self.num_imported_globals()
    return self.get_globals()[idx - self.num_imported_globals()]

  def get_function_type(self, idx):
    self._calc_indexes()
    if idx < self.num_imported_funcs():
      imp = self.imports_by_kind[ExternType.FUNC][idx]
      func_type = imp.type
    else:
      func_type = self.get_function_types()[idx - self.num_imported_funcs()]
    return self.get_types()[func_type]


def parse_dylink_section(wasm_file):
  with Module(wasm_file) as module:
    return module.parse_dylink_section()


def get_exports(wasm_file):
  with Module(wasm_file) as module:
    return module.get_exports()


def get_imports(wasm_file):
  with Module(wasm_file) as module:
    return module.get_imports()


def get_weak_imports(wasm_file):
  weak_imports = []
  dylink_sec = parse_dylink_section(wasm_file)
  for symbols in dylink_sec.import_info.values():
    for symbol, flags in symbols.items():
      if flags & SYMBOL_BINDING_MASK == SYMBOL_BINDING_WEAK:
        weak_imports.append(symbol)
  return weak_imports

# SIG # Begin Windows Authenticode signature block
# MIIoPwYJKoZIhvcNAQcCoIIoMDCCKCwCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCDkO3FKhvR1agIC
# T0YwshiGh+0eGRYn8pzKigdExm/jfKCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGgowghoGAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEIN6xNQ2NEjbE5vmIm7qTF+uRbZ89Uc1gYyzGAu9J+QUiMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAq3JSFZtg0m2+6HgT0SJ5zoI+MjEk
# 2Eqwu+cmxYZ9UoECOCTyiodOUzlscYzyMtqhi0Xn0q5vpliU5a43RaTjYytQ43u7
# leMZfhW51/gvOagx8TtXq2EaxZQomN5MvNeUofntKThL1byy0XokLiQ8y5rVVnJM
# Toi/tMaiPNXt3/rZ/BhmCpOWe/q73vX3s61GJWLLLj0kywCe9+4lVHZ2v3dMV529
# HmrSdLYVoNyYJuA0d3vbu1lqGVfHmBZ8awkFvBrocFg/QlAKoqoFU6ZTtat6B+fk
# KqEktc/Rs8ucYZM6jNKz8JEUKiQtfJ9n9PvvI2+JKR16/SU63Ovp0Ynmd6GCF5Qw
# gheQBgorBgEEAYI3AwMBMYIXgDCCF3wGCSqGSIb3DQEHAqCCF20wghdpAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCAdOiZbe8P/flUSvNYQDXDvWM0P
# tTRE5+Mo0EESWa/8zgIGaO/jiLKeGBMyMDI1MTAxNjE2MTcxOC4zMzhaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046QTkzNS0wM0UwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHqMIIHIDCCBQigAwIBAgITMwAAAgy5ZOM1
# nOz0rgABAAACDDANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQzMDBaFw0yNjA0MjIxOTQzMDBaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# QTkzNS0wM0UwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDKAVYmPeRtga/U
# 6jzqyqLD0MAool23gcBN58+Z/XskYwNJsZ+O+wVyQYl8dPTK1/BC2xAic1m+Jvck
# qjVaQ32KmURsEZotirQY4PKVW+eXwRt3r6szgLuic6qoHlbXox/l0HJtgURkzDXW
# MkKmGSL7z8/crqcvmYqv8t/slAF4J+mpzb9tMFVmjwKXONVdRwg9Q3WaPZBC7Wvo
# i7PRIN2jgjSBnHYyAZSlstKNrpYb6+Gu6oSFkQzGpR65+QNDdkP4ufOf4PbOg3fb
# 4uGPjI8EPKlpwMwai1kQyX+fgcgCoV9J+o8MYYCZUet3kzhhwRzqh6LMeDjaXLP7
# 01SXXiXc2ZHzuDHbS/sZtJ3627cVpClXEIUvg2xpr0rPlItHwtjo1PwMCpXYqnYK
# vX8aJ8nawT9W8FUuuyZPG1852+q4jkVleKL7x+7el8ETehbdkwdhAXyXimaEzWet
# NNSmG/KfHAp9czwsL1vKr4Rgn+pIIkZHuomdf5e481K+xIWhLCPdpuV87EqGOK/j
# bhOnZEqwdvA0AlMaLfsmCemZmupejaYuEk05/6cCUxgF4zCnkJeYdMAP+9Z4kVh7
# tzRFsw/lZSl2D7EhIA6Knj6RffH2k7YtSGSv86CShzfiXaz9y6sTu8SGqF6ObL/e
# u/DkivyVoCfUXWLjiSJsrS63D0EHHQIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFHUO
# RSH/sB/rQ/beD0l5VxQ706GIMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQDZMPr4
# gVmwwf4GMB5ZfHSr34uhug6yzu4HUT+JWMZqz9uhLZBoX5CPjdKJzwAVvYoNuLmS
# 0+9lA5S74rvKqd/u9vp88VGk6U7gMceatdqpKlbVRdn2ZfrMcpI4zOc6BtuYrzJV
# 4cEs1YmX95uiAxaED34w02BnfuPZXA0edsDBbd4ixFU8X/1J0DfIUk1YFYPOrmwm
# I2k16u6TcKO0YpRlwTdCq9vO0eEIER1SLmQNBzX9h2ccCvtgekOaBoIQ3ZRai8Ds
# 1f+wcKCPzD4qDX3xNgvLFiKoA6ZSG9S/yOrGaiSGIeDy5N9VQuqTNjryuAzjvf5W
# 8AQp31hV1GbUDOkbUdd+zkJWKX4FmzeeN52EEbykoWcJ5V9M4DPGN5xpFqXy9aO0
# +dR0UUYWuqeLhDyRnVeZcTEu0xgmo+pQHauFVASsVORMp8TF8dpesd+tqkkQ8VNv
# I20oOfnTfL+7ZgUMf7qNV0ll0Wo5nlr1CJva1bfk2Hc5BY1M9sd3blBkezyvJPn4
# j0bfOOrCYTwYsNsjiRl/WW18NOpiwqciwFlUNqtWCRMzC9r84YaUMQ82Bywk48d4
# uBon5ZA8pXXS7jwJTjJj5USeRl9vjT98PDZyCFO2eFSOFdDdf6WBo/WZUA2hGZ0q
# +J7j140fbXCfOUIm0j23HaAV0ckDS/nmC/oF1jCCB3EwggVZoAMCAQICEzMAAAAV
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
# BRDBcQZqELQdVTNYs6FwZvKhggNNMIICNQIBATCB+aGB0aSBzjCByzELMAkGA1UE
# BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAc
# BgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjElMCMGA1UECxMcTWljcm9zb2Z0
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOkE5
# MzUtMDNFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQDvu8hkhEMt5Z8Ldefls7z1LVU8pqCBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JsKrzAiGA8yMDI1MTAxNjA2MDk1MVoYDzIwMjUxMDE3MDYwOTUxWjB0MDoGCisG
# AQQBhFkKBAExLDAqMAoCBQDsmwqvAgEAMAcCAQACAgGKMAcCAQACAhOqMAoCBQDs
# nFwvAgEAMDYGCisGAQQBhFkKBAIxKDAmMAwGCisGAQQBhFkKAwKgCjAIAgEAAgMH
# oSChCjAIAgEAAgMBhqAwDQYJKoZIhvcNAQELBQADggEBAAWh74Wca3x++/3NC7lF
# fSauyX57LX+Fg0+gh2HWDBvdzELZX8XyDoJ/f0IOgLn3uoNo3FxVHDItxqmXtnRK
# cYeJP/KkO2pMVIkru8JBH1N0JBGBN++nfzBNAX9ZBRpkm0O6RbIjSomZ4ytDFDK4
# oSBFsRihmkMyoXiR7aBOlYRH3ZiXx0Aoac/ji6aa6zcSMx/d5RUk5yS3vn2LD8K3
# 5fgMwx1TUmVc5vIujEi5wrTbCMbo2jeRG8D+XI6yWQP+OxvntRD/r7IeeIVTfXxR
# d5IF7O4Hm16F1bow1uLXwWuebwmoqnia31lh5e47PEkITk5gOzMhzMz+Ci9JkY0Y
# fjcxggQNMIIECQIBATCBkzB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGlu
# Z3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBv
# cmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAIT
# MwAAAgy5ZOM1nOz0rgABAAACDDANBglghkgBZQMEAgEFAKCCAUowGgYJKoZIhvcN
# AQkDMQ0GCyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCC8w1+06KNrBc/wQAPR
# gGpUS3GSNBCfB4NvLYFWjtztyzCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQwgb0E
# INUo17cFMZN46MI5NfIAg9Ux5cO5xM9inre5riuOZ8ItMIGYMIGApH4wfDELMAkG
# A1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
# HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9z
# b2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIMuWTjNZzs9K4AAQAAAgwwIgQg
# ppvs/jw2nEYpb870nj/+6c+oRyCBQK8kostz2rWWhtUwDQYJKoZIhvcNAQELBQAE
# ggIAG3bdodCi/2qy2brJ6PGfOMaLCO4BE0oGgTMeAz2PS6iTh4xA85rnBEmnUQMf
# tzelQFVM18cfZW6lL2UH5TYbltMCvT4cvAYHZlWMYy2T6OFADCqUso71RdKBeG2T
# ewWE4OlNZ8BFVXMsrwg0vW5FM04RqfKxyNRL4yDpMIVClHeW6pxhD3o+y56AX/wd
# N+2Df4E4HVFhjBOoc7bYCh8xc3rIlpZ2kc4hXX28VKPMR+i42o+1w0ezQJI9Ar53
# fdqmMNad5BocHrm04NzjS9rjdAXyd7sgurvx+FQNaaql5ACBlXaWtHYSD8k/FkBs
# OW/rg2+8hedNbGKeWjolqcyhqtcvzg7KO+l04H8sQJ2Bm0OTOjIsBdqA9wTNVxbp
# T1WEkvdL164wTaGGNKW1tUiXwuUEx8lJoZEd8Q+RX3+jtpF6SkMCkWejSK+bcI33
# awR47kbwlfy/9YpFsMmpfXBcdqfZ0dtZsiZ4BZAsnFs3Sw/oRuG6irmc0mBSqfpO
# 8j1va0vkaXaOINUjJgQbFTkLtuiuW9Qy7yACW0mYKy5nK4pKBMpODgy4znO+qFud
# C3P+3vhm4cARny3PjOS8jqWbIqrugJbnAqpoJBC7EDN2FqAy56zFgvsk+oARqXq6
# Y70AkmlX8FCxY1P/3NuNzgPe4tUqTYb6RiWoCSBAx2b60JQ=
# SIG # End Windows Authenticode signature block