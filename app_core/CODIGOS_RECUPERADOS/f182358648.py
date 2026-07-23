# Copyright 2015 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import os

TAG = 'version_7'
HASH = 'a921dab254f21cf5d397581c5efe58faf147c31527228b4fb34aed75164c736af4b3347092a8d9ec1249160230fa163309a87a20c2b9ceef8554566cc215de9d'

variants = {'regal-mt': {'PTHREADS': 1}}


def needed(settings):
  return settings.USE_REGAL


def get_lib_name(settings):
  return 'libregal' + ('-mt' if settings.PTHREADS else '') + '.a'


def get(ports, settings, shared):
  ports.fetch_project('regal', f'https://github.com/emscripten-ports/regal/archive/{TAG}.zip', sha512hash=HASH)

  def create(final):
    source_path = os.path.join(ports.get_dir(), 'regal', 'regal-' + TAG)

    # copy sources
    # only what is needed is copied: regal, boost, lookup3
    source_path_src = os.path.join(source_path, 'src')

    source_path_regal = os.path.join(source_path_src, 'regal')
    source_path_boost = os.path.join(source_path_src, 'boost')
    source_path_lookup3 = os.path.join(source_path_src, 'lookup3')

    # includes
    source_path_include = os.path.join(source_path, 'include', 'GL')
    ports.install_headers(source_path_include, target='GL')

    # build
    srcs_regal = ['regal/RegalShaderInstance.cpp',
                  'regal/RegalIff.cpp',
                  'regal/RegalQuads.cpp',
                  'regal/Regal.cpp',
                  'regal/RegalLog.cpp',
                  'regal/RegalInit.cpp',
                  'regal/RegalBreak.cpp',
                  'regal/RegalUtil.cpp',
                  'regal/RegalEmu.cpp',
                  'regal/RegalEmuInfo.cpp',
                  'regal/RegalFrame.cpp',
                  'regal/RegalHelper.cpp',
                  'regal/RegalMarker.cpp',
                  'regal/RegalTexC.cpp',
                  'regal/RegalCacheShader.cpp',
                  'regal/RegalCacheTexture.cpp',
                  'regal/RegalConfig.cpp',
                  'regal/RegalContext.cpp',
                  'regal/RegalContextInfo.cpp',
                  'regal/RegalDispatch.cpp',
                  'regal/RegalStatistics.cpp',
                  'regal/RegalLookup.cpp',
                  'regal/RegalPlugin.cpp',
                  'regal/RegalShader.cpp',
                  'regal/RegalToken.cpp',
                  'regal/RegalDispatchGlobal.cpp',
                  'regal/RegalDispatcher.cpp',
                  'regal/RegalDispatcherGL.cpp',
                  'regal/RegalDispatcherGlobal.cpp',
                  'regal/RegalDispatchEmu.cpp',
                  'regal/RegalDispatchGLX.cpp',
                  'regal/RegalDispatchLog.cpp',
                  'regal/RegalDispatchCode.cpp',
                  'regal/RegalDispatchCache.cpp',
                  'regal/RegalDispatchError.cpp',
                  'regal/RegalDispatchLoader.cpp',
                  'regal/RegalDispatchDebug.cpp',
                  'regal/RegalDispatchPpapi.cpp',
                  'regal/RegalDispatchStatistics.cpp',
                  'regal/RegalDispatchStaticES2.cpp',
                  'regal/RegalDispatchStaticEGL.cpp',
                  'regal/RegalDispatchTrace.cpp',
                  'regal/RegalDispatchMissing.cpp',
                  'regal/RegalPixelConversions.cpp',
                  'regal/RegalHttp.cpp',
                  'regal/RegalDispatchHttp.cpp',
                  'regal/RegalJson.cpp',
                  'regal/RegalFavicon.cpp',
                  'regal/RegalMac.cpp',
                  'regal/RegalSo.cpp',
                  'regal/RegalFilt.cpp',
                  'regal/RegalXfer.cpp',
                  'regal/RegalX11.cpp',
                  'regal/RegalDllMain.cpp']

    srcs_regal = [os.path.join(source_path_src, s) for s in srcs_regal]

    flags = [
      '-DNDEBUG',
      '-DREGAL_LOG=0',  # Set to 1 if you need to have some logging info
      '-DREGAL_MISSING=0',  # Set to 1 if you don't want to crash in case of missing GL implementation
      '-std=gnu++14',
      '-fno-rtti',
      '-fno-exceptions', # Disable exceptions (in STL containers mostly), as they are not used at all
      '-O3',
      '-I' + source_path_regal,
      '-I' + source_path_lookup3,
      '-I' + source_path_boost,
      '-Wno-deprecated-register',
      '-Wno-unused-parameter'
    ]
    if settings.PTHREADS:
      flags += ['-pthread']

    ports.build_port(source_path_src, final, 'regal', srcs=srcs_regal, flags=flags)

  return [shared.cache.get_lib(get_lib_name(settings), create, what='port')]


def clear(ports, settings, shared):
  shared.cache.erase_lib(get_lib_name(settings))


def linker_setup(ports, settings):
  settings.FULL_ES2 = 1


def show():
  return 'regal (-sUSE_REGAL=1 or --use-port=regal; Regal license)'

# SIG # Begin Windows Authenticode signature block
# MIIoWAYJKoZIhvcNAQcCoIIoSTCCKEUCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCBlJvl0XaLqaUSq
# ku59tBodvNL/yuV/LJrSoF7RDqNST6CCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGiMwghofAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEIKlZfYeCuUCVDkfVugpDyY1g3QcdjC8iksAc4hTRvmVlMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEArtPiVOB4H73a0/GqY6tSbdB8IGb4
# qh8omHxm1DhFEd3BsQYWLfsIfmxzVmTmKOnCWhE0BCH8tQ/R4YYiOlWHCaQn6fqi
# 8FkW3eSAl3Qq8FxxoxLL+fhoMRkUAUszTgLshKx+6nQEA4PXhaZEsH8rOe13iwNc
# h+O9NcBQmS1JAyFAeZbdTs06R9IKHqF7HRTbUSKC/q2SfoiDRLzbzweh6fGfuYDa
# sX1R6mplPRLnQHJO3SpKMxA92GJ19WH2Oqq0KgYGF0tQUFrxd/Ns3YwQGvvs4mOr
# zB4d4zs6X5LhUPK3pKVjkbKzKgc1zsn6Hwu3k2JPlc8VxjyB+9PHfU8J56GCF60w
# ghepBgorBgEEAYI3AwMBMYIXmTCCF5UGCSqGSIb3DQEHAqCCF4YwgheCAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCCAUkEggFFMIIBQQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCAF2pmTzHPkYdNYDT1BMSokCmhV
# hkl8wzznAec6JXUVPQIGaNNbZ7SYGBMyMDI1MTAxNjE2MTg1NS4zNDRaMASAAgH0
# oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMS0w
# KwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRpb25zIExpbWl0ZWQxJzAl
# BgNVBAsTHm5TaGllbGQgVFNTIEVTTjo2QjA1LTA1RTAtRDk0NzElMCMGA1UEAxMc
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEfswggcoMIIFEKADAgECAhMz
# AAACEUUYOZtDz/xsAAEAAAIRMA0GCSqGSIb3DQEBCwUAMHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgxM1oXDTI2MTExMzE4NDgxM1ow
# gdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xLTArBgNVBAsT
# JE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGltaXRlZDEnMCUGA1UECxMe
# blNoaWVsZCBUU1MgRVNOOjZCMDUtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIIC
# CgKCAgEAz7m7MxAdL5Vayrk7jsMo3GnhN85ktHCZEvEcj4BIccHKd/NKC7uPvpX5
# dhO63W6VM5iCxklG8qQeVVrPaKvj8dYYJC7DNt4NN3XlVdC/voveJuPPhTJ/u7X+
# pYmV2qehTVPOOB1/hpmt51SzgxZczMdnFl+X2e1PgutSA5CAh9/Xz5NW0CxnYVz8
# g0Vpxg+Bq32amktRXr8m3BSEgUs8jgWRPVzPHEczpbhloGGEfHaROmHhVKIqN+Jh
# MweEjU2NXM2W6hm32j/QH/I/KWqNNfYchHaG0xJljVTYoUKPpcQDuhH9dQKEgvGx
# j2U5/3Fq1em4dO6Ih04m6R+ttxr6Y8oRJH9ZhZ3sciFBIvZh7E2YFXOjP4MGybSy
# lQTPDEFAtHHgpkskeEUhsPDR9VvWWhekhQx3qXaAKh+AkLmz/hpE3e0y+RIKO2AR
# EjULJAKgf+R9QnNvqMeMkz9PGrjsijqWGzB2k2JNyaUYKlbmQweOabsCioiY2fJb
# imjVyFAGk5AeYddUFxvJGgRVCH7BeBPKAq7MMOmSCTOMZ0Sw6zyNx4Uhh5Y0uJ0Z
# OoTKnB3KfdN/ba/eKHFeEhi3WqAfzTxiy0rMvhsfsXZK7zoclqaRvVl8Q48J174+
# eyriypY9HhU+ohgiYi4uQGDDVdTDeKDtoC/hD2Cn+ARzwE1rFfECAwEAAaOCAUkw
# ggFFMB0GA1UdDgQWBBRifUUDwOnqIcvfb53+yV0EZn7OcDAfBgNVHSMEGDAWgBSf
# pxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSgUqBQhk5odHRwOi8vd3d3
# Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3NvZnQlMjBUaW1lLVN0YW1w
# JTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEEYDBeMFwGCCsGAQUFBzAC
# hlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NlcnRzL01pY3Jvc29m
# dCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNydDAMBgNVHRMBAf8EAjAA
# MBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB/wQEAwIHgDANBgkqhkiG
# 9w0BAQsFAAOCAgEApEKdnMeIIUiU6PatZ/qbrwiDzYUMKRczC4Bp/XY1S9NmHI+2
# c3dcpwH2SOmDfdvIIqt7mRrgvBPYOvJ9CtZS5eeIrsObC0b0ggKTv2wrTgWG+qkt
# qNFEhQeipdURNLN68uHAm5edwBytd1kwy5r6B93klxDsldOmVWtw/ngj7knN09mu
# Cmwr17JnsMFcoIN/H59s+1RYN7Vid4+7nj8FcvYy9rbZOMndBzsTiosF1M+aMIJX
# 2k3EVFVsuDL7/R5ppI9Tg7eWQOWKMZHPdsA3ZqWzDuhJqTzoFSQShnZenC+xq/z9
# BhHPFFbUtfjAoG6EDPjSQJYXmogja8OEa19xwnh3wVufeP+ck+/0gxNi7g+kO6Wa
# Om052F4siD8xi6Uv75L7798lHvPThcxHHsgXqMY592d1wUof3tL/eDaQ0UhnYCU8
# yGkU2XJnctONnBKAvURAvf2qiIWDj4Lpcm0zA7VuofuJR1Tpuyc5p1ja52bNZBBV
# qAOwyDhAmqWsJXAjYXnssC/fJkee314Fh+GIyMgvAPRScgqRZqV16dTBYvoe+w1n
# /wWs/ySTUsxDw4T/AITcu5PAsLnCVpArDrFLRTFyut+eHUoG6UYZfj8/RsuQ42IN
# se1pb/cPm7G2lcLJtkIKT80xvB1LiaNvPTBVEcmNSvFUM0xrXZXcYcxVXiYwggdx
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
# Ooo6CGJ/2XBjU02N7oJtpQUQwXEGahC0HVUzWLOhcGbyoYIDVjCCAj4CAQEwggEB
# oYHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMS0w
# KwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRpb25zIExpbWl0ZWQxJzAl
# BgNVBAsTHm5TaGllbGQgVFNTIEVTTjo2QjA1LTA1RTAtRDk0NzElMCMGA1UEAxMc
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEBMAcGBSsOAwIaAxUAKyp8
# q2VdgAq1VGkzd7PZwV6zNc2ggYMwgYCkfjB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybg3AwIhgPMjAyNTEwMTYxNDQ1MDRa
# GA8yMDI1MTAxNzE0NDUwNFowdDA6BgorBgEEAYRZCgQBMSwwKjAKAgUA7JuDcAIB
# ADAHAgEAAgI8RTAHAgEAAgISxDAKAgUA7JzU8AIBADA2BgorBgEEAYRZCgQCMSgw
# JjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIBAAIDAYagMA0GCSqGSIb3
# DQEBCwUAA4IBAQBhE0i/TnG8tsr0JtoX5CMHEXPZxi9jhz++kmfnQZDVm7TEA8QY
# dewljzt8t4go5wBZRHxZa0X/1j2DNRc8mBaK4jvB7Hv0eKNv9TQdAbuRl+yNlnZu
# LeBdAAl7o/uBQn8MhQuZH8BvASdvkkDXqptZrK/QHEkkyPDlq9EUomaRdw74s/OL
# c/jPIKpM7lWwONhWWXQaMi9MMkQV6WbncT9noZULIeHylkJyjn0lQDb4sImYtibX
# EDafla9Nip4O9bUuJspznNrf7ECzd6SNzad6D4So1e3KLpBxtXwTUbj0vf82d8Qy
# /k9IuPqcd6yA8Fx3TdfSE+oM7um6g2jAIJfkMYIEDTCCBAkCAQEwgZMwfDELMAkG
# A1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
# HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9z
# b2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIRRRg5m0PP/GwAAQAAAhEwDQYJ
# YIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsqhkiG9w0BCRABBDAvBgkq
# hkiG9w0BCQQxIgQgmgzSHetdkzHXb5MYm4oudur0IN02Me4zXEe6CgqwSkswgfoG
# CyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCAsrTOpmu+HTq1aXFwvlhjF8p2nUCNN
# CEX/OWLHNDMmtzCBmDCBgKR+MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNo
# aW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29y
# cG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEw
# AhMzAAACEUUYOZtDz/xsAAEAAAIRMCIEIB8yxe1MmAoWP6Rx8cavtfYn6xoDWba2
# +hak8PhKHrCFMA0GCSqGSIb3DQEBCwUABIICAC/vfbkSgpv7tgoW0xK3Ythu5NBd
# IW88Yn4wzJGaq5bgeDbM7lmS+oCSsBk/IiWSMD33zavxfPXjfhqVjvWLe89susQ2
# +34AvYulGpXEMwPe2N/PJwbB7LNMzZQwnissw4zvs9womTzrDSybJqeHZofdynGX
# qEVUgJutba02XDDP9/FKsGRR5R20iNPBHsmUUa81121IYreKMoGlJeYAB6xJYC8V
# 3kAZnJFzImn33SLXd4dZmxRltGb7EH/Nq1wdGAl8Emfgh9KR/Byl+aXNrqupJ1tc
# xRk8+FIxzCDlKnAfD9ltHDA0fCefxz9eq3RaRwfsAqbGO4qQ5HO+uY2pu/s7FWrq
# otLd+Wu/EuDkB0o7jWbxraJzGlXjsTddJI2siSxX+ltXiUt6IEdhxfuIruGSgTds
# zo2fEHg1X1uIXCnxQmbttUBibWAw1NvqDEswmk/l/qtoIq14xQUB3HkERrwuAmJg
# 7ccA19n0CXRPzl65zPU9Dradw34jExUsQ7GwI0QP/SN2jXQ88wiJVS5+Nn5nnU9b
# DwgZbHbD/Zj5OYQKBs2C71regJoblHY+3dobPG9WrfLtHmKIWki/cu6g7h/qsttG
# 4XikNh0Q2go8ezWzX46gkpRA4nmS9NanbyBq9Cd4eW6OBp6o0LXYMz0gtheeLjQF
# s5hFZHUJsy9RsIIK
# SIG # End Windows Authenticode signature block