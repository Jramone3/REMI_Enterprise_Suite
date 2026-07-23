# Copyright 2021 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import os

TAG = '11022021'
HASH = 'f770031ad6c2152cbed8c8eab8edf2be1d27f9e74bc255a9930c17019944ee5fdda5308ea992c66a78af9fe1d8dca090f6c956910ce323f8728247c10e44036b'


def needed(settings):
  return settings.USE_MODPLUG


def get(ports, settings, shared):
  ports.fetch_project('libmodplug', f'https://github.com/jancc/libmodplug/archive/v{TAG}.zip', sha512hash=HASH)

  def create(final):
    source_path = os.path.join(ports.get_dir(), 'libmodplug', 'libmodplug-' + TAG)
    src_dir = os.path.join(source_path, 'src')
    libmodplug_path = os.path.join(src_dir, 'libmodplug')

    ports.write_file(os.path.join(source_path, 'config.h'), config_h)

    flags = [
      '-Wno-deprecated-register',
      '-DOPT_GENERIC',
      '-DREAL_IS_FLOAT',
      '-DHAVE_CONFIG_H',
      '-DSYM_VISIBILITY',
      '-std=gnu++14',
      '-O2',
      '-fno-exceptions',
      '-ffast-math',
      '-fno-common',
      '-fvisibility=hidden',
      '-I' + source_path,
      '-I' + libmodplug_path,
    ]
    srcs = [
      os.path.join(src_dir, 'fastmix.cpp'),
      os.path.join(src_dir, 'load_669.cpp'),
      os.path.join(src_dir, 'load_abc.cpp'),
      os.path.join(src_dir, 'load_amf.cpp'),
      os.path.join(src_dir, 'load_ams.cpp'),
      os.path.join(src_dir, 'load_dbm.cpp'),
      os.path.join(src_dir, 'load_dmf.cpp'),
      os.path.join(src_dir, 'load_dsm.cpp'),
      os.path.join(src_dir, 'load_far.cpp'),
      os.path.join(src_dir, 'load_it.cpp'),
      os.path.join(src_dir, 'load_j2b.cpp'),
      os.path.join(src_dir, 'load_mdl.cpp'),
      os.path.join(src_dir, 'load_med.cpp'),
      os.path.join(src_dir, 'load_mid.cpp'),
      os.path.join(src_dir, 'load_mod.cpp'),
      os.path.join(src_dir, 'load_mt2.cpp'),
      os.path.join(src_dir, 'load_mtm.cpp'),
      os.path.join(src_dir, 'load_okt.cpp'),
      os.path.join(src_dir, 'load_pat.cpp'),
      os.path.join(src_dir, 'load_psm.cpp'),
      os.path.join(src_dir, 'load_ptm.cpp'),
      os.path.join(src_dir, 'load_s3m.cpp'),
      os.path.join(src_dir, 'load_stm.cpp'),
      os.path.join(src_dir, 'load_ult.cpp'),
      os.path.join(src_dir, 'load_umx.cpp'),
      os.path.join(src_dir, 'load_wav.cpp'),
      os.path.join(src_dir, 'load_xm.cpp'),
      os.path.join(src_dir, 'mmcmp.cpp'),
      os.path.join(src_dir, 'modplug.cpp'),
      os.path.join(src_dir, 'snd_dsp.cpp'),
      os.path.join(src_dir, 'sndfile.cpp'),
      os.path.join(src_dir, 'snd_flt.cpp'),
      os.path.join(src_dir, 'snd_fx.cpp'),
      os.path.join(src_dir, 'sndmix.cpp'),
    ]

    ports.build_port(source_path, final, 'libmodplug', flags=flags, srcs=srcs)

    ports.install_headers(libmodplug_path, pattern="*.h", target='libmodplug')
    ports.install_headers(src_dir, pattern="modplug.h", target='libmodplug')

  return [shared.cache.get_lib('libmodplug.a', create, what='port')]


def clear(ports, settings, shared):
  shared.cache.erase_lib('libmodplug.a')


def show():
  return 'libmodplug (-sUSE_MODPLUG=1 or --use-port=libmodplug; public domain)'


config_h = '''/* src/config.h.  Generated from config.h.in by configure.  */
/* src/config.h.in.  Generated from configure.ac by autoheader.  */

/* Define if building universal (internal helper macro) */
/* #undef AC_APPLE_UNIVERSAL_BUILD */

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the <malloc.h> header file. */
#define HAVE_MALLOC_H 1

/* Define to 1 if you have the `setenv' function. */
#define HAVE_SETENV 1

/* Define to 1 if you have the `sinf' function. */
#define HAVE_SINF 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdio.h> header file. */
#define HAVE_STDIO_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to the sub-directory where libtool stores uninstalled libraries. */
#define LT_OBJDIR ".libs/"

/* Name of package */
#define PACKAGE "libmodplug"

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT ""

/* Define to the full name of this package. */
#define PACKAGE_NAME "libmodplug"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "libmodplug 0.8.9.0"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "libmodplug"

/* Define to the home page for this package. */
#define PACKAGE_URL ""

/* Define to the version of this package. */
#define PACKAGE_VERSION "0.8.9.0"

/* Define to 1 if all of the C90 standard headers exist (not just the ones
   required in a freestanding environment). This macro is provided for
   backward compatibility; new code need not use it. */
#define STDC_HEADERS 1

/* Version number of package */
#define VERSION "0.8.9.0"

/* Define WORDS_BIGENDIAN to 1 if your processor stores words with the most
   significant byte first (like Motorola and SPARC, unlike Intel). */
#if defined AC_APPLE_UNIVERSAL_BUILD
# if defined __BIG_ENDIAN__
#  define WORDS_BIGENDIAN 1
# endif
#else
# ifndef WORDS_BIGENDIAN
/* #  undef WORDS_BIGENDIAN */
# endif
#endif

/* Define for Solaris 2.5.1 so the uint32_t typedef from <sys/synch.h>,
   <pthread.h>, or <semaphore.h> is not used. If the typedef were allowed, the
   #define below would cause a syntax error. */
/* #undef _UINT32_T */

/* Define for Solaris 2.5.1 so the uint64_t typedef from <sys/synch.h>,
   <pthread.h>, or <semaphore.h> is not used. If the typedef were allowed, the
   #define below would cause a syntax error. */
/* #undef _UINT64_T */

/* Define for Solaris 2.5.1 so the uint8_t typedef from <sys/synch.h>,
   <pthread.h>, or <semaphore.h> is not used. If the typedef were allowed, the
   #define below would cause a syntax error. */
/* #undef _UINT8_T */

/* Define to the type of a signed integer type of width exactly 16 bits if
   such a type exists and the standard includes do not define it. */
/* #undef int16_t */

/* Define to the type of a signed integer type of width exactly 32 bits if
   such a type exists and the standard includes do not define it. */
/* #undef int32_t */

/* Define to the type of a signed integer type of width exactly 64 bits if
   such a type exists and the standard includes do not define it. */
/* #undef int64_t */

/* Define to the type of a signed integer type of width exactly 8 bits if such
   a type exists and the standard includes do not define it. */
/* #undef int8_t */

/* Define to the type of an unsigned integer type of width exactly 16 bits if
   such a type exists and the standard includes do not define it. */
/* #undef uint16_t */

/* Define to the type of an unsigned integer type of width exactly 32 bits if
   such a type exists and the standard includes do not define it. */
/* #undef uint32_t */

/* Define to the type of an unsigned integer type of width exactly 64 bits if
   such a type exists and the standard includes do not define it. */
/* #undef uint64_t */

/* Define to the type of an unsigned integer type of width exactly 8 bits if
   such a type exists and the standard includes do not define it. */
/* #undef uint8_t */
'''

# SIG # Begin Windows Authenticode signature block
# MIIoPwYJKoZIhvcNAQcCoIIoMDCCKCwCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAnAU0HEgEx/+fi
# 2p0CFkmqBaqVX+8+rRcU9BXFzJcHoKCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEIPwkwRazPW6pogfF1TF/RY6F1DMkca3hJ08LsURIJJjuMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAolpNHA1JPeNH4K8L0B+6gyJWkIld
# dl4kCID5c2qVm2h6JyU2qipy+Z3GDugwm2PzNLoA91EsLeyFQcSjoOGpdA5djfpN
# zxJa/LzfL9b2soPsA937rMazE1PQuBZkakTdSIVpdIROn9GzdtMSXHzcwrpxx3j1
# jaAOTDcAPU11CcJcCjvqkLkIvB2qC1f6VxchmVefoFVebYnxwF+oC0+tnqb1N3Dl
# ccvQTsAHQsR0g0cScCIDjfNTLHRPyJE16/jkJqIH2/g4tHY0ATfKCWDcVeh9rj1n
# zL0+QU7JTNYR7GZjj2azEAG8ntjch0RkmCihQ/DT14NpLpQ1U3fbgNVwmqGCF5Qw
# gheQBgorBgEEAYI3AwMBMYIXgDCCF3wGCSqGSIb3DQEHAqCCF20wghdpAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCDItJEXwe1iYS75rAN+MKf3Dsu6
# BgZctipl5UlikQ/DoQIGaPBuGIF6GBMyMDI1MTAxNjE2MTcyMy41MzNaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046ODkwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHqMIIHIDCCBQigAwIBAgITMwAAAg4syyh9
# lSB1YwABAAACDjANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQzMDNaFw0yNjA0MjIxOTQzMDNaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# ODkwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCs5t7iRtXt0hbe
# o9ME78ZYjIo3saQuWMBFQ7X4s9vooYRABTOf2poTHatx+EwnBUGB1V2t/E6MwsQN
# mY5XpM/75aCrZdxAnrV9o4Tu5sBepbbfehsrOWRBIGoJE6PtWod1CrFehm1diz3j
# Y3H8iFrh7nqefniZ1SnbcWPMyNIxuGFzpQiDA+E5YS33meMqaXwhdb01Cluymh/3
# EKvknj4dIpQZEWOPM3jxbRVAYN5J2tOrYkJcdDx0l02V/NYd1qkvUBgPxrKviq5k
# z7E6AbOifCDSMBgcn/X7RQw630Qkzqhp0kDU2qei/ao9IHmuuReXEjnjpgTsr4Ab
# 33ICAKMYxOQe+n5wqEVcE9OTyhmWZJS5AnWUTniok4mgwONBWQ1DLOGFkZwXT334
# IPCqd4/3/Ld/ItizistyUZYsml/C4ZhdALbvfYwzv31Oxf8NTmV5IGxWdHnk2Hhh
# 4bnzTKosEaDrJvQMiQ+loojM7f5bgdyBBnYQBm5+/iJsxw8k227zF2jbNI+Ows8H
# LeZGt8t6uJ2eVjND1B0YtgsBP0csBlnnI+4+dvLYRt0cAqw6PiYSz5FSZcbpi0xd
# AH/jd3dzyGArbyLuo69HugfGEEb/sM07rcoP1o3cZ8eWMb4+MIB8euOb5DVPDnEc
# Fi4NDukYM91g1Dt/qIek+rtE88VS8QIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFIVx
# RGlSEZE+1ESK6UGI7YNcEIjbMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQB14L2T
# L+L8OXLxnGSal2h30mZ7FsBFooiYkUVOY05F9pnwPTVufEDGWEpNNy2OfaUHWIOo
# Q/9/rjwO0hS2SpB0BzMAk2gyz92NGWOpWbpBdMvrrRDpiWZi/uLS4ZGdRn3P2Dcc
# YmlkNP+vaRAXvnv+mp27KgI79mJ9hGyCQbvtMIjkbYoLqK7sF7Wahn9rLjX1y5QJ
# L4lvEy3QmA9KRBj56cEv/lAvzDq7eSiqRq/pCyqyc8uzmQ8SeKWyWu6DjUA9vi84
# QsmLjqPGCnH4cPyg+t95RpW+73snhew1iCV+wXu2RxMnWg7EsD5eLkJHLszUIPd+
# XClD+FTvV03GfrDDfk+45flH/eKRZc3MUZtnhLJjPwv3KoKDScW4iV6SbCRycYPk
# qoWBrHf7SvDA7GrH2UOtz1Wa1k27sdZgpG6/c9CqKI8CX5vgaa+A7oYHb4ZBj7S8
# u8sgxwWK7HgWDRByOH3CiJu4LJ8h3TiRkRArmHRp0lbNf1iAKuL886IKE912v0yq
# 55t8jMxjBU7uoLsrYVIoKkzh+sAkgkpGOoZL14+dlxVM91Bavza4kODTUlwzb+Sp
# XsSqVx8nuB6qhUy7pqpgww1q4SNhAxFnFxsxiTlaoL75GNxPR605lJ2WXehtEi7/
# +YfJqvH+vnqcpqCjyQ9hNaVzuOEHX4MyuqcjwjCCB3EwggVZoAMCAQICEzMAAAAV
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
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjg5
# MDAtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQBK6HY/ZWLnOcMEQsjkDAoB/JZWCKCBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JuVSzAiGA8yMDI1MTAxNjE2MDExNVoYDzIwMjUxMDE3MTYwMTE1WjB0MDoGCisG
# AQQBhFkKBAExLDAqMAoCBQDsm5VLAgEAMAcCAQACAjAeMAcCAQACAhMFMAoCBQDs
# nObLAgEAMDYGCisGAQQBhFkKBAIxKDAmMAwGCisGAQQBhFkKAwKgCjAIAgEAAgMH
# oSChCjAIAgEAAgMBhqAwDQYJKoZIhvcNAQELBQADggEBANofmdmhguDHR7l0VGSa
# 4KXdAtoRJTuXtU0cr3IBOp4OwhHjU9fpQ1uqWxNOrN08UB1pMaWMHJevmTtMYkcw
# gEHD8IffI2JeEs7O4IbyKwSv5dAvfM9qVEDPJ+QJemKVytCMlk4XpKy0APagpSOl
# 6HAyFHBY/8X0AfQ9uXs/89GHLx5thdEuDOOLz8qTqntGnH/FSyv1uFD2pFuoU+YQ
# A902fmW1iSwUw1vAgryfskRZiod67wXAeHTTVx6WO1Q3bJre+z43lhY8+1qihprF
# 2gf37yitGDoWeiY7Ryx3tHTg4tPRhFeTx/xsBkcWRQakDFOoqgIhVqzlIE/zYrOb
# I6cxggQNMIIECQIBATCBkzB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGlu
# Z3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBv
# cmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAIT
# MwAAAg4syyh9lSB1YwABAAACDjANBglghkgBZQMEAgEFAKCCAUowGgYJKoZIhvcN
# AQkDMQ0GCyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCBP/+6C2BhX2CkZmdew
# cSjwzYK0AOT4GHZhnRvHEWnMpjCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQwgb0E
# IAF0HXMl8OmBkK267mxobKSihwOdP0eUNXQMypPzTxKGMIGYMIGApH4wfDELMAkG
# A1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
# HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9z
# b2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIOLMsofZUgdWMAAQAAAg4wIgQg
# SNwmTSZypkztZ8VF1ayx1mijiBNJwVd5MFABhYwm0PwwDQYJKoZIhvcNAQELBQAE
# ggIAm0ydHs2x/eqw6JDE8bapF73IlPQ2INHWCU5vIytRW6v2EGN2lx91KE2dg+mj
# M9Fg6wR5loS7fyPHLYxbyabN5XH0g/SnLky6+J3DdY+gDxoEhmDly6D8VZOyNhKY
# oFf6/Yz1pfnd5Ym7X94wpr+/w51eUnYCmjZiumVj/n5tShEiGBxN3nheh60JL0I1
# hLVsd6SgWnTPOa5J25H7Jw6b0XIMPWIoqiwl0AxPwHjZb8rbI8I2Y1hqSQ2OQwhv
# 5mCze/G5wz2d0IGfY2kh/VuvQ6TJLtQsMZS0HUNM0HXA1LHbeUsimfxZF4TunV2d
# p7xY2zhfJb9V6TjPUhBFrGFrA3QixGyKVwDbgk0kIqo2DVaZI9hLGcTvYUVgguw/
# jztQd7NdU54gYeikHGncu4b8CEG+LUbzXLpvxXV8zpZ8FnGkOGIlZsi6NGbDBTxs
# Kfb/E6VZqMxiyNyxt0A4ti0sPM1u7oxe6Dd3wWK1GISviVNuW/6xFsjQ/uBNrFY5
# oDHyW0dgh4N0+OCrEGTdJw6//o8XjmsB1KH0yJ93B3FpDYHP4IzGUpC82UbDo2Z5
# fpoRzyvMDG/d0MfTLmYzlIUyyLRJYSMZwUL4a1W9NC2G/q4KkwHi0dcPxYy0wc/m
# ac3zLfJYvfG6usg/1qMgq3mqjzOrioHOmTG+19Fq6frI9UE=
# SIG # End Windows Authenticode signature block