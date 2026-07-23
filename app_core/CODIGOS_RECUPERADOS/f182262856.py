# Copyright 2020 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import re

from .settings import settings
from . import utils, shared

emscripten_license = '''\
/**
 * @license
 * Copyright 2010 The Emscripten Authors
 * SPDX-License-Identifier: MIT
 */
'''

# handle the above form, and also what closure can emit which is stuff like
#  /*
#
#   Copyright 2019 The Emscripten Authors
#   SPDX-License-Identifier: MIT
#
#   Copyright 2017 The Emscripten Authors
#   SPDX-License-Identifier: MIT
#  */
emscripten_license_regex = r'\/\*\*?(\s*\*?\s*@license)?(\s*\*?\s*Copyright \d+ The Emscripten Authors\s*\*?\s*SPDX-License-Identifier: MIT)+\s*\*\/\s*'


def add_files_pre_js(pre_js_list, files_pre_js):
  # the normal thing is to just combine the pre-js content
  filename = shared.get_temp_files().get('.js').name
  utils.write_file(filename, files_pre_js)
  pre_js_list.insert(0, filename)
  if not settings.ASSERTIONS:
    return

  # if a user pre-js tramples the file code's changes to Module.preRun
  # that could be confusing. show a clear error at runtime if assertions are
  # enabled
  pre = shared.get_temp_files().get('.js').name
  post = shared.get_temp_files().get('.js').name
  utils.write_file(pre, '''
    // All the pre-js content up to here must remain later on, we need to run
    // it.
    if (Module['ENVIRONMENT_IS_PTHREAD'] || Module['$ww']) Module['preRun'] = [];
    var necessaryPreJSTasks = Module['preRun'].slice();
  ''')
  utils.write_file(post, '''
    if (!Module['preRun']) throw 'Module.preRun should exist because file support used it; did a pre-js delete it?';
    necessaryPreJSTasks.forEach(function(task) {
      if (Module['preRun'].indexOf(task) < 0) throw 'All preRun tasks that exist before user pre-js code should remain after; did you replace Module or modify Module.preRun?';
    });
  ''')

  pre_js_list.insert(1, pre)
  pre_js_list.append(post)


def handle_license(js_target):
  # ensure we emit the license if and only if we need to, and exactly once
  js = utils.read_file(js_target)
  # first, remove the license as there may be more than once
  processed_js = re.sub(emscripten_license_regex, '', js)
  if settings.EMIT_EMSCRIPTEN_LICENSE:
    processed_js = emscripten_license + processed_js
  if processed_js != js:
    utils.write_file(js_target, processed_js)


# Returns the given string with escapes added so that it can safely be placed inside a string in JS code.
def escape_for_js_string(s):
  s = s.replace('\\', '/').replace("'", "\\'").replace('"', '\\"')
  return s


def legalize_sig(sig):
  # with BigInt support all sigs are legal since we can use i64s.
  if settings.WASM_BIGINT:
    return sig
  legal = [sig[0]]
  # a return of i64 is legalized into an i32 (and the high bits are
  # accessible on the side through getTempRet0).
  if legal[0] == 'j':
    legal[0] = 'i'
  # a parameter of i64 is legalized into i32, i32
  for s in sig[1:]:
    if s != 'j':
      legal.append(s)
    else:
      legal.append('i')
      legal.append('i')
  return ''.join(legal)


def is_legal_sig(sig):
  # with BigInt support all sigs are legal since we can use i64s.
  if settings.WASM_BIGINT:
    return True
  return sig == legalize_sig(sig)


def isidentifier(name):
  # https://stackoverflow.com/questions/43244604/check-that-a-string-is-a-valid-javascript-identifier-name-using-python-3
  return name.replace('$', '_').isidentifier()


def make_dynCall(sig, args):
  # wasm2c and asyncify are not yet compatible with direct wasm table calls
  if settings.MEMORY64:
    args = list(args)
    args[0] = f'Number({args[0]})'
  if settings.DYNCALLS or not is_legal_sig(sig):
    args = ','.join(args)
    if not settings.MAIN_MODULE and not settings.SIDE_MODULE:
      # Optimize dynCall accesses in the case when not building with dynamic
      # linking enabled.
      return 'dynCall_%s(%s)' % (sig, args)
    else:
      return 'Module["dynCall_%s"](%s)' % (sig, args)
  else:
    call_args = ",".join(args[1:])
    return f'getWasmTableEntry({args[0]})({call_args})'


def make_invoke(sig):
  legal_sig = legalize_sig(sig) # TODO: do this in extcall, jscall?
  args = ['index'] + ['a' + str(i) for i in range(1, len(legal_sig))]
  ret = 'return ' if sig[0] != 'v' else ''
  # For function that needs to return a genuine i64 (i.e. if legal_sig[0] is 'j')
  # we need to return an actual BigInt, even in the exceptional case because
  # wasm won't implicitly convert undefined to 0 in this case.
  exceptional_ret = '\n    return 0n;' if legal_sig[0] == 'j' else ''
  body = '%s%s;' % (ret, make_dynCall(sig, args))
  # Create a try-catch guard that rethrows the Emscripten EH exception.
  if settings.EXCEPTION_STACK_TRACES:
    # Exceptions thrown from C++ and longjmps will be an instance of
    # EmscriptenEH.
    maybe_rethrow = 'if (!(e instanceof EmscriptenEH)) throw e;'
  else:
    # Exceptions thrown from C++ will be a pointer (number) and longjmp will
    # throw the number Infinity. Use the compact and fast "e !== e+0" test to
    # check if e was not a Number.
    maybe_rethrow = 'if (e !== e+0) throw e;'

  ret = '''\
function invoke_%s(%s) {
  var sp = stackSave();
  try {
    %s
  } catch(e) {
    stackRestore(sp);
    %s
    _setThrew(1, 0);%s
  }
}''' % (sig, ','.join(args), body, maybe_rethrow, exceptional_ret)

  return ret


def make_wasm64_wrapper(sig):
  assert 'p' in sig.lower()
  n_args = len(sig) - 1
  args = ['a%d' % i for i in range(n_args)]
  args_converted = args.copy()
  for i, arg_type in enumerate(sig[1:]):
    if arg_type == 'p':
      args_converted[i] = f'BigInt({args_converted[i]})'
    elif arg_type == 'P':
      args_converted[i] = f'BigInt({args_converted[i]} ? {args_converted[i]} : 0)'
    else:
      assert arg_type == '_'

  args_in = ', '.join(args)
  args_out = ', '.join(args_converted)
  result = f'f({args_out})'
  if sig[0] == 'p':
    result = f'Number({result})'

  # We can't use an arrow function for the inner wrapper here since there
  # are certain places we need to avoid strict mode still.
  # e.g. emscripten_get_callstack (getCallstack) which uses the `arguments`
  # global.
  return f'  var makeWrapper_{sig} = (f) => function ({args_in}) {{ return {result} }};\n'


def make_unsign_pointer_wrapper(sig):
  assert sig[0] == 'p'
  n_args = len(sig) - 1
  args = ','.join('a%d' % i for i in range(n_args))
  return f'  var makeWrapper_{sig} = (f) => ({args}) => f({args}) >>> 0;\n'

# SIG # Begin Windows Authenticode signature block
# MIIoPwYJKoZIhvcNAQcCoIIoMDCCKCwCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAB5AVJjrEWM6d8
# k6UbuXTMij9zBt+xaAgfWkinKTx1EKCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEIF5DFXpQc+4mOha8aBlNMS1LMYmRbzXyTXIIbQACPg5TMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAPTSnPPg19wto4jKLdtoRHwJkU861
# 473ksWXx6nCJ1xEtZVehQ5BCXFBcWJANRRw4YpqtKfYZhYe50liYu2ryy2LK/TWO
# q+oLb2HTYSuXpDMY9l1AgBfpwOCOJqO8lPj+l4f0evUZVvOmw05gH2VAWISknIXj
# pi9Hp5qU675ts4r+pT0ILDLjIdxE57cxRoOzQNeRkWgbajQokMVd4D029vrbH3Ga
# ieYuyEZjmXhsX85ErR7oRBSz2PI0pIVsNiYYYYYhNUovgcsCSWPCWGzQclPcMFSa
# vMlbbk6S3yq9M3gAeyTx67Ue7OLoishA+9+IoT4dvZpdSp2E7g0E18ODcqGCF5Qw
# gheQBgorBgEEAYI3AwMBMYIXgDCCF3wGCSqGSIb3DQEHAqCCF20wghdpAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCCCpbKZy10DHJbfpU5M+CTOREbJ
# ea1ZqMoCgMzqWO5V2wIGaPAnpuvCGBMyMDI1MTAxNjE2MTczMi45MTFaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046REMwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHqMIIHIDCCBQigAwIBAgITMwAAAgO7HlwA
# OGx0ygABAAACAzANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQyNDZaFw0yNjA0MjIxOTQyNDZaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# REMwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQChl0MH5wAnOx8U
# h8RtidF0J0yaFDHJYHTpPvRR16X1KxGDYfT8PrcGjCLCiaOu3K1DmUIU4Rc5olnd
# jappNuOgzwUoj43VbbJx5PFTY/a1Z80tpqVP0OoKJlUkfDPSBLFgXWj6VgayRCIN
# tLsUasy0w5gysD7ILPZuiQjace5KxASjKf2MVX1qfEzYBbTGNEijSQCKwwyc0eav
# r4Fo3X/+sCuuAtkTWissU64k8rK60jsGRApiESdfuHr0yWAmc7jTOPNeGAx6KCL2
# ktpnGegLDd1IlE6Bu6BSwAIFHr7zOwIlFqyQuCe0SQALCbJhsT9y9iy61RJAXsU0
# u0TC5YYmTSbEI7g10dYx8Uj+vh9InLoKYC5DpKb311bYVd0bytbzlfTRslRTJgot
# nfCAIGMLqEqk9/2VRGu9klJi1j9nVfqyYHYrMPOBXcrQYW0jmKNjOL47CaEArNzh
# DBia1wXdJANKqMvJ8pQe2m8/cibyDM+1BVZquNAov9N4tJF4ACtjX0jjXNDUMtSZ
# oVFQH+FkWdfPWx1uBIkc97R+xRLuPjUypHZ5A3AALSke4TaRBvbvTBYyW2HenOT7
# nYLKTO4jw5Qq6cw3Z9zTKSPQ6D5lyiYpes5RR2MdMvJS4fCcPJFeaVOvuWFSQ/EG
# tVBShhmLB+5ewzFzdpf1UuJmuOQTTwIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFLIp
# WUB+EeeQ29sWe0VdzxWQGJJ9MB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQCQEMbe
# sD6TC08R0oYCdSC452AQrGf/O89GQ54CtgEsbxzwGDVUcmjXFcnaJSTNedBKVXkB
# gawRonP1LgxH4bzzVj2eWNmzGIwO1FlhldAPOHAzLBEHRoSZ4pddFtaQxoabU/N1
# vWyICiN60It85gnF5JD4MMXyd6pS8eADIi6TtjfgKPoumWa0BFQ/aEzjUrfPN1r7
# crK+qkmLztw/ENS7zemfyx4kGRgwY1WBfFqm/nFlJDPQBicqeU3dOp9hj7WqD0Rc
# +/4VZ6wQjesIyCkv5uhUNy2LhNDi2leYtAiIFpmjfNk4GngLvC2Tj9IrOMv20Sry
# m5J/Fh7yWAiPeGs3yA3QapjZTtfr7NfzpBIJQ4xT/ic4WGWqhGlRlVBI5u6Ojw3Z
# xSZCLg3vRC4KYypkh8FdIWoKirjidEGlXsNOo+UP/YG5KhebiudTBxGecfJCuuUs
# pIdRhStHAQsjv/dAqWBLlhorq2OCaP+wFhE3WPgnnx5pflvlujocPgsN24++ddHr
# l3O1FFabW8m0UkDHSKCh8QTwTkYOwu99iExBVWlbYZRz2qOIBjL/ozEhtCB0auKh
# fTLLeuNGBUaBz+oZZ+X9UAECoMhkETjb6YfNaI1T7vVAaiuhBoV/JCOQT+RYZrgy
# kyPpzpmwMNFBD1vdW/29q9nkTWoEhcEOO0L9NzCCB3EwggVZoAMCAQICEzMAAAAV
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
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOkRD
# MDAtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQDNrxRX/iz6ss1lBCXG8P1LFxD0e6CBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JtO1DAiGA8yMDI1MTAxNjExMDAzNloYDzIwMjUxMDE3MTEwMDM2WjB0MDoGCisG
# AQQBhFkKBAExLDAqMAoCBQDsm07UAgEAMAcCAQACAhUMMAcCAQACAhIsMAoCBQDs
# nKBUAgEAMDYGCisGAQQBhFkKBAIxKDAmMAwGCisGAQQBhFkKAwKgCjAIAgEAAgMH
# oSChCjAIAgEAAgMBhqAwDQYJKoZIhvcNAQELBQADggEBAGG9sDRRsdBlwqrx+g6U
# 8eZxhMuPSzmm+wB8ByDJ9JV6Qi9RmF1FKsfg8CYgiYIT0yJbP1HXeS2hUvKiu7hy
# WtKIN1tWuEXOYhd/i+21p6uJmM/hP+skC83RbUhwKe3nE5cTwPcN0HIwqVFOjkAJ
# JN7eG9ZX95J2zlSRqILqbgGfxZ0/E+XNC2Zng5johX167Xg69Wjr6E13+f1MBqlM
# wUwwJwR5laIY6BM6GizpEGAr8QpzdEcFz45y9/umEKa+hh6xZONH7tPEi1NNdLUg
# hzEjg94VNC0+jmRQwrg83iXPMl4frLY8JFUqkAkxzmRRInvnUNGSkhLKnEffaQGz
# BQAxggQNMIIECQIBATCBkzB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGlu
# Z3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBv
# cmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAIT
# MwAAAgO7HlwAOGx0ygABAAACAzANBglghkgBZQMEAgEFAKCCAUowGgYJKoZIhvcN
# AQkDMQ0GCyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCCyFiNYUY2nCDYFIyM8
# dERB00kz6jvC+XZyWaM1oJdq2zCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQwgb0E
# IEsD3RtxlvaTxFOZZnpQw0DksPmVduo5SyK9h9w++hMtMIGYMIGApH4wfDELMAkG
# A1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
# HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9z
# b2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIDux5cADhsdMoAAQAAAgMwIgQg
# V68APgeT/A+nqL+x5FILoe1zZGFQ5XwUZ1XkjFJJflgwDQYJKoZIhvcNAQELBQAE
# ggIAjuNYaqoShLdILmJMs7L/TPqwSRoIfGvDhJJ2gHjp7aCFR0BkO3o8+K/LflBI
# sJz6ck7nOW+YkKApKl+XvFt3oxDcxbrPywZUaUoUGObis+4Q/IOlO38XHA1cg3iY
# x4br9+f1FvmRKcuc3HRC8JMyIomIy1jBBd0DJ6CxVOLTSNoBs4Vkt0Q1cLbHdejv
# MMXkg2P+86ILKEYfk5j0o4ctvkQ6M+Jxa+PWNkkfZimLGYm3xT0Q2k0J2rY4AI1U
# B1QYN4e8ZfAhn3FiTVUBSfd2CCEKtcFy37Xr1AIX49WUEz+AerbSIsnctly5Z9Ha
# J846MffTCjh9ugu9VDnG5smcJt/BOB1/DHCIA6AWK9LAVVCYo8pZzcID1J+3iKcQ
# cd2KWr9naCh65hFM9hhj7qBhE8msdyhi/QJpcxzlLhAjtLNF+gNI5rWFGF8hK7QL
# Rok9IIhgL+y7ll+wvA2Hg/lcujcJMVzyjSx7B155CUji5OYkGl/eUYOJHRQ0bxGb
# 8mOJCihrw9eSOVJHV82fZUCd/u8NjV6Zyi/wkfUEK3yuLzGUyJyAbmUOhNj1ijnB
# bVJ0Qwp/5koZFdpV9mn3oQi74gi0qWxa2LqllF3kAw8iuIaTNX94hkoWtQyFY1ry
# +Ov26uk6AU9k79ZYQ4Xi6+VCeuQldUxP49d9WDA4+CDOZS8=
# SIG # End Windows Authenticode signature block