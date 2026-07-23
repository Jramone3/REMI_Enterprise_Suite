#!/usr/bin/env python3
# Copyright 2014 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""Tool to manage building of system libraries and ports.

In general emcc will build them automatically on demand, so you do not
strictly need to use this tool, but it gives you more control over the
process (in particular, if emcc does this automatically, and you are
running multiple build commands in parallel, confusion can occur).
"""

import argparse
import fnmatch
import logging
import sys
import time
from contextlib import contextmanager

from tools import cache
from tools import shared
from tools import system_libs
from tools import ports
from tools import utils
from tools.settings import settings
from tools.system_libs import USE_NINJA


# Minimal subset of targets used by CI systems to build enough to useful
MINIMAL_TASKS = [
    'libbulkmemory',
    'libcompiler_rt',
    'libcompiler_rt-wasm-sjlj',
    'libc',
    'libc-debug',
    'libc_optz',
    'libc_optz-debug',
    'libc++abi',
    'libc++abi-except',
    'libc++abi-noexcept',
    'libc++abi-debug',
    'libc++abi-debug-except',
    'libc++abi-debug-noexcept',
    'libc++',
    'libc++-except',
    'libc++-noexcept',
    'libal',
    'libdlmalloc',
    'libdlmalloc-tracing',
    'libdlmalloc-debug',
    'libembind',
    'libembind-rtti',
    'libemmalloc',
    'libemmalloc-debug',
    'libemmalloc-memvalidate',
    'libemmalloc-verbose',
    'libemmalloc-memvalidate-verbose',
    'libmimalloc',
    'libmimalloc-mt',
    'libGL',
    'libGL-getprocaddr',
    'libhtml5',
    'libsockets',
    'libstubs',
    'libstubs-debug',
    'libstandalonewasm-nocatch',
    'crt1',
    'crt1_proxy_main',
    'crtbegin',
    'libunwind-except',
    'libnoexit',
# dotnet change, remove it, so that we don't download the sqlite3 source code in emsdk
#    'sqlite3',
#    'sqlite3-mt',
    'libwebgpu',
    'libwebgpu_cpp',
]

# Additional tasks on top of MINIMAL_TASKS that are necessary for PIC testing on
# CI (which has slightly more tests than other modes that want to use MINIMAL)
MINIMAL_PIC_TASKS = MINIMAL_TASKS + [
    'libcompiler_rt-mt',
    'libc-mt',
    'libc-mt-debug',
    'libc_optz-mt',
    'libc_optz-mt-debug',
    'libc++abi-mt',
    'libc++abi-mt-noexcept',
    'libc++abi-debug-mt',
    'libc++abi-debug-mt-noexcept',
    'libc++-mt',
    'libc++-mt-noexcept',
    'libdlmalloc-mt',
    'libGL-emu',
    'libGL-emu-webgl2-getprocaddr',
    'libGL-mt-getprocaddr',
    'libGL-mt-emu',
    'libGL-mt-emu-webgl2-getprocaddr',
    'libGL-mt-emu-webgl2-ofb-getprocaddr',
    'libsockets_proxy',
    'libsockets-mt',
    'crtbegin',
    'libsanitizer_common_rt',
    'libubsan_rt',
    'libwasm_workers_stub-debug',
    'libfetch',
    'libfetch-mt',
    'libwasmfs',
    'libwasmfs-debug',
    'libwasmfs_no_fs',
    'giflib',
]

PORTS = sorted(list(ports.ports_by_name.keys()) + list(ports.port_variants.keys()))

temp_files = shared.get_temp_files()
logger = logging.getLogger('embuilder')
legacy_prefixes = {
  'libgl': 'libGL',
}


def get_help():
  all_tasks = get_all_tasks()
  all_tasks.sort()
  return '''
Available targets:

  build / clear
        %s

Issuing 'embuilder build ALL' causes each task to be built.
''' % '\n        '.join(all_tasks)


@contextmanager
def get_port_variant(name):
  if name in ports.port_variants:
    name, extra_settings = ports.port_variants[name]
    old_settings = settings.dict().copy()
    for key, value in extra_settings.items():
      setattr(settings, key, value)
  else:
    old_settings = None

  yield name

  if old_settings:
    settings.dict().update(old_settings)


def clear_port(port_name):
  with get_port_variant(port_name) as port_name:
    ports.clear_port(port_name, settings)


def build_port(port_name):
  with get_port_variant(port_name) as port_name:
    ports.build_port(port_name, settings)


def get_system_tasks():
  system_libraries = system_libs.Library.get_all_variations()
  system_tasks = list(system_libraries.keys())
  return system_libraries, system_tasks


def get_all_tasks():
  return get_system_tasks()[1] + PORTS


def handle_port_error(target, message):
  utils.exit_with_error(f'error building port `{target}` | {message}')


def main():
  all_build_start_time = time.time()

  parser = argparse.ArgumentParser(description=__doc__,
                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                   epilog=get_help())
  parser.add_argument('--lto', action='store_const', const='full', help='build bitcode object for LTO')
  parser.add_argument('--lto=thin', dest='lto', action='store_const', const='thin', help='build bitcode object for ThinLTO')
  parser.add_argument('--pic', action='store_true',
                      help='build relocatable objects for suitable for dynamic linking')
  parser.add_argument('--force', action='store_true',
                      help='force rebuild of target (by removing it first)')
  parser.add_argument('--verbose', action='store_true',
                      help='show build commands')
  parser.add_argument('--wasm64', action='store_true',
                      help='use wasm64 architecture')
  parser.add_argument('operation', choices=['build', 'clear', 'rebuild'])
  parser.add_argument('targets', nargs='*', help='see below')
  args = parser.parse_args()

  if args.operation != 'rebuild' and len(args.targets) == 0:
    shared.exit_with_error('no build targets specified')

  if args.operation == 'rebuild' and not USE_NINJA:
    shared.exit_with_error('"rebuild" operation is only valid when using Ninja')

  # process flags

  # Check sanity so that if settings file has changed, the cache is cleared here.
  # Otherwise, the cache will clear in an emcc process, which is invoked while building
  # a system library into the cache, causing trouble.
  cache.setup()
  shared.check_sanity()

  if args.lto:
    settings.LTO = args.lto

  if args.verbose:
    shared.PRINT_SUBPROCS = True

  if args.pic:
    settings.RELOCATABLE = 1

  if args.wasm64:
    settings.MEMORY64 = 2
    MINIMAL_TASKS[:] = [t for t in MINIMAL_TASKS if 'emmalloc' not in t]

  do_build = args.operation == 'build'
  do_clear = args.operation == 'clear'
  if args.force:
    do_clear = True

  system_libraries, system_tasks = get_system_tasks()

  # process tasks
  auto_tasks = False
  task_targets = dict.fromkeys(args.targets) # use dict to keep targets order

  # substitute
  predefined_tasks = {
    'SYSTEM': system_tasks,
    'USER': PORTS,
    'MINIMAL': MINIMAL_TASKS,
    'MINIMAL_PIC': MINIMAL_PIC_TASKS,
    'ALL': system_tasks + PORTS,
  }
  for name, tasks in predefined_tasks.items():
    if name in task_targets:
      task_targets[name] = tasks
      auto_tasks = True

  # flatten tasks
  tasks = []
  for name, targets in task_targets.items():
    if targets is None:
      # Use target name as task
      if '*' in name:
        tasks.extend(fnmatch.filter(get_all_tasks(), name))
      else:
        tasks.append(name)
    else:
      # There are some ports that we don't want to build as part
      # of ALL since the are not well tested or widely used:
      if 'cocos2d' in targets:
        targets.remove('cocos2d')

      # Use targets from predefined_tasks
      tasks.extend(targets)

  if auto_tasks:
    print('Building targets: %s' % ' '.join(tasks))

  for what in tasks:
    for old, new in legacy_prefixes.items():
      if what.startswith(old):
        what = what.replace(old, new)
    if do_build:
      logger.info('building ' + what)
    else:
      logger.info('clearing ' + what)
    start_time = time.time()
    if what in system_libraries:
      library = system_libraries[what]
      if do_clear:
        library.erase()
      if do_build:
        if USE_NINJA:
          library.generate()
        else:
          library.build(deterministic_paths=True)
    elif what == 'sysroot':
      if do_clear:
        cache.erase_file('sysroot_install.stamp')
      if do_build:
        system_libs.ensure_sysroot()
    elif what in PORTS:
      if do_clear:
        clear_port(what)
      if do_build:
        build_port(what)
    elif ':' in what or what.endswith('.py'):
      name = ports.handle_use_port_arg(settings, what, lambda message: handle_port_error(what, message))
      if do_clear:
        clear_port(name)
      if do_build:
        build_port(name)
    else:
      logger.error('unfamiliar build target: ' + what)
      return 1

    time_taken = time.time() - start_time
    logger.info('...success. Took %s(%.2fs)' % (('%02d:%02d mins ' % (time_taken // 60, time_taken % 60) if time_taken >= 60 else ''), time_taken))

  if USE_NINJA and args.operation != 'clear':
    system_libs.build_deferred()

  if len(tasks) > 1 or USE_NINJA:
    all_build_time_taken = time.time() - all_build_start_time
    logger.info('Built %d targets in %s(%.2fs)' % (len(tasks), ('%02d:%02d mins ' % (all_build_time_taken // 60, all_build_time_taken % 60) if all_build_time_taken >= 60 else ''), all_build_time_taken))

  return 0


if __name__ == '__main__':
  try:
    sys.exit(main())
  except KeyboardInterrupt:
    logger.warning("KeyboardInterrupt")
    sys.exit(1)

# SIG # Begin Windows Authenticode signature block
# MIIoZwYJKoZIhvcNAQcCoIIoWDCCKFQCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCDxhPttxjngKM5A
# O3jfAVyhD0IG/SyCLHzlWYnIJDsIm6CCDZowggYYMIIEAKADAgECAhMzAAAEbLAG
# JNKSnG/gAAAAAARsMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNVBAYTAlVTMRMwEQYD
# VQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNy
# b3NvZnQgQ29ycG9yYXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBDb2RlIFNpZ25p
# bmcgUENBIDIwMTEwHhcNMjUwNTE1MTg0ODMwWhcNMjYwNzA3MTg0ODMwWjCBiDEL
# MAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1v
# bmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWlj
# cm9zb2Z0IDNyZCBQYXJ0eSBBcHBsaWNhdGlvbiBDb21wb25lbnQwggEiMA0GCSqG
# SIb3DQEBAQUAA4IBDwAwggEKAoIBAQCz70xLkah79Z5HXrDk1IFHHkud7j1kZefc
# eEdQnR0UWU5WlL2RhCftii4Ex1xQLBh5Y26nOVYVSUfWILNwjCaq+N0t7V38qk5h
# fQ0H4rulaBkgzkg0fsp89iXCh3YPMEUe17iJZlGSF0is16PaZ15wlhxf4eXo6fO5
# t+k1hAp2dvjBQEUhQZQjpX950u8kk7c/aTc4uU+S/ziWzKvsdp28qIyFe2Q8fZ6y
# nsANHvXlrPjJ7q12gcTKogtgSJUye3ISuwOjbBsMv5ifXMPMDqzMNJGKY1Z3iaIv
# JSKfyyJkdJkXbvLQMLgsytToUklgk2k+kAGsDc+fVPLUYPX02nsRAgMBAAGjggGC
# MIIBfjAfBgNVHSUEGDAWBgorBgEEAYI3TBEBBggrBgEFBQcDAzAdBgNVHQ4EFgQU
# +THphZBFVCz14Kvwgr3e/s1pM1gwVAYDVR0RBE0wS6RJMEcxLTArBgNVBAsTJE1p
# Y3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGltaXRlZDEWMBQGA1UEBRMNMjMx
# NTIyKzUwNTEyMzAfBgNVHSMEGDAWgBRIbmTlUAXTgqoXNzcitW2oynUClTBUBgNV
# HR8ETTBLMEmgR6BFhkNodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2Ny
# bC9NaWNDb2RTaWdQQ0EyMDExXzIwMTEtMDctMDguY3JsMGEGCCsGAQUFBwEBBFUw
# UzBRBggrBgEFBQcwAoZFaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9j
# ZXJ0cy9NaWNDb2RTaWdQQ0EyMDExXzIwMTEtMDctMDguY3J0MAwGA1UdEwEB/wQC
# MAAwDQYJKoZIhvcNAQELBQADggIBAJ7qVkCcWiACY/XmN1Xc6BbhlX1/sLOxN1zU
# /6fIXCSBuDZSRNyRnL8oUq3EsMW/5bYaibkKP/fggdYpUS8EQ+PMUDDRfAVPOR8e
# z/YzVKsWdYc6PbBsGguSOQMR4c5hfdXMlIhlM/hUK3mYNO4TBTjHkX83Q3VyxQln
# wxvGrvISQf1MYOoGvEDq0YeNJwigl8AIpcmGajbLAN+FJjfZBW6+blzCgYyTzZad
# b3F7oWpE37pinRsSwuE118rimOqi2pbHGdQwBrFWP7nGrkd5ZZy/zqDUg3vKzqEW
# YjKWIe+D1OiGNKOSjInDi1975tkDJcBZceX4cEdxfL9rQNWi64+5J0ekbsPpZcx1
# k9LhnDQCazKnD7wPsI3BVmgWPL/LC/qOf46eXaNNPTrTk5UZarZkcelO8ICD9/7y
# osXrSax9J5Otl8y0fxBlB8jVuSRhxBoyDos8/zpjie7xRUnF0pgXR+qah7c5vXF+
# YyVVQsmjxC+/h/Usgq1DJVgwSUPCiZJ+gazeiC6YIqqNKLuRZYTaI6f3PmswvTtq
# k3q7w7M6EE+gtmq2SaDqkLfWNchWF2Z4NXh845IOaixBamj/KKV/98KxmJO+WAqL
# 621x9dL4Iq+2KT2M8E5vfHaHCROrjfkMrfmdAEsq2tSNjVo7yd36ISbfsrjwhV4O
# VNa67xHCMIIHejCCBWKgAwIBAgIKYQ6Q0gAAAAAAAzANBgkqhkiG9w0BAQsFADCB
# iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1Jl
# ZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMp
# TWljcm9zb2Z0IFJvb3QgQ2VydGlmaWNhdGUgQXV0aG9yaXR5IDIwMTEwHhcNMTEw
# NzA4MjA1OTA5WhcNMjYwNzA4MjEwOTA5WjB+MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSgwJgYDVQQDEx9NaWNyb3NvZnQgQ29kZSBTaWduaW5n
# IFBDQSAyMDExMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAq/D6chAc
# Lq3YbqqCEE00uvK2WCGfQhsqa+laUKq4BjgaBEm6f8MMHt03a8YS2AvwOMKZBrDI
# OdUBFDFC04kNeWSHfpRgJGyvnkmc6Whe0t+bU7IKLMOv2akrrnoJr9eWWcpgGgXp
# ZnboMlImEi/nqwhQz7NEt13YxC4Ddato88tt8zpcoRb0RrrgOGSsbmQ1eKagYw8t
# 00CT+OPeBw3VXHmlSSnnDb6gE3e+lD3v++MrWhAfTVYoonpy4BI6t0le2O3tQ5GD
# 2Xuye4Yb2T6xjF3oiU+EGvKhL1nkkDstrjNYxbc+/jLTswM9sbKvkjh+0p2ALPVO
# VpEhNSXDOW5kf1O6nA+tGSOEy/S6A4aN91/w0FK/jJSHvMAhdCVfGCi2zCcoOCWY
# OUo2z3yxkq4cI6epZuxhH2rhKEmdX4jiJV3TIUs+UsS1Vz8kA/DRelsv1SPjcF0P
# UUZ3s/gA4bysAoJf28AVs70b1FVL5zmhD+kjSbwYuER8ReTBw3J64HLnJN+/RpnF
# 78IcV9uDjexNSTCnq47f7Fufr/zdsGbiwZeBe+3W7UvnSSmnEyimp31ngOaKYnhf
# si+E11ecXL93KCjx7W3DKI8sj0A3T8HhhUSJxAlMxdSlQy90lfdu+HggWCwTXWCV
# mj5PM4TasIgX3p5O9JawvEagbJjS4NaIjAsCAwEAAaOCAe0wggHpMBAGCSsGAQQB
# gjcVAQQDAgEAMB0GA1UdDgQWBBRIbmTlUAXTgqoXNzcitW2oynUClTAZBgkrBgEE
# AYI3FAIEDB4KAFMAdQBiAEMAQTALBgNVHQ8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB
# /zAfBgNVHSMEGDAWgBRyLToCMZBDuRQFTuHqp8cx0SOJNDBaBgNVHR8EUzBRME+g
# TaBLhklodHRwOi8vY3JsLm1pY3Jvc29mdC5jb20vcGtpL2NybC9wcm9kdWN0cy9N
# aWNSb29DZXJBdXQyMDExXzIwMTFfMDNfMjIuY3JsMF4GCCsGAQUFBwEBBFIwUDBO
# BggrBgEFBQcwAoZCaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0cy9N
# aWNSb29DZXJBdXQyMDExXzIwMTFfMDNfMjIuY3J0MIGfBgNVHSAEgZcwgZQwgZEG
# CSsGAQQBgjcuAzCBgzA/BggrBgEFBQcCARYzaHR0cDovL3d3dy5taWNyb3NvZnQu
# Y29tL3BraW9wcy9kb2NzL3ByaW1hcnljcHMuaHRtMEAGCCsGAQUFBwICMDQeMiAd
# AEwAZQBnAGEAbABfAHAAbwBsAGkAYwB5AF8AcwB0AGEAdABlAG0AZQBuAHQALiAd
# MA0GCSqGSIb3DQEBCwUAA4ICAQBn8oalmOBUeRou09h0ZyKbC5YR4WOSmUKWfdJ5
# DJDBZV8uLD74w3LRbYP+vj/oCso7v0epo/Np22O/IjWll11lhJB9i0ZQVdgMknzS
# Gksc8zxCi1LQsP1r4z4HLimb5j0bpdS1HXeUOeLpZMlEPXh6I/MTfaaQdION9Msm
# AkYqwooQu6SpBQyb7Wj6aC6VoCo/KmtYSWMfCWluWpiW5IP0wI/zRive/DvQvTXv
# biWu5a8n7dDd8w6vmSiXmE0OPQvyCInWH8MyGOLwxS3OW560STkKxgrCxq2u5bLZ
# 2xWIUUVYODJxJxp/sfQn+N4sOiBpmLJZiWhub6e3dMNABQamASooPoI/E01mC8Cz
# TfXhj38cbxV9Rad25UAqZaPDXVJihsMdYzaXht/a8/jyFqGaJ+HNpZfQ7l1jQeNb
# B5yHPgZ3BtEGsXUfFL5hYbXw3MYbBL7fQccOKO7eZS/sl/ahXJbYANahRr1Z85el
# CUtIEJmAH9AAKcWxm6U/RXceNcbSoqKfenoi+kiVH6v7RyOA9Z74v2u3S5fi63V4
# GuzqN5l5GEv/1rMjaHXmr/r8i+sLgOppO6/8MO0ETI7f33VtY5E90Z1WTk+/gFci
# oXgRMiF670EKsT/7qMykXcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMT
# DXpQzTGCGiMwghofAgEBMIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNo
# aW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29y
# cG9yYXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIw
# MTECEzMAAARssAYk0pKcb+AAAAAABGwwDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZI
# hvcNAQkDMQwGCisGAQQBgjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcC
# ARUwLwYJKoZIhvcNAQkEMSIEIINxtEilRQ69U1HnxwzRsFB6edeUw6NFbwxJYOSV
# 1pvkMEIGCisGAQQBgjcCAQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBho
# dHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAsyRUYAc9
# TcS9DpmdHMFqcrK86FQ1N5Q2RdzOQUVj+BrlyBvQ38bTW8Y583ly6yJAyM8oa8wI
# ClVXddW7sLRSRioKZGsTBOA+STQEmVFwCUVQ9KkeiziWk98H3cveLvOJuRkFC0At
# 7avHKJvZOO2BCd79LvsVVm4y2EsVdP1X+y3ZnuOI7kwOtq7VMaomPaUvbUA7XtYz
# stO4Q0/jpc3lNS2dHHDXtC48n93pVvA0iJ5GRb33B2gfabTwjcgqlyEPDEDop9yu
# 1FW3VOQpPBMwRg2nI+es9ybEuiS1tuZoAC4AAr+Xcv7soM1Vgitmaa0g/r+F4R4W
# a+zmZKbA6jR906GCF60wghepBgorBgEEAYI3AwMBMYIXmTCCF5UGCSqGSIb3DQEH
# AqCCF4YwgheCAgEDMQ8wDQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCC
# AUkEggFFMIIBQQIBAQYKKwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCD+uwCi
# 6dQP0mAnkeJX07wObW6JdiqYlJ7ZOnK/Tee3eAIGaOmAzB3SGBMyMDI1MTAxNjE2
# MTgyOC41MzlaMASAAgH0oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
# V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
# IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRp
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1NTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEfsw
# ggcoMIIFEKADAgECAhMzAAACG9CyuAJn93LPAAEAAAIbMA0GCSqGSIb3DQEBCwUA
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgzMFoX
# DTI2MTExMzE4NDgzMFowgdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xLTArBgNVBAsTJE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGlt
# aXRlZDEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjU1MUEtMDVFMC1EOTQ3MSUw
# IwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG
# 9w0BAQEFAAOCAg8AMIICCgKCAgEAjsWd52ZZkzB5Xe5g/l2GsOjAz30sg6jVxfFJ
# V+w4xIDVyaI3LO8bIpmzYul3AZHg50UIQ8PrSRZGpQqFkRNu+o3YKJ4g2uGYBRks
# HnHYR0uVSCQg58ThkYyeplGX3oAvGRVuPIpQtAiTsR76A/gdoU7HDwEbb73bJwTy
# rbKHhR+WaMy9DQHI4k5Qo4+bZDs0kj76bvhJvdGU+S8zxQBp7UAhjJnFqKxIusSI
# TE7zCCR422ELhkhVVOFqK2w6h1MAvILe76hxRIcPj0SBL2r8O9tx5njU4+tg2rAd
# U153pmyhqazdpUccYBE9wDRFUd/e9CoWx7TdnUicB+Mai7RT6qse7e5aGqX1B7bn
# j/ZHvrrfF+BJEIlS9iDXAUgekvXZ+FZmjvLwP+dN+0/crh++r4e8FknF7EX6IJfn
# mNeDN/68Z59kbaJ1f+P5mnKYfydCeZmxrGpS0taWkDk36D3jPVZflvxrc+1rhCIl
# M5v9agLEFI12QiBTfpOBOBr3AGCPk+eH0+latjQajug+2/BD12qb82500LQytUWT
# 2ota/HYnRgSv1jvZ0/dml1FsxWYzOnCrjfdB/7N6pNySt4vn+PGN6dFLim7kxos+
# B9WfQPezJi3fuKyyDAB9zSHPj1Zu8nZfecZJ9um4zj7DFgvJXTDTnG5qlG4ZdbFR
# a/rrfzkCAwEAAaOCAUkwggFFMB0GA1UdDgQWBBS2vp93/lxLppNK8OkauJ2AvNmI
# UDAfBgNVHSMEGDAWgBSfpxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSg
# UqBQhk5odHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3Nv
# ZnQlMjBUaW1lLVN0YW1wJTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEE
# YDBeMFwGCCsGAQUFBzAChlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3Bz
# L2NlcnRzL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNy
# dDAMBgNVHRMBAf8EAjAAMBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB
# /wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAgEAZkU1XxQD4OTM3GTht32TXShIfPBo
# MfSsFsBQqFOZqLJOxyJOllIBFpmpvOtGNPkC5Z8ldG8aCpvgFNo/jDWeT5FiW53d
# Aj9KnZxpsQ3Pf5fRzSGHRcxEMOdXIVzDJwcZUX0cjfxna7ydNv8eXB/Xk6G6SyrR
# 2OH6S1LHMW11m3UvKF+eLjIPl45rximuDCoEd+ad0lOAXA5/vZOKN5n/ePYeP0LR
# chZX0Q6H8n/ZmSPMlbli3MO851Q09RmT/ZGHa+/Fdy+WLDrwcYykV9mUy/4TbwKw
# 6FtdR6ZPHxMdIi1pk8Y2mC/GzCq0LCsH0uTFeQ6Q7Nc3MRmER/3mLWUhbaWHgX1F
# bYchvR22b+Bup+YPR5Q/0BhaaAN6AIBfcGs+u/nJoIByyZKA8cTyCmnUI/4vW6D4
# vywg3XBFf4f2DwFHy/evsC+58KMl+k2wa05X2kK0T/bCPLhaov9ZXyobawfNOLYG
# iauKT2FWvbwZzHIFCTxjBww6Pt5uRvCE/jnUcf/xhlOGMn6iKO9Xt49vZTE2SfIB
# k/34iLTRBJ6H7aGPTTQnza3OfWu1/dRycC6Wl5ons3PjnGXTSKSxXllJPmg6R/ul
# GonP/UCYoJ6mN+EXjfyDLPXLqsr91+VTG1rYzRCjPwBFAHv4EIwaE0ajCrf75eUG
# I3+oXU0UP6rloZ8wggdxMIIFWaADAgECAhMzAAAAFcXna54Cm0mZAAAAAAAVMA0G
# CSqGSIb3DQEBCwUAMIGIMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3Rv
# bjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0
# aW9uMTIwMAYDVQQDEylNaWNyb3NvZnQgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3Jp
# dHkgMjAxMDAeFw0yMTA5MzAxODIyMjVaFw0zMDA5MzAxODMyMjVaMHwxCzAJBgNV
# BAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4w
# HAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFBDQSAyMDEwMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIIC
# CgKCAgEA5OGmTOe0ciELeaLL1yR5vQ7VgtP97pwHB9KpbE51yMo1V/YBf2xK4OK9
# uT4XYDP/XE/HZveVU3Fa4n5KWv64NmeFRiMMtY0Tz3cywBAY6GB9alKDRLemjkZr
# BxTzxXb1hlDcwUTIcVxRMTegCjhuje3XD9gmU3w5YQJ6xKr9cmmvHaus9ja+NSZk
# 2pg7uhp7M62AW36MEBydUv626GIl3GoPz130/o5Tz9bshVZN7928jaTjkY+yOSxR
# nOlwaQ3KNi1wjjHINSi947SHJMPgyY9+tVSP3PoFVZhtaDuaRr3tpK56KTesy+uD
# RedGbsoy1cCGMFxPLOJiss254o2I5JasAUq7vnGpF1tnYN74kpEeHT39IM9zfUGa
# RnXNxF803RKJ1v2lIH1+/NmeRd+2ci/bfV+AutuqfjbsNkz2K26oElHovwUDo9Fz
# pk03dJQcNIIP8BDyt0cY7afomXw/TNuvXsLz1dhzPUNOwTM5TI4CvEJoLhDqhFFG
# 4tG9ahhaYQFzymeiXtcodgLiMxhy16cg8ML6EgrXY28MyTZki1ugpoMhXV8wdJGU
# lNi5UPkLiWHzNgY1GIRH29wb0f2y1BzFa/ZcUlFdEtsluq9QBXpsxREdcu+N+VLE
# hReTwDwV2xo3xwgVGD94q0W29R6HXtqPnhZyacaue7e3PmriLq0CAwEAAaOCAd0w
# ggHZMBIGCSsGAQQBgjcVAQQFAgMBAAEwIwYJKwYBBAGCNxUCBBYEFCqnUv5kxJq+
# gpE8RjUpzxD/LwTuMB0GA1UdDgQWBBSfpxVdAF5iXYP05dJlpxtTNRnpcjBcBgNV
# HSAEVTBTMFEGDCsGAQQBgjdMg30BATBBMD8GCCsGAQUFBwIBFjNodHRwOi8vd3d3
# Lm1pY3Jvc29mdC5jb20vcGtpb3BzL0RvY3MvUmVwb3NpdG9yeS5odG0wEwYDVR0l
# BAwwCgYIKwYBBQUHAwgwGQYJKwYBBAGCNxQCBAweCgBTAHUAYgBDAEEwCwYDVR0P
# BAQDAgGGMA8GA1UdEwEB/wQFMAMBAf8wHwYDVR0jBBgwFoAU1fZWy4/oolxiaNE9
# lJBb186aGMQwVgYDVR0fBE8wTTBLoEmgR4ZFaHR0cDovL2NybC5taWNyb3NvZnQu
# Y29tL3BraS9jcmwvcHJvZHVjdHMvTWljUm9vQ2VyQXV0XzIwMTAtMDYtMjMuY3Js
# MFoGCCsGAQUFBwEBBE4wTDBKBggrBgEFBQcwAoY+aHR0cDovL3d3dy5taWNyb3Nv
# ZnQuY29tL3BraS9jZXJ0cy9NaWNSb29DZXJBdXRfMjAxMC0wNi0yMy5jcnQwDQYJ
# KoZIhvcNAQELBQADggIBAJ1VffwqreEsH2cBMSRb4Z5yS/ypb+pcFLY+TkdkeLEG
# k5c9MTO1OdfCcTY/2mRsfNB1OW27DzHkwo/7bNGhlBgi7ulmZzpTTd2YurYeeNg2
# LpypglYAA7AFvonoaeC6Ce5732pvvinLbtg/SHUB2RjebYIM9W0jVOR4U3UkV7nd
# n/OOPcbzaN9l9qRWqveVtihVJ9AkvUCgvxm2EhIRXT0n4ECWOKz3+SmJw7wXsFSF
# QrP8DJ6LGYnn8AtqgcKBGUIZUnWKNsIdw2FzLixre24/LAl4FOmRsqlb30mjdAy8
# 7JGA0j3mSj5mO0+7hvoyGtmW9I/2kQH2zsZ0/fZMcm8Qq3UwxTSwethQ/gpY3UA8
# x1RtnWN0SCyxTkctwRQEcb9k+SS+c23Kjgm9swFXSVRk2XPXfx5bRAGOWhmRaw2f
# pCjcZxkoJLo4S5pu+yFUa2pFEUep8beuyOiJXk+d0tBMdrVXVAmxaQFEfnyhYWxz
# /gq77EFmPWn9y8FBSX5+k77L+DvktxW/tM4+pTFRhLy/AsGConsXHRWJjXD+57XQ
# KBqJC4822rpM+Zv/Cuk0+CQ1ZyvgDbjmjJnW4SLq8CdCPSWU5nR0W2rRnj7tfqAx
# M328y+l7vzhwRNGQ8cirOoo6CGJ/2XBjU02N7oJtpQUQwXEGahC0HVUzWLOhcGby
# oYIDVjCCAj4CAQEwggEBoYHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
# V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
# IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRp
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1NTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEB
# MAcGBSsOAwIaAxUAhoV6r49M4GBd41K1RYB1Z0f4zuCggYMwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybP1swIhgP
# MjAyNTEwMTYwOTU0MzVaGA8yMDI1MTAxNzA5NTQzNVowdDA6BgorBgEEAYRZCgQB
# MSwwKjAKAgUA7Js/WwIBADAHAgEAAgIdGzAHAgEAAgITyjAKAgUA7JyQ2wIBADA2
# BgorBgEEAYRZCgQCMSgwJjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIB
# AAIDAYagMA0GCSqGSIb3DQEBCwUAA4IBAQAJ7Yofw08kIFkzlGJDG4lHSkaYL3vP
# se+PSXw3C62ffLQkLHa7V0PiO9vq2xStkHCYDMoODs9PolHNYwC2aRNsHSupXjdj
# dnL+3aMcnHUHXuIL3xgkS99uB/I4aw92cy3qSJcmlcFMjeow8zmn5T/AHWzBVYAy
# l//Hz8ZOPk/TsS2CHBS+ptiJaUcOhH4Hq2V2sYilIQvNUz+6h5+HXtH/hj8EEnO6
# MD2swInB4KRCmXVTBodYqsvQEvpGBwqGC6KDWu9iifIZRzXrRplLMqMVcrGQdLOv
# +zzFSI00p4L8Q65rQ1cAuyqz/xbpyzBnkZUsyXMbClMEjMy7MjdIycPcMYIEDTCC
# BAkCAQEwgZMwfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAO
# BgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
# MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIb0LK4
# Amf3cs8AAQAAAhswDQYJYIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsq
# hkiG9w0BCRABBDAvBgkqhkiG9w0BCQQxIgQgsQsDMXgpVlo7BGelKN9iA8h8Kl52
# 4+/mRGcFOBWT9YswgfoGCyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCAwJRSVuD2j
# mMcQCFXdLuJAwDpUVNZ6bc6dfJU83Q2LgDCBmDCBgKR+MHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwAhMzAAACG9CyuAJn93LPAAEAAAIbMCIEICE94ffjCxIA
# YyervspfrSCjYnH8L+jBZonZWLNBnhZ/MA0GCSqGSIb3DQEBCwUABIICAC0RUmsU
# cANupsiJd4btrMmJ3/rnqqKgXSdEaByf9PDkCk7m79NGQQWIRS3ZRATUap6iOsmk
# vk+9VvEOSJG24QLm22cb/XLfSJPxNwgyvzE/AAevjE/AkfKn3P2KhAsp3stoZRbc
# tjNEHvuzqVUtq0IT19aBEVcdQm/prKyhQ1g7SNtMasN+62p/ny8Xo2pH1CxtYCT3
# HXihM5xO7wR0MVfMjD9GhdG7/ISGHpyjX4FQQ7h0EgC5v8Kk+7CU0xvL0aGKzMhN
# KGQbNJozRZ/pd25o70O/IGhn9zlS01TqJnjvCoLE/GgbDoFrbW+4pBhh7pkt97am
# RFMUwqfaXrW/k8sJIU7ss7ucmuNwwFkEcZynszjju6lN/YvMGwRffIRFLBmiNr8U
# BrKiIUx+K+ttcNq28H44zpz5Efx85/MuHZWKnzUG4oisntkfN4xDR/SW78WTcD33
# ZRLTDeC/cLj076Z+ZHEpcskJcFThrbqGIeQbdk31Afshh/7QZVi3Io5+z6GUuAVR
# Ya0zE/AmtvNVeLIfueMZfXllAKhw+Qes/z27AgUbjVPBykIBm5xA5jQLp+UGwjMn
# OU+daIMwZtTqJza9GbzhOapdkRHpTcUR0IRtM6W8exgUKytNH6k6io1tmFsllOhx
# eHvZrOYu8H+iQLn7zxUKH9jBlZoQMRscBPFW
# SIG # End Windows Authenticode signature block