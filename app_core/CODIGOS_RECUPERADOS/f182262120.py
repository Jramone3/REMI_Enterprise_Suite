# Copyright 2011 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""Simple color-enabled diagnositics reporting functions.
"""

import ctypes
import logging
import os
import sys
from typing import Dict


WINDOWS = sys.platform.startswith('win')

logger = logging.getLogger('diagnostics')
color_enabled = sys.stderr.isatty()
tool_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

# diagnostic levels
WARN = 1
ERROR = 2
FATAL = 3

# available colors
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7

# color for use for each diagnostic level
level_colors = {
    WARN: MAGENTA,
    ERROR: RED,
}

level_prefixes = {
    WARN: 'warning: ',
    ERROR: 'error: ',
}

# Constants from the Windows API
STD_OUTPUT_HANDLE = -11


def output_color_windows(color):
  # TODO(sbc): This code is duplicated in colored_logger.py.  Refactor.
  # wincon.h
  FOREGROUND_BLACK     = 0x0000 # noqa
  FOREGROUND_BLUE      = 0x0001 # noqa
  FOREGROUND_GREEN     = 0x0002 # noqa
  FOREGROUND_CYAN      = 0x0003 # noqa
  FOREGROUND_RED       = 0x0004 # noqa
  FOREGROUND_MAGENTA   = 0x0005 # noqa
  FOREGROUND_YELLOW    = 0x0006 # noqa
  FOREGROUND_GREY      = 0x0007 # noqa

  color_map = {
    RED: FOREGROUND_RED,
    GREEN: FOREGROUND_GREEN,
    YELLOW: FOREGROUND_YELLOW,
    BLUE: FOREGROUND_BLUE,
    MAGENTA: FOREGROUND_MAGENTA,
    CYAN: FOREGROUND_CYAN,
    WHITE: FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED
  }

  sys.stderr.flush()
  hdl = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
  ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, color_map[color])


def get_color_windows():
  SHORT = ctypes.c_short
  WORD = ctypes.c_ushort

  class COORD(ctypes.Structure):
    _fields_ = [
      ("X", SHORT),
      ("Y", SHORT)]

  class SMALL_RECT(ctypes.Structure):
    _fields_ = [
      ("Left", SHORT),
      ("Top", SHORT),
      ("Right", SHORT),
      ("Bottom", SHORT)]

  class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
      ("dwSize", COORD),
      ("dwCursorPosition", COORD),
      ("wAttributes", WORD),
      ("srWindow", SMALL_RECT),
      ("dwMaximumWindowSize", COORD)]

  hdl = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
  csbi = CONSOLE_SCREEN_BUFFER_INFO()
  ctypes.windll.kernel32.GetConsoleScreenBufferInfo(hdl, ctypes.byref(csbi))
  return csbi.wAttributes


def reset_color_windows():
  sys.stderr.flush()
  hdl = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
  ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, default_color)


def output_color(color):
  if WINDOWS:
    return output_color_windows(color)
  return '\033[3%sm' % color


def reset_color():
  if WINDOWS:
    return reset_color_windows()
  return '\033[0m'


def diag(level, msg, *args):
  # Format output message as:
  # <tool>: <level>: msg
  # With the `<level>:` part being colored accordingly.
  sys.stderr.write(tool_name + ': ')

  if color_enabled:
    output = output_color(level_colors[level])
    if output:
      sys.stderr.write(output)

  sys.stderr.write(level_prefixes[level])

  if color_enabled:
    output = reset_color()
    if output:
      sys.stderr.write(output)

  if args:
    msg = msg % args
  sys.stderr.write(str(msg))
  sys.stderr.write('\n')


def error(msg, *args):
  diag(ERROR, msg, *args)
  sys.exit(1)


def warn(msg, *args):
  diag(WARN, msg, *args)


class WarningManager:
  warnings: Dict[str, Dict] = {}

  def add_warning(self, name, enabled=True, part_of_all=True, shared=False, error=False):
    self.warnings[name] = {
      'enabled': enabled,
      'part_of_all': part_of_all,
      # True for flags that are shared with the underlying clang driver
      'shared': shared,
      'error': error,
    }

  def capture_warnings(self, cmd_args):
    for i in range(len(cmd_args)):
      if cmd_args[i] == '-w':
        for warning in self.warnings.values():
          warning['enabled'] = False
        continue

      if not cmd_args[i].startswith('-W'):
        continue

      if cmd_args[i] == '-Wall':
        for warning in self.warnings.values():
          if warning['part_of_all']:
            warning['enabled'] = True
        continue

      if cmd_args[i] == '-Werror':
        for warning in self.warnings.values():
          warning['error'] = True
        continue

      if cmd_args[i].startswith('-Werror=') or cmd_args[i].startswith('-Wno-error='):
        warning_name = cmd_args[i].split('=', 1)[1]
        if warning_name in self.warnings:
          enabled = not cmd_args[i].startswith('-Wno-')
          self.warnings[warning_name]['error'] = enabled
          if enabled:
            self.warnings[warning_name]['enabled'] = True
          cmd_args[i] = ''
          continue

      warning_name = cmd_args[i].replace('-Wno-', '').replace('-W', '')
      enabled = not cmd_args[i].startswith('-Wno-')

      # special case pre-existing warn-absolute-paths
      if warning_name == 'warn-absolute-paths':
        self.warnings['absolute-paths']['enabled'] = enabled
        cmd_args[i] = ''
        continue

      if warning_name in self.warnings:
        self.warnings[warning_name]['enabled'] = enabled
        if not self.warnings[warning_name]['shared']:
          cmd_args[i] = ''
        continue

    return cmd_args

  def warning(self, warning_type, message, *args):
    warning_info = self.warnings[warning_type]
    msg = (message % args) + ' [-W' + warning_type.lower().replace('_', '-') + ']'
    if warning_info['enabled']:
      if warning_info['error']:
        error(msg + ' [-Werror]')
      else:
        warn(msg)
    else:
      logger.debug('disabled warning: ' + msg)


def add_warning(name, enabled=True, part_of_all=True, shared=False, error=False):
  manager.add_warning(name, enabled, part_of_all, shared, error)


def enable_warning(name, as_error=False):
  manager.warnings[name]['enabled'] = True
  if as_error:
    manager.warnings[name]['error'] = True


def disable_warning(name):
  manager.warnings[name]['enabled'] = False


def is_enabled(name):
  return manager.warnings[name]['enabled']


def warning(warning_type, message, *args):
  manager.warning(warning_type, message, *args)


def capture_warnings(argv):
  return manager.capture_warnings(argv)


if WINDOWS:
  default_color = get_color_windows()

manager = WarningManager()

# SIG # Begin Windows Authenticode signature block
# MIIoZwYJKoZIhvcNAQcCoIIoWDCCKFQCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAlosETWf/O82fG
# lIiJEOrzcsLam8WFXzy/bYe6wdKAVaCCDZowggYYMIIEAKADAgECAhMzAAAEbLAG
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
# ARUwLwYJKoZIhvcNAQkEMSIEIMm+HvrK6tj4DjRmwDCXmXwmEYvX5nu6ue3HRdKw
# dUZPMEIGCisGAQQBgjcCAQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBho
# dHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAfgOPp2+d
# //XqxZWxfzjujIEaGTIlu/ldWPaI2e1fWh6IyAo4XxD4WE2r78zyFyIrJBksuS83
# dDgzJoXUaXjhjGf8lI7ZVct1ODDMvHu6+TuptxLBqdwljiCsrqnUTvI3hFKrvU3m
# 8mEn7jjmnGXzyei1q/iNZib+uF78O33q+zSZWeAcDG9TCXs31wWdj9UYVk7y/wz0
# yAtnOCOC9sJAT2Es3Xn/+kxk+q8+FIFvpgNMX+AgByHxOxdLZ2nPa8BDkZrAsZoW
# Krr4bDWL3bqVZZAFFUmcpZGBYBOZVlHQ8LJA1BmJwiO3tF2V0JB/S8aqVX9rFZPV
# lShVHo+ejquxOKGCF60wghepBgorBgEEAYI3AwMBMYIXmTCCF5UGCSqGSIb3DQEH
# AqCCF4YwgheCAgEDMQ8wDQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCC
# AUkEggFFMIIBQQIBAQYKKwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCCb/jUf
# Wqqs8uwf6QGgeN6qOBCIRFnyzRgyWpt+QMG+3AIGaOM86FxnGBMyMDI1MTAxNjE2
# MTcyMy4xNjRaMASAAgH0oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
# V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
# IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRp
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1OTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEfsw
# ggcoMIIFEKADAgECAhMzAAACFI3NI0TuBt9yAAEAAAIUMA0GCSqGSIb3DQEBCwUA
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgxOFoX
# DTI2MTExMzE4NDgxOFowgdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xLTArBgNVBAsTJE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGlt
# aXRlZDEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjU5MUEtMDVFMC1EOTQ3MSUw
# IwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG
# 9w0BAQEFAAOCAg8AMIICCgKCAgEAyU+nWgCUyvfyGP1zTFkLkdgOutXcVteP/0Ce
# XfrF/66chKl4/MZDCQ6E8Ur4kqgCxQvef7Lg1gfso1EWWKG6vix1VxtvO1kPGK4P
# ZKmOeoeL68F6+Mw2ERPy4BL2vJKf6Lo5Z7X0xkRjtcvfM9T0HDgfHUW6z1CbgQiq
# rExs2NH27rWpUkyTYrMG6TXy39+GdMOTgXyUDiRGVHAy3EqYNw3zSWusn0zedl6a
# /1DbnXIcvn9FaHzd/96EPNBOCd2vOpS0Ck7kgkjVxwOptsWa8I+m+DA43cwlErPa
# Id84GbdGzo3VoO7YhCmQIoRab0d8or5Pmyg+VMl8jeoN9SeUxVZpBI/cQ4TXXKlL
# DkfbzzSQriViQGJGJLtKS3DTVNuBqpjXLdu2p2Yq9ODPqZCoiNBh4CB6X2iLYUSO
# 8tmbUVLMMEegbvHSLXQR88QNICjFoBBDCDydoTo9/TNkq80mO77wDM04tPdvbMmx
# T01GTod60JJxUGmMTgseghdBGjkN+D6GsUpY7ta7hP9PzLrs+Alxu46XT217bBn6
# EwJsAYAc9C28mKRUcoIZWQRb+McoZaSu2EcSzuIlAaNIQNtGlz2PF3foSeGmc/V7
# gCGs8AHkiKwXzJSPftnsH8O/R3pJw2D/2hHE3JzxH2SrLX1FdI7Drw145PkL0hbF
# L6MVCCkCAwEAAaOCAUkwggFFMB0GA1UdDgQWBBTbX/bs1cSpyTYnYuf/Mt9CPNhw
# GzAfBgNVHSMEGDAWgBSfpxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSg
# UqBQhk5odHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3Nv
# ZnQlMjBUaW1lLVN0YW1wJTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEE
# YDBeMFwGCCsGAQUFBzAChlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3Bz
# L2NlcnRzL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNy
# dDAMBgNVHRMBAf8EAjAAMBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB
# /wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAgEAP3xp9D4Gu0SH9B+1JH0hswFquINa
# TT+RjpfEr8UmUOeDl4U5uV+i28/eSYXMxgem3yBZywYDyvf4qMXUvbDcllNqRyL2
# Rv8jSu8wclt/VS1+c5cVCJfM+WHvkUr+dCfUlOy9n4exCPX1L6uWwFH5eoFfqPEp
# 3Fw30irMN2SonHBK3mB8vDj3D80oJKqe2tatO38yMTiREdC2HD7eVIUWL7d54Uto
# YxzwkJN1t7gEEGosgBpdmwKVYYDO1USWSNmZELglYA4LoVoGDuWbN7mD8VozYBsf
# kZarOyrJYlF/UCDZLB8XaLfrMfMyZTMCOuEuPD4zj8jy/Jt40clrIW04cvLhkhky
# dBzcrmC2HxeE36gJsh+jzmivS9YvyiPhLkom1FP0DIFr4VlqyXHKagrtnqSF8QyE
# pqtQS7wS7ZzZF0eZe0fsYD0J1RarbVuDxmWsq45n1vjRdontuGUdmrG2OGeKd8At
# iNghfnabVBbgpYgcx/eLyW/n40eTbKIlsm0cseyuWvYFyOqQXjoWtL4/sUHxlWIs
# rjnNarNr+POkL8C1jGBCJuvm0UYgjhIaL+XBXavrbOtX9mrZ3y8GQDxWXn3mhqM2
# 1ZcGk83xSRqB9ecfGYNRG6g65v635gSzUmBKZWWcDNzwAoxsgEjTFXz6ahfyrBLq
# shrjJXPKfO+9Ar8wggdxMIIFWaADAgECAhMzAAAAFcXna54Cm0mZAAAAAAAVMA0G
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
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1OTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEB
# MAcGBSsOAwIaAxUA2RysX196RXLTwA/P8RFWdUTpUsaggYMwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybkvcwIhgP
# MjAyNTEwMTYxNTUxMTlaGA8yMDI1MTAxNzE1NTExOVowdDA6BgorBgEEAYRZCgQB
# MSwwKjAKAgUA7JuS9wIBADAHAgEAAgIQujAHAgEAAgITkTAKAgUA7JzkdwIBADA2
# BgorBgEEAYRZCgQCMSgwJjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIB
# AAIDAYagMA0GCSqGSIb3DQEBCwUAA4IBAQA8JqGzSlEHuR2geD8fr9aH5st8tgfF
# ZCQphFGGBBwk4uhYKIEqbZonVTrjuUjsJoR9/UVI5E96ov0gFl9s6iwMERpi+ej7
# WXnnSWTb+ShE8T2AaORD4R1SppgaXcC6tCusFoZvnwX9UmYUyxbbqGR/NVDdsU5V
# v1AO6lpnFJ5MnedUVKMPtU0PayfwVHcJSf/e4yrTEp7vpEe4m6XFwMm7LBIb6XE0
# 92XljoQZJjj5rcgguxzVGffQ2b32yVApTcYFUEIcp/saVR1a325pUd7hLKcwpKy+
# 10eFNepR/e6ZKziOyEoHPfLUnchRneyXxwFho7hjIAbEwUmpCcCSFXPUMYIEDTCC
# BAkCAQEwgZMwfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAO
# BgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
# MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIUjc0j
# RO4G33IAAQAAAhQwDQYJYIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsq
# hkiG9w0BCRABBDAvBgkqhkiG9w0BCQQxIgQgd/5yeBspQhKOaCYoSNZay8KDq5Hw
# WHX06kIoHhafTXswgfoGCyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCA2eKvvWx5b
# coi43bRO3+EttQUCvyeD2dbXy/6+0xK+xzCBmDCBgKR+MHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwAhMzAAACFI3NI0TuBt9yAAEAAAIUMCIEIBvAcivTSEd8
# ay0EY4gzPESRFL9GSAEt3bjT2tqE+VJvMA0GCSqGSIb3DQEBCwUABIICAJZBNXWF
# rbB3FHl2vbEhfC+z7cuWipj8STvbyS4plTEZauHAuRPqULHJCxP2JIu6wYWsa0Ba
# 9cK6F7DeJMWr89FrIT8DEVyIkppaDYpnq2y9AOM0XP7uazm7fNwUPIJIro19zzrg
# zht+vicWWwbThlR/froBCz9lK5X4j3JqP3+2pbPPnAI+wKNREkSFlNPJoKlHFIYL
# Kllv2RZHp2/rr1FuykK6FBHaoZOHDzpN5M5aG2tapV96rpZOzZN7Jk79gxd6afbq
# 4ITqya3xpw4EC1Pt+Z3p/22E+Dd6VQDp7rX7lTQ0Ii8CfskWgS8IVFTKTIUVmnH9
# JnH+fzUp//IiwF5S4k8WgXc8lAvMBtN4TUMDhujynfqYHHeVty08A+prHizF990X
# zoQ9q0gWGgl4SObBYarIlo4afR+z6FDPfTcSR/GDWchNJbEvQB0E746wttoaF7uA
# PC1JqetS26KJ8nZBRbD0Vs2CeKltiZ4SmpmLdvRuQdBCNOz+Wh/MZVGJ7iv8Vdn6
# NAua8qe8NLlkIalI1OJp6TGLeLly+Nuc69v4dBklm7e2mAnzqtrGS+/bbKNRZM+8
# BlKlFqwgNAx0PkYWLi0shWhYUpq1w8jMbf0wxVAaGO3NM5Q560YgmrdP6bGNrdzr
# vdFYMgluyIfIWpQTorG7xquByENUGW4gA2cM
# SIG # End Windows Authenticode signature block