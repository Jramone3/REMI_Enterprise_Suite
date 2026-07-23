#!/usr/bin/env python3
# Copyright 2016 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path


profiler_logs_path = os.path.join(tempfile.gettempdir(), 'emscripten_toolchain_profiler_logs')


# Deletes all previously captured log files to make room for a new clean run.
def delete_profiler_logs():
  if os.path.exists(profiler_logs_path):
    shutil.rmtree(profiler_logs_path)


def list_files_in_directory(d):
  files = []
  if os.path.exists(d):
    for i in os.listdir(d):
      f = os.path.join(d, i)
      if os.path.isfile(f):
        files.append(f)
  return files


def create_profiling_graph(outfile):
  log_files = [f for f in list_files_in_directory(profiler_logs_path) if 'toolchain_profiler.pid_' in f]

  all_results = []
  if len(log_files):
    print(f'Processing {len(log_files)} profile log files in {profiler_logs_path}...')
  for f in log_files:
    print(f'Processing: {f}')
    json_data = Path(f).read_text()
    if len(json_data.strip()) == 0:
      continue
    lines = json_data.split('\n')
    lines = [x for x in lines if x != '[' and x != ']' and x != ',' and len(x.strip())]
    lines = [(x + ',') if not x.endswith(',') else x for x in lines]
    lines[-1] = lines[-1][:-1]
    json_data = '[' + '\n'.join(lines) + ']'
    try:
      all_results += json.loads(json_data)
    except json.JSONDecodeError as e:
      print(str(e), file=sys.stderr)
      print('Failed to parse JSON file "' + f + '"!', file=sys.stderr)
      return 1
  if len(all_results) == 0:
    print(f'No profiler logs were found in path: ${profiler_logs_path}.\nTry setting the environment variable EMPROFILE=1 and run some emcc commands, then re-run "emprofile.py --graph".', file=sys.stderr)
    return 1

  all_results.sort(key=lambda x: x['time'])

  emprofile_json_data = json.dumps(all_results, indent=2)

  html_file = outfile + '.html'
  html_contents = Path(os.path.dirname(os.path.realpath(__file__)), 'toolchain_profiler.results_template.html').read_text().replace('{{{ emprofile_json_data }}}', emprofile_json_data)
  Path(html_file).write_text(html_contents)
  print(f'Wrote "{html_file}"')
  return 0


def main(args):
  if '--help' in args:
    print('''\
Usage:
       emprofile.py --clear (or -c)
         Deletes all previously recorded profiling log files.
         Use this to abort/drop any previously collected
         profiling data for a new profiling run.

       emprofile.py [--no-clear]
         Draws a graph from all recorded profiling log files,
         and deletes the recorded profiling files, unless
         --no-clear is also passed.

Optional parameters:

        --outfile=x.html (or -o=x.html)
          Specifies the name of the results file to generate.
''')
    return 0

  if '--reset' in args or '--clear' in args or '-c' in args:
    delete_profiler_logs()
    return 0
  else:
    outfile = 'toolchain_profiler.results_' + time.strftime('%Y%m%d_%H%M')
    for i, arg in enumerate(args):
      if arg.startswith('--outfile=') or arg.startswith('-o='):
        outfile = arg.split('=', 1)[1].strip().replace('.html', '')
      elif arg == '-o':
        outfile = args[i + 1].strip().replace('.html', '')
    if create_profiling_graph(outfile):
      return 1
    if '--no-clear' not in args:
      delete_profiler_logs()

  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))

# SIG # Begin Windows Authenticode signature block
# MIIoPgYJKoZIhvcNAQcCoIIoLzCCKCsCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCBAETV0KBbaKoXt
# 2C58oiMTOdolVbIL+gcvjp9FDoxFmKCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEINoStPNVF8qiQkUJbbufOXfgJFxRzY6LKgE+g4OHjPjaMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAIi1FObk5Drw9z2pWFMaA96dgu5k+
# EX17K1Qq3TkN36c7/par7xt1F4tXr7wWf7czEPgUe6kAvGYHYaVcQN8492Z0Ak0u
# JQPpkci/9QXoR6pVOV/aW6DX9IbGt/Yckd6c8463rk/qBxoOsDM3ZqYp/yTgQY3a
# z4zSAMSw0X4RyoAQPN86ldJhM1pTlwWVns3YSLrC3lDYHUYeE8nXIoUpTkGa6N1y
# tW4JbJ/ZO0MSJRY0Sc5FR3a4FAIk/zlUMs3n6tI3dW/fj1ZakbynXY852tEA6e+K
# 0YjeVWLDXZ7ltFpup+APfXaPTLfJbe/vCAgTFCNO8+o5iEEsR0WfyfW7aqGCF5Mw
# ghePBgorBgEEAYI3AwMBMYIXfzCCF3sGCSqGSIb3DQEHAqCCF2wwghdoAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCDRA4F1bIx6W+fGX9yQSCujOnRp
# 4v1Qmk4olH4l1gjlDQIGaPC0ynK5GBMyMDI1MTAxNjE2MTgzNS4wOTFaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046MzMwMy0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHpMIIHIDCCBQigAwIBAgITMwAAAg9XmkcU
# QOZG5gABAAACDzANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQzMDRaFw0yNjA0MjIxOTQzMDRaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# MzMwMy0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCl6DTurxf66o73
# G0A2yKo1/nYvITBQsd50F52SQzo2cSrt+EDEFCDlSxZzWJD7ujQ1Z1dMbMT6YhK7
# JUvwxQ+LkQXv2k/3v3xw8xJ2mhXuwbT+s1WOL0+9g9AOEAAM6WGjCzI/LZq3/tzH
# r56in/Z++o/2soGhyGhKMDwWl4J4L1Fn8ndtoM1SBibPdqmwmPXpB9QtaP+TCOC1
# vAaGQOdsqXQ8AdlK6Vuk9yW9ty7S0kRP1nXkFseM33NzBu//ubaoJHb1ceYPZ4U4
# EOXBHi/2g09WRL9QWItHjPGJYjuJ0ckyrOG1ksfAZWP+Bu8PXAq4s1Ba/h/nXhXA
# wuxThpvaFb4T0bOjYO/h2LPRbdDMcMfS9Zbhq10hXP6ZFHR0RRJ+rr5A8ID9l0Ug
# oUu/gNvCqHCMowz97udo7eWODA7LaVv81FHHYw3X5DSTUqJ6pwP+/0lxatxajbSG
# sm267zqVNsuzUoF2FzPM+YUIwiOpgQvvjYIBkB+KUwZf2vRIPWmhAEzWZAGTox/0
# vj4eHgxwER9fpThcsbZGSxx0nL54Hz+L36KJyEVio+oJVvUxm75YEESaTh1RnL0D
# ls91sBw6mvKrO2O+NCbUtfx+cQXYS0JcWZef810BW9Bn/eIvow3Kcx0dVuqDfIWf
# W7imeTLAK9QAEk+oZCJzUUTvhh2hYQIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFJnU
# MQ2OtyAhLR/MD2qtJ9lKRP9ZMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQBTowbo
# 1bUE7fXTy+uW9m58qGEXRBGVMEQiFEfSui1fhN7jS+kSiN0SR5Kl3AuV49xOxgHo
# 9+GIne5Mpg5n4NS5PW8nWIWGj/8jkE3pdJZSvAZarXD4l43iMNxDhdBZqVCkAYcd
# FVZnxdy+25MRY6RfaGwkinjnYNFA6DYL/1cxw6Ya4sXyV7FgPdMmxVpffnPEDFv4
# mcVx3jvPZod7gqiDcUHbyV1gaND3PejyJ1MGfBYbAQxsynLX1FUsWLwKsNPRJjyn
# wlzBT/OQbxnzkjLibi4h4dOwcN+H4myDtUSnYq9Xf4YvFlZ+mJs5Ytx4U9JVCyW/
# WERtIEieTvTRgvAYj/4Mh1F2Elf8cdILgzi9ezqYefxdsBD8Vix35yMC5LTnDUoy
# VVulUeeDAJY8+6YBbtXIty4phIkihiIHsyWVxW2YGG6A6UWenuwY6z9oBONvMHlq
# tD37ZyLn0h1kCkkp5kcIIhMtpzEcPkfqlkbDVogMoWy80xulxt64P4+1YIzkRht3
# zTO+jLONu1pmBt+8EUh7DVct/33tuW5NOSx56jXQ1TdOdFBpgcW8HvJii8smQ1TQ
# P42HNIKIJY5aiMkK9M2HoxYrQy2MoHNOPySsOzr3le/4SDdX67uobGkUNerlJKzK
# pTR5ZU0SeNAu5oCyDb6gdtTiaN50lCC6m44sXjCCB3EwggVZoAMCAQICEzMAAAAV
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
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjMz
# MDMtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQBetIzj2C/MkdiI03EyNsCtSOMdWqCBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JszQzAiGA8yMDI1MTAxNjA5MDI1OVoYDzIwMjUxMDE3MDkwMjU5WjBzMDkGCisG
# AQQBhFkKBAExKzApMAoCBQDsmzNDAgEAMAYCAQACAQYwBwIBAAICEmowCgIFAOyc
# hMMCAQAwNgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAKMAgCAQACAweh
# IKEKMAgCAQACAwGGoDANBgkqhkiG9w0BAQsFAAOCAQEAWGSixZRfZE38uH3eQGrV
# uBdXh7bM1JssFkew3EZgReO4Uo0+jE7M2ipIriSwcJwTnflQ3bX/b6R+jjlOos1n
# P77xv2a+EzkxR6ESBjoYSiYlHo8fAuxpPZKge4wyE+6F+wanKGIGa8C8NmLjjcpK
# VBojAp5k8U97mXsY8GkhYCbLhUUyfUPmoSsc5wrl3snmCMWuK2iOwnrcsLC94dS5
# AZwI36TSoKPktSM/1mUNCtFPu3NmlBt/RxEuUmuUQoAQl3c8821js+DXLrng7YKo
# Eyb8eJxFrHYlQ6ruawPieFi21cQHhQyaqntTSJnTFWCJwY0tiXtyrDSaI2Ai9api
# XzGCBA0wggQJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwAhMz
# AAACD1eaRxRA5kbmAAEAAAIPMA0GCWCGSAFlAwQCAQUAoIIBSjAaBgkqhkiG9w0B
# CQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIIoIr9lBJdhH4TRa3eC7
# XDA0qYgc6FXQWNszcpLsygmYMIH6BgsqhkiG9w0BCRACLzGB6jCB5zCB5DCBvQQg
# 3Ud3lSYqebsVbvE/eeIax8cm3jFHxe74zGBddzSKqfgwgZgwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAg9XmkcUQOZG5gABAAACDzAiBCCo
# HzSXphZWo15bRtvtnjfb018BwDIojtXw+T/RyLlUSzANBgkqhkiG9w0BAQsFAASC
# AgAYUU7q7lcFv69Pcyw5gjGb+lurpBV0vz7A+Lng0vVNVTeJsNFpDG2PQ+CkMtSe
# kyYDftEKo6lmTufXUExTBsLagCXFjKlpXMbJxIbyEmWPuGdHoJ3inqgSk82CJuHc
# jGCbb9VEfh+LxpyV3bbyqDEB39WPsfRggfEq38OkpQb9cw49F2t2xH43BUwbL1vz
# G9DeVTvk2aIuktu6OHCuf2+FQqzq9Gqshv4700RyV/RyV3l0FwUa3cfDOZ7pCxBR
# CuCMX0+jb+XDQHCde2hugcio2KVfi2LlDLVK3Kr53oUjpBKHfCgUBrz+7lj5tYwn
# m9Ferz1GLCZ/re8ByNF1s+NhOSTkaVE95M6K/K3fXzcsbzDJwAIdIttlVDsYOXvl
# JA9tj/43XFIdLqEaOan4xGkppaqjLYNWFfqBDqMfzET1h4J5c5veH+EzU7Mmslnd
# bB9Oh8FN2S2viE0Ih+0JDz51KLi4xGJuDS6hUa+d1p1dmjo8bKVcoQcraxzqP+oT
# U+uh9Nqn9Wig1YbwDa79T9GHCcR69A1N5PHJCZPmiEmDQFRHiPuOR6YB65D/LGkd
# mw/PpO3HL0Me8zeJRmjcfJrv+UkuAb6TuO1l4V1NgEIFZHc4wLH89S29Iiwgw/jE
# Xee6eesoB6o1RIuUcUOFADzMnjE3PwWmDBJG5ZCSpcVaTw==
# SIG # End Windows Authenticode signature block