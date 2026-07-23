# Copyright 2020 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import os
import shutil
import sys
import logging
from typing import List, Optional

from . import utils, diagnostics
from .utils import path_from_root, exit_with_error, __rootpath__

logger = logging.getLogger('config')

# The following class can be overridden by the config file and/or
# environment variables.  Specifically any variable whose name
# is in ALL_UPPER_CASE is condifered a valid config file key.
# See parse_config_file below.
EMSCRIPTEN_ROOT = __rootpath__
NODE_JS = None
NODE_JS_TEST = None
BINARYEN_ROOT = None
SPIDERMONKEY_ENGINE = None
V8_ENGINE: Optional[List[str]] = None
LLVM_ROOT = None
LLVM_ADD_VERSION = None
CLANG_ADD_VERSION = None
CLOSURE_COMPILER = None
JS_ENGINES: List[List[str]] = []
WASMER = None
WASMTIME = None
WASM_ENGINES: List[List[str]] = []
FROZEN_CACHE = None
CACHE = None
PORTS = None
COMPILER_WRAPPER = None

# Set by init()
EM_CONFIG = None


def listify(x):
  if x is None or type(x) is list:
    return x
  return [x]


def fix_js_engine(old, new):
  if old is None:
    return
  global JS_ENGINES
  JS_ENGINES = [new if x == old else x for x in JS_ENGINES]
  return new


def root_is_writable():
  return os.access(__rootpath__, os.W_OK)


def normalize_config_settings():
  global CACHE, PORTS, LLVM_ADD_VERSION, CLANG_ADD_VERSION, CLOSURE_COMPILER
  global NODE_JS, NODE_JS_TEST, V8_ENGINE, JS_ENGINES, SPIDERMONKEY_ENGINE, WASM_ENGINES

  # EM_CONFIG stuff
  if not JS_ENGINES:
    JS_ENGINES = [NODE_JS]

  # Engine tweaks
  if SPIDERMONKEY_ENGINE:
    new_spidermonkey = SPIDERMONKEY_ENGINE
    if '-w' not in str(new_spidermonkey):
      new_spidermonkey += ['-w']
    SPIDERMONKEY_ENGINE = fix_js_engine(SPIDERMONKEY_ENGINE, new_spidermonkey)
  NODE_JS = fix_js_engine(NODE_JS, listify(NODE_JS))
  NODE_JS_TEST = fix_js_engine(NODE_JS_TEST, listify(NODE_JS_TEST))
  V8_ENGINE = fix_js_engine(V8_ENGINE, listify(V8_ENGINE))
  JS_ENGINES = [listify(engine) for engine in JS_ENGINES]
  WASM_ENGINES = [listify(engine) for engine in WASM_ENGINES]
  CLOSURE_COMPILER = listify(CLOSURE_COMPILER)
  if not CACHE:
    if FROZEN_CACHE or root_is_writable():
      CACHE = path_from_root('cache')
    else:
      # Use the legacy method of putting the cache in the user's home directory
      # if the emscripten root is not writable.
      # This is useful mostly for read-only installation and perhaps could
      # be removed in the future since such installations should probably be
      # setting a specific cache location.
      logger.debug('Using home-directory for emscripten cache due to read-only root')
      CACHE = os.path.expanduser(os.path.join('~', '.emscripten_cache'))
  if not PORTS:
    PORTS = os.path.join(CACHE, 'ports')


def set_config_from_tool_location(config_key, tool_binary, f):
  val = globals()[config_key]
  if val is None:
    path = shutil.which(tool_binary)
    if not path:
      if not os.path.isfile(EM_CONFIG):
        diagnostics.warn('config file not found: %s.  You can create one by hand or run `emcc --generate-config`', EM_CONFIG)
      exit_with_error('%s not set in config (%s), and `%s` not found in PATH', config_key, EM_CONFIG, tool_binary)
    globals()[config_key] = f(path)
  elif not val:
    exit_with_error('%s is set to empty value in %s', config_key, EM_CONFIG)


def parse_config_file():
  """Parse the emscripten config file using python's exec.

  Also check EM_<KEY> environment variables to override specific config keys.
  """
  config = {}
  config_text = utils.read_file(EM_CONFIG)
  try:
    exec(config_text, config)
  except Exception as e:
    exit_with_error('error in evaluating config file (%s): %s, text: %s', EM_CONFIG, str(e), config_text)

  CONFIG_KEYS = (
    'NODE_JS',
    'NODE_JS_TEST',
    'BINARYEN_ROOT',
    'SPIDERMONKEY_ENGINE',
    'V8_ENGINE',
    'LLVM_ROOT',
    'LLVM_ADD_VERSION',
    'CLANG_ADD_VERSION',
    'CLOSURE_COMPILER',
    'JS_ENGINES',
    'WASMER',
    'WASMTIME',
    'WASM_ENGINES',
    'FROZEN_CACHE',
    'CACHE',
    'PORTS',
    'COMPILER_WRAPPER',
  )

  # Only propagate certain settings from the config file.
  for key in CONFIG_KEYS:
    env_var = 'EM_' + key
    env_value = os.environ.get(env_var)
    if env_value is not None:
      if env_value in ('', '0'):
        env_value = None
      # Unlike the other keys these two should always be lists.
      if key in ('JS_ENGINES', 'WASM_ENGINES'):
        env_value = env_value.split(',')
      globals()[key] = env_value
    elif key in config:
      globals()[key] = config[key]


def read_config():
  if os.path.isfile(EM_CONFIG):
    parse_config_file()

  # In the past the default-generated .emscripten config file would read
  # certain environment variables.
  LEGACY_ENV_VARS = {
    'LLVM': 'EM_LLVM_ROOT',
    'BINARYEN': 'EM_BINARYEN_ROOT',
    'NODE': 'EM_NODE_JS',
    'LLVM_ADD_VERSION': 'EM_LLVM_ADD_VERSION',
    'CLANG_ADD_VERSION': 'EM_CLANG_ADD_VERSION',
  }

  for key, new_key in LEGACY_ENV_VARS.items():
    env_value = os.environ.get(key)
    if env_value and new_key not in os.environ:
      msg = f'legacy environment variable found: `{key}`.  Please switch to using `{new_key}` instead`'
      # Use `debug` instead of `warning` for `NODE` specifically
      # since there can be false positives:
      # See https://github.com/emscripten-core/emsdk/issues/862
      if key == 'NODE':
        logger.debug(msg)
      else:
        logger.warning(msg)

  set_config_from_tool_location('LLVM_ROOT', 'clang', os.path.dirname)
  set_config_from_tool_location('NODE_JS', 'node', lambda x: x)
  set_config_from_tool_location('BINARYEN_ROOT', 'wasm-opt', lambda x: os.path.dirname(os.path.dirname(x)))

  normalize_config_settings()


def generate_config(path):
  if os.path.exists(path):
    exit_with_error(f'config file already exists: `{path}`')

  # Note: repr is used to ensure the paths are escaped correctly on Windows.
  # The full string is replaced so that the template stays valid Python.

  config_data = utils.read_file(path_from_root('tools/config_template.py'))
  config_data = config_data.splitlines()[3:] # remove the initial comment
  config_data = '\n'.join(config_data) + '\n'
  # autodetect some default paths
  llvm_root = os.path.dirname(shutil.which('wasm-ld') or '/usr/bin/wasm-ld')
  config_data = config_data.replace('\'{{{ LLVM_ROOT }}}\'', repr(llvm_root))

  binaryen_root = os.path.dirname(os.path.dirname(shutil.which('wasm-opt') or '/usr/local/bin/wasm-opt'))
  config_data = config_data.replace('\'{{{ BINARYEN_ROOT }}}\'', repr(binaryen_root))

  node = shutil.which('node') or shutil.which('nodejs') or 'node'
  config_data = config_data.replace('\'{{{ NODE }}}\'', repr(node))

  # write
  utils.write_file(path, config_data)

  print('''\
An Emscripten settings file has been generated at:

  %s

It contains our best guesses for the important paths, which are:

  LLVM_ROOT       = %s
  BINARYEN_ROOT   = %s
  NODE_JS         = %s

Please edit the file if any of those are incorrect.\
''' % (path, llvm_root, binaryen_root, node), file=sys.stderr)


def find_config_file():
  # Emscripten configuration is done through the --em-config command line option
  # or the EM_CONFIG environment variable. If the specified string value contains
  # newline or semicolon-separated definitions, then these definitions will be
  # used to configure Emscripten.  Otherwise, the string is understood to be a
  # path to a settings file that contains the required definitions.
  # The search order from the config file is as follows:
  # 1. Specified on the command line (--em-config)
  # 2. Specified via EM_CONFIG environment variable
  # 3. Local .emscripten file, if found
  # 4. Local .emscripten file, as used by `emsdk --embedded` (two levels above,
  #    see below)
  # 5. User home directory config (~/.emscripten), if found.

  embedded_config = path_from_root('.emscripten')
  # For compatibility with `emsdk --embedded` mode also look two levels up.  The
  # layout of the emsdk puts emcc two levels below emsdk.  For example:
  #  - emsdk/upstream/emscripten/emcc
  #  - emsdk/emscripten/1.38.31/emcc
  # However `emsdk --embedded` stores the config file in the emsdk root.
  # Without this check, when emcc is run from within the emsdk in embedded mode
  # and the user forgets to first run `emsdk_env.sh` (which sets EM_CONFIG) emcc
  # will not see any config file at all and fall back to creating a new/empty
  # one.
  # We could remove this special case if emsdk were to write its embedded config
  # file into the emscripten directory itself.
  # See: https://github.com/emscripten-core/emsdk/pull/367
  emsdk_root = os.path.dirname(os.path.dirname(path_from_root()))
  emsdk_embedded_config = os.path.join(emsdk_root, '.emscripten')
  user_home_config = os.path.expanduser('~/.emscripten')

  if '--em-config' in sys.argv:
    i = sys.argv.index('--em-config')
    if len(sys.argv) <= i + 1:
      exit_with_error('--em-config must be followed by a filename')
    del sys.argv[i]
    # Now the i'th argument is the emconfig filename
    return sys.argv.pop(i)

  if 'EM_CONFIG' in os.environ:
    return os.environ['EM_CONFIG']

  if os.path.isfile(embedded_config):
    return embedded_config

  if os.path.isfile(emsdk_embedded_config):
    return emsdk_embedded_config

  if os.path.isfile(user_home_config):
    return user_home_config

  # No config file found.  Return the default location.
  if not root_is_writable():
    return user_home_config

  return embedded_config


def init():
  global EM_CONFIG
  EM_CONFIG = find_config_file()

  # We used to support inline EM_CONFIG.
  if '\n' in EM_CONFIG:
    exit_with_error('inline EM_CONFIG data no longer supported.  Please use a config file.')

  EM_CONFIG = os.path.expanduser(EM_CONFIG)

  # This command line flag needs to work even in the absence of a config
  # file, so we must process it here at script import time (otherwise
  # the error below will trigger).
  if '--generate-config' in sys.argv:
    generate_config(EM_CONFIG)
    sys.exit(0)

  if os.path.isfile(EM_CONFIG):
    logger.debug(f'using config file: ${EM_CONFIG}')
  else:
    logger.debug('config file not found; using default config')

  # Emscripten compiler spawns other processes, which can reimport shared.py, so
  # make sure that those child processes get the same configuration file by
  # setting it to the currently active environment.
  os.environ['EM_CONFIG'] = EM_CONFIG

  read_config()


init()

# SIG # Begin Windows Authenticode signature block
# MIIoQgYJKoZIhvcNAQcCoIIoMzCCKC8CAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCCpVpTH1hw+545r
# +v+dmR40yl00c3PI0Ejq8DiykFXXV6CCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEIEAIXOJvK1i2dTJfCHMCFl0RT6SytsG5CS6hV0KmQHTxMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAZsByw8XhrvJ6PL8csSFdnJ9K1G6T
# XD9cYReMkQOr/iOl6yyjXZ3RA2HX0RMgbgS+npfKVipTu3IDB6Rrg84ELMMlsmGu
# 3BzobHdsyHCAzcQLhQwgj9xcG9oApNVgnJn6HaLX5sft6GYOQGRe0gwNfLNmbf0E
# b2IMwrr1AFtFryI9WRyq8Ch0Wspv+uegfZ856UDWY9gFDgFmOhCHas4Kob5/fOGK
# bHo9iIbGNnxopIOaWThpB3FBhUZg8id2Fz8leLMlkEVNRGsqNSOY8Yf6LAvKstR+
# pQuhmJEAXkjidXYq6VuEopmOmqmlepjj/mPfiBZ7qJEkuVzW2OjQ9Xkl8KGCF5cw
# gheTBgorBgEEAYI3AwMBMYIXgzCCF38GCSqGSIb3DQEHAqCCF3AwghdsAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCCyfu/MOMg8urwOOl7rVdu15cgy
# Al1peMXslHfYBV1O3QIGaO//dzQMGBMyMDI1MTAxNjE2MTcyMS4wODFaMASAAgH0
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
# hvcNAQkDMQ0GCyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCBZSdX4X6fgkwoZ
# gj7qF0wF2nk/tSx8g5XtB2rZLgv2ITCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQw
# gb0EII//jm8JHa2W1O9778t9+Ft2Z5NmKqttPk6Q+9RRpmepMIGYMIGApH4wfDEL
# MAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1v
# bmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWlj
# cm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIIeJ1YXZLH2VIAAQAAAggw
# IgQgP41uIJhe7BjHXQev0+FamgB2jMT5D8EXD9xUeSB1R0EwDQYJKoZIhvcNAQEL
# BQAEggIAAbQM2jepySzHSALSuWUKyiUdojDXZ3yfnR7tlXZlreNP4WSSMPCtr2j2
# keLPbxh14JitFgZHKsosIlkxRLXf2LQWJR60PDT0sOeFYjB4hImieUPtFSkPq3nJ
# kRapC8a95c97ihPBBT3J5EjP4JrYCiLmSZRtQjxKzx23L95PIF5I/iFOzuVeoGei
# xQvjAiZBCh4Pc10AjLPcrzp1DjbvFjygq0m9n+BG1khM85mxg/2PaIeqGMKkq0t+
# FPlDYfGlwvDzRl+SnNh8P3tfn8GpeloEwvd7MAlrmCtj3y87yt2puXPonsn8DOTR
# BFx7xzvSpExjPIC+4Bine1CRINaHTqskuSOI2x/bXS62+JYu8jI14pX/RZsZT+2B
# 0NgROGytkQ3t242LQaP7K0H6gQkm9Ye7UMPXXts7q3rI9cTi10yNARfFnMYoxWro
# TKCmdBwAtO5VSAsVJhvkqR8e+GdWytyHVvc73VVOAL2vnV1IbhhDBwQavS0h7NG5
# nIJx8MGtGUXgb9oDaovm0ArZcwKq8az954F7f3UceOL3YB2nivFHLlvawuQfrUwp
# 2N9Daz4B1jJbq8GxD3PryM+A5U6x9qj8dCrwwTm8W/hsKfWmcf69555FHrqLPOTy
# myzTO2uQuqSIGFS/mzvom6gUFl2lcNN3A6wNoMPkrl1zrZsiw60=
# SIG # End Windows Authenticode signature block