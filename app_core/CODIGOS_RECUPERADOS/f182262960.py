#!/usr/bin/env python3
# Copyright 2014 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import os
import sys


def convert_line_endings(text, from_eol, to_eol):
  if from_eol == to_eol:
    return text
  return text.replace(from_eol, to_eol)


def convert_line_endings_in_file(filename, from_eol, to_eol):
  if from_eol == to_eol:
    return # No conversion needed

  with open(filename, 'rb') as f:
    text = f.read()
  text = convert_line_endings(text, from_eol.encode(), to_eol.encode())
  with open(filename, 'wb') as f:
    f.write(text)


def check_line_endings(filename, expect_only=None, print_errors=True, print_info=False):
  """Detect inconsitent/invalid line endings.

  This function checks and prints out the detected line endings in the given
  file. If the file only contains either Windows \\r\\n line endings or Unix \\n
  line endings, it returns 0.  Otherwise, in the presence of old macOS or
  mixed/malformed line endings, a non-zero error code is returned.
  """
  if not os.path.exists(filename):
    if print_errors:
      print('File not found: ' + filename, file=sys.stderr)
    return 1

  with open(filename, 'rb') as f:
    data = f.read()

  index = data.find(b"\r\r\n")
  if index != -1:
    if print_errors:
      print("File '" + filename + "' contains BAD line endings of form \\r\\r\\n!", file=sys.stderr)
      bad_line = data[index - 50:index + 50].replace(b'\r', b'\\r').replace(b'\n', b'\\n')
      print("Content around the location: '" + bad_line.decode('utf-8') + "'", file=sys.stderr)
    return 1 # Bad line endings in file, return a non-zero process exit code.

  has_dos_line_endings = False
  has_unix_line_endings = False
  dos_line_ending_example = ''
  dos_line_ending_count = 0
  unix_line_ending_example = ''
  unix_line_ending_count = 0

  index = data.find(b'\r\n')
  if index != -1:
    dos_line_ending_example = data[index - 50:index + 50].replace(b'\r', b'\\r').replace(b'\n', b'\\n')
    dos_line_ending_count = data.count(b'\r\n')
    # Replace all DOS line endings with some other character, and continue testing what's left.
    data = data.replace(b'\r\n', b'A')
    has_dos_line_endings = True

  index = data.find(b'\r\n')
  if index != -1:
    unix_line_ending_example = data[index - 50:index + 50].replace(b'\r', b'\\r').replace(b'\n', b'\\n')
    unix_line_ending_count = data.count(b'\n')
    has_unix_line_endings = True

  index = data.find(b'\r')
  if index != -1:
    old_macos_line_ending_example = data[index - 50:index + 50].replace(b'\r', b'\\r').replace(b'\n', b'\\n')
    if print_errors:
      print('File \'' + filename + '\' contains OLD macOS line endings "\\r"', file=sys.stderr)
      print("Content around an OLD macOS line ending location: '" + old_macos_line_ending_example + "'", file=sys.stderr)
    # We don't want to use the old macOS (9.x) line endings anywhere.
    return 1

  if has_dos_line_endings and has_unix_line_endings:
    if print_errors:
      print('File \'' + filename + '\' contains both DOS "\\r\\n" and UNIX "\\n" line endings! (' + str(dos_line_ending_count) + ' DOS line endings, ' + str(unix_line_ending_count) + ' UNIX line endings)', file=sys.stderr)
      print("Content around a DOS line ending location: '" + dos_line_ending_example + "'", file=sys.stderr)
      print("Content around an UNIX line ending location: '" + unix_line_ending_example + "'", file=sys.stderr)
    # Mixed line endings
    return 1

  if print_info:
    if has_dos_line_endings:
      print('File \'' + filename + '\' contains DOS "\\r\\n" line endings.')
    if has_unix_line_endings:
      print('File \'' + filename + '\' contains UNIX "\\n" line endings.')

  if expect_only == '\n' and has_dos_line_endings:
    if print_errors:
      print('File \'' + filename + '\' contains DOS "\\r\\n" line endings! (' + str(dos_line_ending_count) + ' DOS line endings), but expected only UNIX line endings!', file=sys.stderr)
      print("Content around a DOS line ending location: '" + dos_line_ending_example + "'", file=sys.stderr)
    return 1 # DOS line endings, but expected UNIX

  if expect_only == '\r\n' and has_unix_line_endings:
    if print_errors:
      print('File \'' + filename + '\' contains UNIX "\\n" line endings! (' + str(unix_line_ending_count) + ' UNIX line endings), but expected only DOS line endings!', file=sys.stderr)
      print("Content around a UNIX line ending location: '" + unix_line_ending_example + "'", file=sys.stderr)
    return 1 # UNIX line endings, but expected DOS

  return 0


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print('Unknown command line ' + str(sys.argv) + '!', file=sys.stderr)
    print('Usage: ' + sys.argv[0] + ' <filename>', file=sys.stderr)
    sys.exit(1)
  sys.exit(check_line_endings(sys.argv[1], print_info=True))

# SIG # Begin Windows Authenticode signature block
# MIIoZwYJKoZIhvcNAQcCoIIoWDCCKFQCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAeDLCYtpdSLLpP
# +G81kJMYnbHMTV1faFIh+YpEgfAWSKCCDZowggYYMIIEAKADAgECAhMzAAAEbLAG
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
# ARUwLwYJKoZIhvcNAQkEMSIEIPRDldAZb2rJhRqlJtJO25U//j8O4HUkhGVMTg35
# HTE3MEIGCisGAQQBgjcCAQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBho
# dHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEANCxNQ8fY
# CBxIWGQNoBMAw2/HG0ysbEPQggdcgV6Qgv9v37mK8MLiIzdx/kSxPST/uGc6IwUC
# M6WHo1uZ4oMihm+O1pxPipCzz9MSoJCvO6E1tGMhF/aN4FoqEJlIp+mhNlMdVR0C
# AhKXoo8CKAcIUTedDCHzYR7/JCxq5H1ktUuIwCqg4eGyy8BcWaVdoH+eiNdnKNim
# 8KmriS63Y9xDo0kexYW3LJexq9B+02wUszLf3ZyTZlRIA6iDf55lqq4Lm/bgB2/c
# AB9KP5IDBSRzaXwKHsWiAj3fCY5FDjEx1LAw4fWHv4Glotq0giMWCW54NFYvZLet
# X1Fp5nLEOTvliaGCF60wghepBgorBgEEAYI3AwMBMYIXmTCCF5UGCSqGSIb3DQEH
# AqCCF4YwgheCAgEDMQ8wDQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCC
# AUkEggFFMIIBQQIBAQYKKwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCBgZ1wn
# 8vjz3lrdo1xjCPIbOay0Q5dBJ84fgSGgIU2p3QIGaO3v6zK/GBMyMDI1MTAxNjE2
# MTgwNS4wMTVaMASAAgH0oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
# V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
# IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRp
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo2NTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEfsw
# ggcoMIIFEKADAgECAhMzAAACFRgD04EHJnxTAAEAAAIVMA0GCSqGSIb3DQEBCwUA
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgyMFoX
# DTI2MTExMzE4NDgyMFowgdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xLTArBgNVBAsTJE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGlt
# aXRlZDEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjY1MUEtMDVFMC1EOTQ3MSUw
# IwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG
# 9w0BAQEFAAOCAg8AMIICCgKCAgEAw3HV3hVxL0lEYPV03XeNKZ517VIbgexhlDPd
# pXwDS0BYtxPwi4XYpZR1ld0u6cr2Xjuugdg50DUx5WHL0QhY2d9vkJSk02rE/75h
# cKt91m2Ih287QRxRMmFu3BF6466k8qp5uXtfe6uciq49YaS8p+dzv3uTarD4hQ8U
# T7La95pOJiRqxxd0qOGLECvHLEXPXioNSx9pyhzhm6lt7ezLxJeFVYtxShkavPoZ
# N0dOCiYeh4KgoKoyagzMuSiLCiMUW4Ue4Qsm658FJNGTNh7V5qXYVA6k5xjw5WeW
# dKOz0i9A5jBcbY9fVOo/cA8i1bytzcDTxb3nctcly8/OYeNstkab/Isq3Cxe1vq9
# 6fIHE1+ZGmJjka1sodwqPycVp/2tb+BjulPL5D6rgUXTPF84U82RLKHV57bB8fHR
# pgnjcWBQuXPgVeSXpERWimt0NF2lCOLzqgrvS/vYqde5Ln9YlKKhAZ/xDE0TLIIr
# 6+I/2JTtXP34nfjTENVqMBISWcakIxAwGb3RB5yHCxynIFNVLcfKAsEdC5U2em0f
# AvmVv0sonqnv17cuaYi2eCLWhoK1Ic85Dw7s/lhcXrBpY4n/Rl5l3wHzs4vOIhu8
# 7DIy5QUaEupEsyY0NWqgI4BWl6v1wgse+l8DWFeUXofhUuCgVTuTHN3K8idoMbn8
# Q3edUIECAwEAAaOCAUkwggFFMB0GA1UdDgQWBBSJIXfxcqAwFqGj9jdwQtdSqadj
# 1zAfBgNVHSMEGDAWgBSfpxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSg
# UqBQhk5odHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3Nv
# ZnQlMjBUaW1lLVN0YW1wJTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEE
# YDBeMFwGCCsGAQUFBzAChlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3Bz
# L2NlcnRzL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNy
# dDAMBgNVHRMBAf8EAjAAMBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB
# /wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAgEAd42HtV+kGbvxzLBTC5O7vkCIBPy/
# BwpjCzeL53hAiEOebp+VdNnwm9GVCfYq3KMfrj4UvKQTUAaS5Zkwe1gvZ3ljSSnC
# OyS5OwNu9dpg3ww+QW2eOcSLkyVAWFrLn6Iig3TC/zWMvVhqXtdFhG2KJ1lSbN22
# 2csY3E3/BrGluAlvET9gmxVyyxNy59/7JF5zIGcJibydxs94JL1BtPgXJOfZzQ+/
# 3iTc6eDtmaWT6DKdnJocp8wkXKWPIsBEfkD6k1Qitwvt0mHrORah75SjecOKt4oW
# ayVLkPTho12e0ongEg1cje5fxSZGthrMrWKvI4R7HEC7k8maH9ePA3ViH0CVSSOe
# faPTGMzIhHCo5p3jG5SMcyO3eA9uEaYQJITJlLG3BwwGmypY7C/8/nj1SOhgx1Hg
# J0ywOJL9xfP4AOcWmCfbsqgGbCaC7WH5sINdzfMar8V7YNFqkbCGUKhc8GpIyE+M
# KnyVn33jsuaGAlNRg7dVRUSoYLJxvUsw9GOwyBpBwbE9sqOLm+HsO00oF23PMio7
# WFXcFTZAjp3ujihBAfLrXICgGOHPdkZ042u1LZqOcnlr3XzvgMe+mPPyasW8f0rt
# zJj3V5E/EKiyQlPxj9Mfq2x9himnlXWGZCVPeEBROrNbDYBfazTyLNCOTsRtksOS
# V3FBtPnpQtLN754wggdxMIIFWaADAgECAhMzAAAAFcXna54Cm0mZAAAAAAAVMA0G
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
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo2NTFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEB
# MAcGBSsOAwIaAxUAj6eTejbuYE1Ifjbfrt6tXevCUSCggYMwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybETowIhgP
# MjAyNTEwMTYwNjM3NDZaGA8yMDI1MTAxNzA2Mzc0NlowdDA6BgorBgEEAYRZCgQB
# MSwwKjAKAgUA7JsROgIBADAHAgEAAgIByjAHAgEAAgIS/DAKAgUA7JxiugIBADA2
# BgorBgEEAYRZCgQCMSgwJjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIB
# AAIDAYagMA0GCSqGSIb3DQEBCwUAA4IBAQAD2kBUctvWki8mPLTaiVkUtvorDEZf
# rFGPWv2227/7GuZXLUcKWusVB+j1iGNfUxFuvemMHrzQ9fpqYtzvwiFHifT29L9f
# rVADlx4u8kfhW/1HHrvSEi/3QvD52zxF44GsgKLAXiJGKt3CeqZ+43+1OArcPOGI
# bRwq1Fek4Ic2yYB/bjF41elF+Mls0phQHlB1h/UUDjegMamKhivVv7p4Oc161UFo
# MQU5DQwCuI7n/9BE7kxVhPgQyrXVxRwElBf3Gh9Ms3GqEEb6aVVMTEKmWjFUcDDN
# CbOlFVt6UAHkZetaKHN+eDIYcZCy4FkL5XxaafoTOdD3Kq07LNWKtUjKMYIEDTCC
# BAkCAQEwgZMwfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAO
# BgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
# MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIVGAPT
# gQcmfFMAAQAAAhUwDQYJYIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsq
# hkiG9w0BCRABBDAvBgkqhkiG9w0BCQQxIgQgmqwhtQZKsjtNTZqzZvsUv0jJPIVt
# /R+O9YGaEu0rqAkwgfoGCyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCBwEPR2PDrT
# FLcrtQsKrUi7oz5JNRCF/KRHMihSNe7sijCBmDCBgKR+MHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwAhMzAAACFRgD04EHJnxTAAEAAAIVMCIEIAAjsVUx4p+k
# 2IOYoaN7h74ovmr4LEi39MmxguPb/EEIMA0GCSqGSIb3DQEBCwUABIICAGjOAuBO
# 0btmw/78nAQVvweMoDW5EhlIbHnLuojsrHuuwPggYSOoScse5Zd2eik2liMCqPGF
# auzZnuu4l8s7petjOcX2+n0SfqCvImiW5zWfL/SbkuP4Djgcx2zD0gb/69Xdu5Ba
# xurCvrdnsF6ZQAIdpGuTlOjIxsZEz0MUc5SdmEzBug1FuykzDU6d7YjCeAk1GDWY
# PnJK3jeLp36jWd+cnF0y7NRZb0lwaq1j9RUSqcfVGSpR2iMkNUEntE5QsxAcpJvZ
# g6VdUytzw2jMraj1TgfhegE2hIu7TWaU/h+YnJqRvKYAP7A1pJbXKWAoNcAppcII
# LwOpgBr/4/Vvpb/7TRtt4m/IikLEmg/4tzioeLgLBNBX7uGXHSMRu1+qWbGzjPYG
# +xlY0DHfC3KsWo0bNvF0hmQIvu2MwURnLORBhex1xE3dx9v1hHbiDlAAGe+cnI9k
# gXPcAI/fGGP0qD2wsYN8jgQjqfLuvxxwdGhRmtiJ5xZ9K2oxzGViBX+KvEIwB4wv
# +E3hOwFbp5UwNeghgzYNeZcjbLB6qnCPLugoJ1KiG51dEPyiZzN3tdo6lJEg7/8r
# d5zdlMSlhw6rmiEIkkh7jFVexrjfo7+YKHJM5ouJk5oXcSLzckhTAR6Q0psTsHpN
# kKrgRaEl8Oo929825c3ErqgHVKBJABRdgxv4
# SIG # End Windows Authenticode signature block