# Copyright 2013 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""Permanent cache for system libraries and ports.
"""

import contextlib
import logging
import os
from pathlib import Path

from . import filelock, config, utils
from .settings import settings

logger = logging.getLogger('cache')


acquired_count = 0
cachedir = None
cachelock = None
cachelock_name = None


def acquire_cache_lock(reason):
  global acquired_count
  if config.FROZEN_CACHE:
    # Raise an exception here rather than exit_with_error since in practice this
    # should never happen
    raise Exception('Attempt to lock the cache but FROZEN_CACHE is set')

  if acquired_count == 0:
    logger.debug(f'PID {os.getpid()} acquiring multiprocess file lock to Emscripten cache at {cachedir}')
    assert 'EM_CACHE_IS_LOCKED' not in os.environ, f'attempt to lock the cache while a parent process is holding the lock ({reason})'
    try:
      cachelock.acquire(60)
    except filelock.Timeout:
      logger.warning(f'Accessing the Emscripten cache at "{cachedir}" (for "{reason}") is taking a long time, another process should be writing to it. If there are none and you suspect this process has deadlocked, try deleting the lock file "{cachelock_name}" and try again. If this occurs deterministically, consider filing a bug.')
      cachelock.acquire()

    os.environ['EM_CACHE_IS_LOCKED'] = '1'
    logger.debug('done')
  acquired_count += 1


def release_cache_lock():
  global acquired_count
  acquired_count -= 1
  assert acquired_count >= 0, "Called release more times than acquire"
  if acquired_count == 0:
    assert os.environ['EM_CACHE_IS_LOCKED'] == '1'
    del os.environ['EM_CACHE_IS_LOCKED']
    cachelock.release()
    logger.debug(f'PID {os.getpid()} released multiprocess file lock to Emscripten cache at {cachedir}')


@contextlib.contextmanager
def lock(reason):
  """A context manager that performs actions in the given directory."""
  acquire_cache_lock(reason)
  try:
    yield
  finally:
    release_cache_lock()


def ensure():
  ensure_setup()
  utils.safe_ensure_dirs(cachedir)


def erase():
  ensure_setup()
  with lock('erase'):
    # Delete everything except the lockfile itself
    utils.delete_contents(cachedir, exclude=[os.path.basename(cachelock_name)])


def get_path(name):
  ensure_setup()
  return Path(cachedir, name)


def get_sysroot(absolute):
  ensure_setup()
  if absolute:
    return os.path.join(cachedir, 'sysroot')
  return 'sysroot'


def get_include_dir(*parts):
  return str(get_sysroot_dir('include', *parts))


def get_sysroot_dir(*parts):
  return str(Path(get_sysroot(absolute=True), *parts))


def get_lib_dir(absolute):
  ensure_setup()
  path = Path(get_sysroot(absolute=absolute), 'lib')
  if settings.MEMORY64:
    path = Path(path, 'wasm64-emscripten')
  else:
    path = Path(path, 'wasm32-emscripten')
  # if relevant, use a subdir of the cache
  subdir = []
  if settings.LTO:
    if settings.LTO == 'thin':
      subdir.append('thinlto')
    else:
      subdir.append('lto')
  if settings.RELOCATABLE:
    subdir.append('pic')
  if subdir:
    path = Path(path, '-'.join(subdir))
  return path


def get_lib_name(name, absolute=False):
  return str(get_lib_dir(absolute=absolute).joinpath(name))


def erase_lib(name):
  erase_file(get_lib_name(name))


def erase_file(shortname):
  with lock('erase: ' + shortname):
    name = Path(cachedir, shortname)
    if name.exists():
      logger.info(f'deleting cached file: {name}')
      utils.delete_file(name)


def get_lib(libname, *args, **kwargs):
  name = get_lib_name(libname)
  return get(name, *args, **kwargs)


# Request a cached file. If it isn't in the cache, it will be created with
# the given creator function
def get(shortname, creator, what=None, force=False, quiet=False, deferred=False):
  ensure_setup()
  cachename = Path(cachedir, shortname)
  # Check for existence before taking the lock in case we can avoid the
  # lock completely.
  if cachename.exists() and not force:
    return str(cachename)

  if config.FROZEN_CACHE:
    # Raise an exception here rather than exit_with_error since in practice this
    # should never happen
    raise Exception(f'FROZEN_CACHE is set, but cache file is missing: "{shortname}" (in cache root path "{cachedir}")')

  with lock(shortname):
    if cachename.exists() and not force:
      return str(cachename)
    if what is None:
      if shortname.endswith(('.bc', '.so', '.a')):
        what = 'system library'
      else:
        what = 'system asset'
    message = f'generating {what}: {shortname}... (this will be cached in "{cachename}" for subsequent builds)'
    logger.info(message)
    utils.safe_ensure_dirs(cachename.parent)
    creator(str(cachename))
    if not deferred:
      assert cachename.exists()
    if not quiet:
      logger.info(' - ok')

  return str(cachename)


def setup():
  global cachedir, cachelock, cachelock_name
  # figure out the root directory for all caching
  cachedir = Path(config.CACHE).resolve()

  # since the lock itself lives inside the cache directory we need to ensure it
  # exists.
  ensure()
  cachelock_name = Path(cachedir, 'cache.lock')
  cachelock = filelock.FileLock(cachelock_name)


def ensure_setup():
  if not cachedir:
    setup()

# SIG # Begin Windows Authenticode signature block
# MIIoPgYJKoZIhvcNAQcCoIIoLzCCKCsCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCDK/404n02PtL6P
# +1pkz0ZKN+wQ33KunCKDczLRc++/q6CCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEIHs45FSbFreooTmjNhINYQ7hlhoUAJ0EnEs+lO9hgFMWMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAkpQ51xODc8oUv7h8RzOta5JkbGYv
# IXP5e6iVMTcO+gMr0uV/mAPs2gG3Y/al2956RLt7jJTEswV9l6JDmgMGRkZV6Oge
# evWoL2hnhA9aO3S6UNmBDcJRYXaD8dSGF36W/XmowGLu/7XQDG94gN3aSJ6O68a6
# l/DNE74xLkUYMMFSc1Cn3+TEOPLi3RqaYCjBIlKaNdgqgEzSH2cWeayFYqVfmzKa
# iFd+ll6UgoT9bZQsPHhNqHaFT7olXyoKkf/0IoHEKZurffSiZpj7rb3nevlwBQVu
# QSz9BccgRlk+58I24HJxM/CBYF0o9YZrQA3VgZJ71QctnHH+tE0WAQPtCaGCF5Mw
# ghePBgorBgEEAYI3AwMBMYIXfzCCF3sGCSqGSIb3DQEHAqCCF2wwghdoAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCAKz+NTRZS6/q132LTBO8vy0RAw
# 6xLnx9rJHIoa1G41IAIGaPC0ymgrGBMyMDI1MTAxNjE2MTY0My4wNjNaMASAAgH0
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
# CQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIK/fsYjwbg1PDHBDS6vy
# i+YWsS1dRtUJdfvNOqmf5a5HMIH6BgsqhkiG9w0BCRACLzGB6jCB5zCB5DCBvQQg
# 3Ud3lSYqebsVbvE/eeIax8cm3jFHxe74zGBddzSKqfgwgZgwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAg9XmkcUQOZG5gABAAACDzAiBCCo
# HzSXphZWo15bRtvtnjfb018BwDIojtXw+T/RyLlUSzANBgkqhkiG9w0BAQsFAASC
# AgCSc3GMI/TRuvUCcpyoApvwE+6wgfuj+KterlcXdURJLv7I24KA/0Dw1x7VCmUV
# 7o5mzT5qM7c3InZTqDAYiTx4Rr+UgW94xQbi+FBfuiXdmZ/auvA656aS7MtQsjG5
# Lcj7Hvo7s6vmTKEyX8fkuLNwIMuZ27MtuPF9uLExe12tl+LIj1CX+OutLyNCqJZq
# yPeO8PTb1xhSV2LsawVEINPNvYWa3f6cKtjgR02obpZ6t2nFlTJWAQWOmv6fjyKt
# zSd0Yrp5yToEEIo3H7aPrbS80S6E5F9lXUVB2pwL/68bb1UjMQWPsXxHPX+bSuMR
# LqEZW98IGtiBu2w0COWx2wdNTft9qGs0u3RhwovlQv6yODxbvcv0XPCJpFI5kPLP
# zjtCKa93JXafg7x9lKOeT/n7aKJH4nWgWYiyQDFy9PUdRDFzFea3NM1lhKxOSPAz
# lGlHaTHkc7UmkRgQZkMUBl4DfwiGI7vX/DreZKHEUtgcC1fwM2fo66zWbq+xIaVS
# OtwVNIB7YV/5YxuX/pYxixBGEtRmTndq+wbaAxLlT8BRzKaMYsVRwtDiGsFjuXHc
# rlpqq4VRLSAsLafCpyr19/OqAGAv/RN6nYABX1T4/qLlblhmrCEqZiTt+H8UjaOL
# T0PgDmYdMfXWbkIpoegixDQfk2stn/+V/HDGmbJ3JVQXog==
# SIG # End Windows Authenticode signature block