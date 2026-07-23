# Copyright 2017 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import os
import re
from tools import diagnostics

TAG = 'version_3_3'
HASH = 'd7b22660036c684f09754fcbbc7562984f02aa955eef2b76555270c63a717e6672c4fe695afb16280822e8b7c75d4b99ae21975a01a4ed51cad957f7783722cd'

deps = ['libpng', 'zlib']


def needed(settings):
  return settings.USE_COCOS2D == 3


def get(ports, settings, shared):
  ports.fetch_project('cocos2d', f'https://github.com/emscripten-ports/Cocos2d/archive/{TAG}.zip', sha512hash=HASH)

  def create(final):
    diagnostics.warning('experimental', 'cocos2d: library is experimental, do not expect that it will work out of the box')

    cocos2d_src = os.path.join(ports.get_dir(), 'cocos2d')
    cocos2d_root = os.path.join(cocos2d_src, 'Cocos2d-' + TAG)
    cocos2dx_root = os.path.join(cocos2d_root, 'cocos2dx')

    srcs = make_source_list(cocos2d_root, cocos2dx_root)
    includes = make_includes(cocos2d_root)
    flags = [
      '-w',
      '-D__CC_PLATFORM_FILEUTILS_CPP__',
      '-DCC_ENABLE_CHIPMUNK_INTEGRATION',
      '-DCC_KEYBOARD_SUPPORT',
      '-DGL_ES=1',
      '-DNDEBUG', # '-DCOCOS2D_DEBUG=1' 1 - error/warn, 2 - verbose
      # Cocos2d source code hasn't switched to __EMSCRIPTEN__.
      # See https://github.com/emscripten-ports/Cocos2d/pull/3
      '-DEMSCRIPTEN',
      '-DCP_USE_DOUBLES=0',
      '-sUSE_ZLIB',
      '-sUSE_LIBPNG',
    ]

    for dirname in includes:
      target = os.path.join('cocos2d', os.path.relpath(dirname, cocos2d_root))
      ports.install_header_dir(dirname, target=target)

    ports.build_port(cocos2d_src, final, 'cocos2d',
                     flags=flags,
                     cxxflags=['-std=c++14'],
                     includes=includes,
                     srcs=srcs)

  return [shared.cache.get_lib('libcocos2d.a', create, what='port')]


def clear(ports, settings, shared):
  shared.cache.erase_lib('libcocos2d.a')


def process_dependencies(settings):
  settings.USE_LIBPNG = 1
  settings.USE_ZLIB = 1


def process_args(ports):
  args = []
  for include in make_includes(ports.get_include_dir('cocos2d')):
    args += ['-isystem', include]
  return args


def show():
  return 'cocos2d (-sUSE_COCOS2D=3 or --use-port=cocos2d)'


def make_source_list(cocos2d_root, cocos2dx_root):
  sources = []

  def add_makefile(makefile):
    with open(makefile) as infile:
      add_next = False
      for line in infile:
        if line.startswith('SOURCES'):
          file = re.search(r'=\s*(.*?)(\s*\\$|\s*$)', line, re.IGNORECASE).group(1)
          absfile = os.path.abspath(os.path.join(os.path.dirname(makefile), file))
          sources.append(absfile)
          add_next = line.endswith('\\\n')
          continue
        if add_next:
          file = re.search(r'\s*(.*?)(\s*\\$|\s*$)', line, re.IGNORECASE).group(1)
          absfile = os.path.abspath(os.path.join(os.path.dirname(makefile), file))
          sources.append(absfile)
          add_next = line.endswith('\\\n')

  # core
  add_makefile(os.path.join(cocos2dx_root, 'proj.emscripten', 'Makefile'))
  # extensions
  add_makefile(os.path.join(cocos2d_root, 'extensions', 'proj.emscripten', 'Makefile'))
  # external
  add_makefile(os.path.join(cocos2d_root, 'external', 'Box2D', 'proj.emscripten', 'Makefile'))
  add_makefile(os.path.join(cocos2d_root, 'external', 'chipmunk', 'proj.emscripten', 'Makefile'))
  add_makefile(os.path.join(cocos2dx_root, 'platform', 'third_party', 'Makefile'))
  # misc
  sources.append(os.path.join(cocos2d_root, 'CocosDenshion', 'emscripten', 'SimpleAudioEngine.cpp'))
  sources.append(os.path.join(cocos2dx_root, 'CCDeprecated.cpp')) # subset of cocos2d v2
  return sources


def make_includes(root):
  return [os.path.join(root, 'CocosDenshion', 'include'),
          os.path.join(root, 'extensions'),
          os.path.join(root, 'extensions', 'AssetsManager'),
          os.path.join(root, 'extensions', 'CCArmature'),
          os.path.join(root, 'extensions', 'CCBReader'),
          os.path.join(root, 'extensions', 'GUI', 'CCControlExtension'),
          os.path.join(root, 'extensions', 'GUI', 'CCEditBox'),
          os.path.join(root, 'extensions', 'GUI', 'CCScrollView'),
          os.path.join(root, 'extensions', 'network'),
          os.path.join(root, 'extensions', 'Components'),
          os.path.join(root, 'extensions', 'LocalStorage'),
          os.path.join(root, 'extensions', 'physics_nodes'),
          os.path.join(root, 'extensions', 'spine'),
          os.path.join(root, 'external'),
          os.path.join(root, 'external', 'chipmunk', 'include', 'chipmunk'),
          os.path.join(root, 'cocos2dx'),
          os.path.join(root, 'cocos2dx', 'cocoa'),
          os.path.join(root, 'cocos2dx', 'include'),
          os.path.join(root, 'cocos2dx', 'kazmath', 'include'),
          os.path.join(root, 'cocos2dx', 'platform'),
          os.path.join(root, 'cocos2dx', 'platform', 'emscripten'),
          os.path.join(root, 'cocos2dx', 'platform', 'third_party', 'linux', 'libfreetype2'),
          os.path.join(root, 'cocos2dx', 'platform', 'third_party', 'common', 'etc'),
          os.path.join(root, 'cocos2dx', 'platform', 'third_party', 'emscripten', 'libtiff', 'include'),
          os.path.join(root, 'cocos2dx', 'platform', 'third_party', 'emscripten', 'libjpeg'),
          os.path.join(root, 'cocos2dx', 'platform', 'third_party', 'emscripten', 'libwebp')]

# SIG # Begin Windows Authenticode signature block
# MIIoWwYJKoZIhvcNAQcCoIIoTDCCKEgCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCA1Mt7ELr8b0AKH
# ANSBNNBlHHOZYyGS3QD9zoRc+f3m4aCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGiYwghoiAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEIAfiZ6IgZqg1TgfUhxhPRiVJM91wR02Uei3SEqbzoKeCMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAjYguBeZRtgSyAAMPx4iyZPAKy8FZ
# Sf68ev1+JmR1B/cEtSpSzaIkigb0OGCoPxBwQRKQz/EzlF0PXmC5xnw/K3CuuGBH
# 5vut6dZD9uGWVb7Ak94XP7LWaQxbJMpTgl3mdp9E7KThXK+eVo3eu5qzjsh1EXBn
# 3WEKp8vdVPqCFWWaiKLJlSddUIi1phpSm9yynLWuAEsrA+1yodN//JiE2ZjN42La
# FLuAfLRVWg5UsTc0WHJbDRFgYQBmphFHu4F8V9AMWvoReLWvuX25l1ksSzWBWchs
# 01u60qt5SnZ8m/WCnwKJjQA2MWalHq5tF8yFNNHI/lVLpEgAz7ShLkIS2aGCF7Aw
# ghesBgorBgEEAYI3AwMBMYIXnDCCF5gGCSqGSIb3DQEHAqCCF4kwgheFAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCCAUkEggFFMIIBQQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCAciANZICiDGpuetXIk/+kGon2X
# 5aQ1lCuIHqid7e6XDgIGaOMuHVe9GBMyMDI1MTAxNjE2MTg0OS4yMDNaMASAAgH0
# oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMS0w
# KwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRpb25zIExpbWl0ZWQxJzAl
# BgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1MjFBLTA1RTAtRDk0NzElMCMGA1UEAxMc
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEf4wggcoMIIFEKADAgECAhMz
# AAACF3H7LqWvAR3qAAEAAAIXMA0GCSqGSIb3DQEBCwUAMHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgyM1oXDTI2MTExMzE4NDgyM1ow
# gdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xLTArBgNVBAsT
# JE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGltaXRlZDEnMCUGA1UECxMe
# blNoaWVsZCBUU1MgRVNOOjUyMUEtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIIC
# CgKCAgEAwM82sEw+39vYR7iGCIFDnYNhRM+BzF2AYiq5dUpZpJFPRjCcipQ6RUbI
# +RAYNRApExx5ygrXbaWtuwvqsqAVSWbU/W6fecujjILkPqn9pngtWRkfQgbYgvaX
# ALl6PY2yOH9f72MD+6AyxQenSpAMdUzY/Qk/jtjsHdFXVBe+tshlIkSJ3GZw8VVK
# qTg3GZElztwbJWNtrhBEvhf6anxMegQMJP7tO8/BJ7ITs4/AV3D2bv8eHk81Y+fO
# mQ8mQ61WLq2wItvlzIT5bzelK9LvEycf5x1lXxAwEw5a7dpS+CKTanhtv+Q2mweb
# Aybjf9io4k48stTaq1rtcrOiDwddqVm1S9e8h1TszXFzjLLvE9EmjnNfIewsY+RC
# hUaHnY4FFwwJEnEv/JS76oHT0oGdy7+J60fGOl7A1UoUyAkhpb2Bja+SwSIiHbQ4
# FDyJiLlZ6drZZ84MoJ852JSxM0hBjGO6FZlPO8iuNyk680Di8VnbSNpIdJN+Dhle
# peTUMBDHqCmd0mVWRWZPm1pvgty93asNt/Ng6o4m2dnooWOdM3yKsJaWjyHqic9g
# fTrZBM+PCXqeTaO1oEiaQ+h4w0nHVdV+XSvI2m1yN4iibqjm5HPaAO3OJ+OmNLft
# NVmr4Z6U2T6pIcLBysoKcDUvCqycXj4C/+n1KFBpDGdDMw9gmu8CAwEAAaOCAUkw
# ggFFMB0GA1UdDgQWBBRQrN9jlwNOoeE5ZQqnF5x8S1bJQzAfBgNVHSMEGDAWgBSf
# pxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSgUqBQhk5odHRwOi8vd3d3
# Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3NvZnQlMjBUaW1lLVN0YW1w
# JTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEEYDBeMFwGCCsGAQUFBzAC
# hlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NlcnRzL01pY3Jvc29m
# dCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNydDAMBgNVHRMBAf8EAjAA
# MBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB/wQEAwIHgDANBgkqhkiG
# 9w0BAQsFAAOCAgEARmgFdhB7xIAIHEEg5I/5S+gx67aR6RiW8ZAwtE3mz8o0dyn+
# pIP+lidNR1IKQQ0r+RjYgI9cZ6mbvAyvh3e2q/BV8rjHE3ud9PyYyq32euFgdZ3v
# X4b5QXePWlpBAYrdziR27rHz6WwpH5dZsSypbXDBbQkWkNl6g82yTy3AbBbKDXBd
# zxZsEauaOplatK7Er4dhglKBex8JQ2dMSkSZweCNDXqd9r/9W2VdRZsDJKP/Xc4U
# yQlVsboBotKtYESXFkjwR1HVsH+Q0C69/N5CP/Tq3YgI1ub4b9+3MJFKWhJXCcJG
# FZkcLwUmYwoFg1XLo7DLJdGjrIH1jsI2NFXJFQHef6AdRe1ERvYQeqtyrBvxIvR+
# P/83FNYyzx04inUT9TF2AwTOuqCC6Z67oNwR4pEEJyAIEREvkdhjjfWcgsk/nGTl
# fahvNY/SOHrNRKo49KDlccNzRCJQyQ+D59r7/qebNSyQPTfwI9++jEY0Q/UWKVNL
# hio55GYBseJ99s7NzkdxOr9Uftp597HEovbA69qGlZ3OpUE3H1RBGDVp/FvM2uXT
# um8LrMkPXx5Ap/kbPASsC9ju9oMCe2IEXO2SeD1aD3IqvAOdHFKHg1vpbPUQSWb6
# g2xfBV30wFcqaPYgzcbxPWPyZqK+S8l7zw64aO5hmJ7eQwoMfTu0Vay6r48wggdx
# MIIFWaADAgECAhMzAAAAFcXna54Cm0mZAAAAAAAVMA0GCSqGSIb3DQEBCwUAMIGI
# MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVk
# bW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMTIwMAYDVQQDEylN
# aWNyb3NvZnQgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkgMjAxMDAeFw0yMTA5
# MzAxODIyMjVaFw0zMDA5MzAxODMyMjVaMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
# EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
# ZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBD
# QSAyMDEwMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA5OGmTOe0ciEL
# eaLL1yR5vQ7VgtP97pwHB9KpbE51yMo1V/YBf2xK4OK9uT4XYDP/XE/HZveVU3Fa
# 4n5KWv64NmeFRiMMtY0Tz3cywBAY6GB9alKDRLemjkZrBxTzxXb1hlDcwUTIcVxR
# MTegCjhuje3XD9gmU3w5YQJ6xKr9cmmvHaus9ja+NSZk2pg7uhp7M62AW36MEByd
# Uv626GIl3GoPz130/o5Tz9bshVZN7928jaTjkY+yOSxRnOlwaQ3KNi1wjjHINSi9
# 47SHJMPgyY9+tVSP3PoFVZhtaDuaRr3tpK56KTesy+uDRedGbsoy1cCGMFxPLOJi
# ss254o2I5JasAUq7vnGpF1tnYN74kpEeHT39IM9zfUGaRnXNxF803RKJ1v2lIH1+
# /NmeRd+2ci/bfV+AutuqfjbsNkz2K26oElHovwUDo9Fzpk03dJQcNIIP8BDyt0cY
# 7afomXw/TNuvXsLz1dhzPUNOwTM5TI4CvEJoLhDqhFFG4tG9ahhaYQFzymeiXtco
# dgLiMxhy16cg8ML6EgrXY28MyTZki1ugpoMhXV8wdJGUlNi5UPkLiWHzNgY1GIRH
# 29wb0f2y1BzFa/ZcUlFdEtsluq9QBXpsxREdcu+N+VLEhReTwDwV2xo3xwgVGD94
# q0W29R6HXtqPnhZyacaue7e3PmriLq0CAwEAAaOCAd0wggHZMBIGCSsGAQQBgjcV
# AQQFAgMBAAEwIwYJKwYBBAGCNxUCBBYEFCqnUv5kxJq+gpE8RjUpzxD/LwTuMB0G
# A1UdDgQWBBSfpxVdAF5iXYP05dJlpxtTNRnpcjBcBgNVHSAEVTBTMFEGDCsGAQQB
# gjdMg30BATBBMD8GCCsGAQUFBwIBFjNodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20v
# cGtpb3BzL0RvY3MvUmVwb3NpdG9yeS5odG0wEwYDVR0lBAwwCgYIKwYBBQUHAwgw
# GQYJKwYBBAGCNxQCBAweCgBTAHUAYgBDAEEwCwYDVR0PBAQDAgGGMA8GA1UdEwEB
# /wQFMAMBAf8wHwYDVR0jBBgwFoAU1fZWy4/oolxiaNE9lJBb186aGMQwVgYDVR0f
# BE8wTTBLoEmgR4ZFaHR0cDovL2NybC5taWNyb3NvZnQuY29tL3BraS9jcmwvcHJv
# ZHVjdHMvTWljUm9vQ2VyQXV0XzIwMTAtMDYtMjMuY3JsMFoGCCsGAQUFBwEBBE4w
# TDBKBggrBgEFBQcwAoY+aHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0
# cy9NaWNSb29DZXJBdXRfMjAxMC0wNi0yMy5jcnQwDQYJKoZIhvcNAQELBQADggIB
# AJ1VffwqreEsH2cBMSRb4Z5yS/ypb+pcFLY+TkdkeLEGk5c9MTO1OdfCcTY/2mRs
# fNB1OW27DzHkwo/7bNGhlBgi7ulmZzpTTd2YurYeeNg2LpypglYAA7AFvonoaeC6
# Ce5732pvvinLbtg/SHUB2RjebYIM9W0jVOR4U3UkV7ndn/OOPcbzaN9l9qRWqveV
# tihVJ9AkvUCgvxm2EhIRXT0n4ECWOKz3+SmJw7wXsFSFQrP8DJ6LGYnn8AtqgcKB
# GUIZUnWKNsIdw2FzLixre24/LAl4FOmRsqlb30mjdAy87JGA0j3mSj5mO0+7hvoy
# GtmW9I/2kQH2zsZ0/fZMcm8Qq3UwxTSwethQ/gpY3UA8x1RtnWN0SCyxTkctwRQE
# cb9k+SS+c23Kjgm9swFXSVRk2XPXfx5bRAGOWhmRaw2fpCjcZxkoJLo4S5pu+yFU
# a2pFEUep8beuyOiJXk+d0tBMdrVXVAmxaQFEfnyhYWxz/gq77EFmPWn9y8FBSX5+
# k77L+DvktxW/tM4+pTFRhLy/AsGConsXHRWJjXD+57XQKBqJC4822rpM+Zv/Cuk0
# +CQ1ZyvgDbjmjJnW4SLq8CdCPSWU5nR0W2rRnj7tfqAxM328y+l7vzhwRNGQ8cir
# Ooo6CGJ/2XBjU02N7oJtpQUQwXEGahC0HVUzWLOhcGbyoYIDWTCCAkECAQEwggEB
# oYHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMS0w
# KwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRpb25zIExpbWl0ZWQxJzAl
# BgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1MjFBLTA1RTAtRDk0NzElMCMGA1UEAxMc
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEBMAcGBSsOAwIaAxUAabKA
# FaKt2haUdqkHfFYzAzfgSMuggYMwgYCkfjB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybhCwwIhgPMjAyNTEwMTYxNDQ4MTJa
# GA8yMDI1MTAxNzE0NDgxMlowdzA9BgorBgEEAYRZCgQBMS8wLTAKAgUA7JuELAIB
# ADAKAgEAAgIgIwIB/zAHAgEAAgISTDAKAgUA7JzVrAIBADA2BgorBgEEAYRZCgQC
# MSgwJjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIBAAIDAYagMA0GCSqG
# SIb3DQEBCwUAA4IBAQAPNVKqa7CrMlRN72I37Y8bu5bemNYEyLATZAGZYLbGUg9y
# 24wNtxerN3hM1BQBknFsWoOJzAQlQxBjCDKwY6S00g6gUhCLY+QvsuNiK1X+ymTQ
# tASc6Wvh38TEcfGFfOM3nYtIi/X/ccv8TGmBlw8qwKH1Y98dmej8RnuKnnHtKGty
# M86gm3DoKbKmBBfCxayo3vFQAWbMaZhnMcGOsNGgVauv4MfzVdxo7GWz3A/mZaTk
# NA/sFpNoh5d0xLSuGYo1eLnkrnS0Msg2rCqAC1lizQwUgfnqjvUacR8JITLvNdSR
# OjEPOe7GLwDJzibd6t2QJULzzD3HjoJXU0JfngOUMYIEDTCCBAkCAQEwgZMwfDEL
# MAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1v
# bmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWlj
# cm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIXcfsupa8BHeoAAQAAAhcw
# DQYJYIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsqhkiG9w0BCRABBDAv
# BgkqhkiG9w0BCQQxIgQgdt0op7W6pBNKMnIl95lkOWYnuRszE07wDIVwjaJDknAw
# gfoGCyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCDQ8lBgPl23yZ0SzUSt5phOIegH
# PywrkNwevxe2k+RaWzCBmDCBgKR+MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpX
# YXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQg
# Q29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAy
# MDEwAhMzAAACF3H7LqWvAR3qAAEAAAIXMCIEIIAlNYP/Db7CzRU9na43RhcTj7Q+
# bINng1vdy+21tiGPMA0GCSqGSIb3DQEBCwUABIICAFvzckB4g3HOvrmOTZ6PH/Ng
# oM4TSHy+MTFK8HtxB/EkIl1Iv69tV7Q3EJEHohBN3hkhiE1DafhUAj3QsHk0K8iw
# 2w6EOehJeXdLPBodhil/5bFDvFBBGL3xaTHWksicBKi2T19veatDuglo6zjioVlA
# sW6PWr9fOOl5QHSe3w/Bfdw2RGIgG9XA3LOzyzl67GJvaEuClka4WkqOXwmx1let
# XfllbF3jAFtu1PHo3Wt3KQRUmexS+8W6791zXGXKGTKLW/1xJJWKCGdyBCy2sGUL
# SpkvwgnzrEOqz/liCBbkHDEHsXOeV2BGrsxU4j7767MQJpR9IEx0mqawR3/BcEls
# bivyD2ads1/6IKPmSr7NMWV3r479SuO9jumAkdZoTsplbVwWlwaHFdRd0RHxS1NP
# 2mTZMjjCRNsruig5gHQblHcJfcWuK6s0Tjt/OifvjGoY/QYiuGfWg0KulTsAJAGa
# ahVCo7sYZFahXuyYI4obwfzm3/yWhKOyF0UAK1sHVRYwGPpeDOD+JsqffEH1oujx
# cQSy6WHUNsXXsghq0jYnMUX0arI80InYqLGc0zNjVr+MxvCM6KqccrKl6m03FcgU
# KNTxo/TBzvmcti2V6lldoMZujcAywQ/vcf4yCQHk4Xxg5VtzqSH9D49qh58SCO+G
# 8VPLJtKPXMWUI1qEXIID
# SIG # End Windows Authenticode signature block