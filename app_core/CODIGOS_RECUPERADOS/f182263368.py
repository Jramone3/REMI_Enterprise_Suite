#!/usr/bin/env python3

"""Find files in the test/ that are not referenced and can
be deleted.  This is a work in progress and still contains
false positives in the output."""

import os
import sys
import fnmatch
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))
test_dir = os.path.join(root_dir, 'test')
ignore_dirs = {
  'third_party',
  'metadce',
  'cmake',
  '__pycache__',
}
ignore_files = {
  'getValue_setValue_assert.out',
  'test_emsize.wasm',
  'legacy_exported_runtime_numbers_assert.out',
  'test_asyncify_during_exit_no_async.out',
}
ignore_root_patterns = ['runner.*', 'test_*.py']
ignore_root_files = {
  'check_clean.py',
  'jsrun.py',
  'clang_native.py',
  'common.py',
  'parallel_testsuite.py',
  'parse_benchmark_output.py',
  'malloc_bench.c',
}


def grep(string, subdir=''):
  cmd = subprocess.run(['git', 'grep', '--quiet', string, 'test/' + subdir], check=False)
  return not cmd.returncode


def check_file(dirpath, filename):
  normpath = os.path.normpath(os.path.join(dirpath, filename))
  relpath = os.path.relpath(normpath, test_dir)
  stem, ext = os.path.splitext(normpath)

  # Ignore explicit exceptions
  if dirpath == test_dir:
    if filename in ignore_root_files:
      return
    if any(fnmatch.fnmatch(filename, pattern) for pattern in ignore_root_patterns):
      return

  if os.path.basename(filename) in ignore_files:
    return

  # .out files are live if and only if they live alongside a live source file
  if ext == '.out' and os.path.exists(stem + '.cpp') or os.path.exists(stem + '.c'):
    return

  # Files under 'core' can be live if they are find in a `do_core_test` call.
  parts = relpath.split(os.path.sep)
  if parts[0] == 'core':
    pattern = "do_core_test('" + os.path.join(*parts[1:]) + "'"
    if grep(pattern, 'test_core.py'):
      return
    pattern = "'" + os.path.basename(stem) + "'"
    if grep(pattern, 'test_core.py'):
      return

  # Files under 'other' can be live if they are find in a `do_other_test` call.
  if parts[0] == 'other':
    pattern = "do_other_test('" + os.path.join(*parts[1:]) + "'"
    if grep(pattern, 'test_other.py'):
      return

  # Files under 'code_size' are live if the stem can be found quoted in test code.
  if parts[0] == 'code_size':
    if ext == '.json' and grep("'" + os.path.basename(stem) + "'"):
      return

  # test_asan builds it pathnames programatically based on the basename, so just
  # search for the basename.
  if filename.startswith('test_asan_'):
    relpath = os.path.basename(relpath)

  if grep(relpath):
    return

  print('Unreferenced: ' + os.path.relpath(normpath, root_dir))


def main(args):
  if len(args):
    for arg in args:
      check_file(test_dir, arg)
    return 0

  for dirpath, dirnames, filenames in os.walk(test_dir):
    if os.path.basename(dirpath) in ignore_dirs:
      dirnames.clear()
      filenames.clear()
      continue
    for filename in filenames:
      check_file(dirpath, filename)

  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))

# SIG # Begin Windows Authenticode signature block
# MIIoZwYJKoZIhvcNAQcCoIIoWDCCKFQCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCBXhMdnFk/ScOXq
# ac3M8C2ekd6rwKEV3YR9ElL7C74ONKCCDZowggYYMIIEAKADAgECAhMzAAAEbLAG
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
# ARUwLwYJKoZIhvcNAQkEMSIEIAL2TdwdR4sRn5Pz4rt38upODaLrIvfrIP2oc6gD
# Up4ZMEIGCisGAQQBgjcCAQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBho
# dHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAN7LdQF8J
# 9uidpuwusA84LtlMBqa7LGcJRedWiGO7zQPjMfjU2UJXHg1UYYbXnaqJhbJJZjwR
# +DQCKwyQp0J2vIV2emMY1havACHXJh0lrOib9xYU0xJRsVoRF/xv8tqn0sORSoBH
# CBUZWcYB8hRqzvH34sFI2RrxFYEdczCb/e7YcBsr5AmaJaGBWuXaBZE1ripY1vwG
# cgHjzYy/Z9psKNF8NfAysPeTzmSMGYbFt1W8LDh7a/sYrzHjr9XYaTr2WEkIHAeJ
# TvjhNVQs37fVgsqcAPMCS2d8dabd7NPKwF/LGjFVNww8k5jpWbY3qhiFniLoUwjY
# sjIt4mbfVezYj6GCF60wghepBgorBgEEAYI3AwMBMYIXmTCCF5UGCSqGSIb3DQEH
# AqCCF4YwgheCAgEDMQ8wDQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCC
# AUkEggFFMIIBQQIBAQYKKwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCBIrNzW
# XscnTD65kupxzyWBCF1Wla8Tcz+g29U/qmngIQIGaN7ZDUGtGBMyMDI1MTAxNjE2
# MTcxOC42MjVaMASAAgH0oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMK
# V2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
# IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRp
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1NzFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEfsw
# ggcoMIIFEKADAgECAhMzAAACFtaTzvuTH+3hAAEAAAIWMA0GCSqGSIb3DQEBCwUA
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgyMloX
# DTI2MTExMzE4NDgyMlowgdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xLTArBgNVBAsTJE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGlt
# aXRlZDEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjU3MUEtMDVFMC1EOTQ3MSUw
# IwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG
# 9w0BAQEFAAOCAg8AMIICCgKCAgEAv2gMH2/jMTYMazrMpHcKp2gvaq1lknMuq8VS
# hK15JWEAAlFPkdJm81RlPVitzr+eocrzZ+2M2NrPuUoFZLGVA5k6dXOIsMFbv8Kd
# ssHDSAe1SiwtqZdOiYiLFp25TlgWwhf1plSBalJiMUpTG5xnZ3epa42K++QDBO3m
# pAYg9dYyLzIRevXk8Mgn5V14oWXedi5NfGqmwZwR2DT1DtDNNhsi09L4DMD/Z82Y
# c84haKTszLs1IFDxmNg0M1sDj3syAeH0ApXb8pIjH8mcDM8UH2rFV/fFDgLRjZZd
# vhPv9T68hW+DijevmDe/oysyPt9H8bqyNOp3vihUbB0OFFoPq5OlMu6BGeU9mWi/
# IR3Yx0bT2mNdzuMBybeyGf6l5xFiwuycWFCtn4VfiA2ZyAftmQAKaP2a92u0+bmS
# idHXv3vN136EFtt+b3Hbwmd1ZNYqSSJ9DFihN3ZH/fyNbQJpVe+DVVNygYreJvli
# bZqOMxvAS/nAZFXjUVDLzOHRYoBzERFaX4nb4wigty8UefGyARetZI24vrZOYc/c
# DHbFKXdSqKaUUjdSRNiNrcUXMeOBPySPeT12mehLf/AUwq1vEWyOL9k6HyiNYuOg
# SJbpikmR8EbNeP03+hovK2GLChTURzKX9o2F0gKv/Qw2eG3QdnEC2E9h9SMU7dcl
# qPtXWTcCAwEAAaOCAUkwggFFMB0GA1UdDgQWBBQEMJr2Wp/vbkoHARzwyDBf2453
# +TAfBgNVHSMEGDAWgBSfpxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSg
# UqBQhk5odHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3Nv
# ZnQlMjBUaW1lLVN0YW1wJTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEE
# YDBeMFwGCCsGAQUFBzAChlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3Bz
# L2NlcnRzL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNy
# dDAMBgNVHRMBAf8EAjAAMBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB
# /wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAgEAwzLCEkKyPwWT3YBte/UnTkDHD+zn
# g4Z+0O63IuCFOs8Ndnp5J39opYtzGaW7JVfwFiqXLap9ACf3801TLXaJIC/kt/JL
# JgUTm/aN5I/WNEz0Lkg3VwyDSu+rScw27GwvjLXgJ6MXDF8XdQ82SZe3h17EV7Bd
# qpHUimsGWRd82pncaC7gPauqNJojfu2PrhvL87vZDGzYnWSdn24hcfVEHdrUxQo2
# usEkZ54XnXEWj4XvufYtpcY0SveFyjgA9kMdFRydpAB1DGqOBo9rviUBUddXzUbN
# 8hpcC88lMMNSB0c3JBGHT6LfMPRkFZqwRwoNWJD5p9JgowxY+PBLoAMpGr8Yu602
# ITkhGaHK14AF+YASJJzbHR69Acyf4YBUKnp5Pv1FMcZ38pabosHFKBfOURCZuoPr
# THvGAm9tVTo9uEqmescWWgzm5G4DJfU5zp3maBKpFVQ2nrh8HDuxxSEjE8xc6z+0
# 7VHdOuct6B+Kw+iT650iKGvbBe3lSyScJ+CLg+vodIBEYNK/uH+nEJ/AYrx2c/RW
# jqDFQ7k37lJt0Mcm7gNKZjVrFKlZ5nfw8Kg8buUfh9WWwMpreq5P3wiPMv6PZQQ/
# vYWi9NU9FlxQAfuUcMEtjNZ4nWiOE3WaeJJVQWomjLVMycmLaFI97d61Vv31tLL5
# vqUYy4LfqsMUUbEwggdxMIIFWaADAgECAhMzAAAAFcXna54Cm0mZAAAAAAAVMA0G
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
# b25zIExpbWl0ZWQxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjo1NzFBLTA1RTAt
# RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEB
# MAcGBSsOAwIaAxUA6UTLnqhqEB2Z1pfHwWFPiQB7WTuggYMwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybI5wwIhgP
# MjAyNTEwMTYwNzU2MTJaGA8yMDI1MTAxNzA3NTYxMlowdDA6BgorBgEEAYRZCgQB
# MSwwKjAKAgUA7JsjnAIBADAHAgEAAgIFPDAHAgEAAgIXKjAKAgUA7Jx1HAIBADA2
# BgorBgEEAYRZCgQCMSgwJjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIB
# AAIDAYagMA0GCSqGSIb3DQEBCwUAA4IBAQBcoAd4A85XsHFyVjKh/eWCKw2/jt3V
# rr6v45VZXL4KQIQ0KLwrJB28PfNYKQ6+T5hhTFd1385Bl2FSP5eYxg8XXgxD/dWN
# f4EUwhVerrIHb+Xv+B07uEIigQ5SdLnxbk9hkDKyVN92oRGVc6JD6KMgtIL6hBTr
# Kfvp4P9ZYTfHOElN54gv1TC1dIuxv0XBcZL5G3QhA9qM4jGYy/8IrpLuTuCJOWO4
# oEMwHZhELlJPjFo+8dwarjwtI6MXGB1nR2s0ddR68OegZuFSlWsevJghaF8jfuxL
# Fq1eucX6K0ILQjrV77g9O9rrYn7afOCUnBKoSbULzslAAq4Diwwt6nr8MYIEDTCC
# BAkCAQEwgZMwfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAO
# BgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
# MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIW1pPO
# +5Mf7eEAAQAAAhYwDQYJYIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsq
# hkiG9w0BCRABBDAvBgkqhkiG9w0BCQQxIgQgnNy5iG9VDK7mjWPvFFPUDcQ9QT1k
# GBuZ4Z6Veg/FrSUwgfoGCyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCCdpN7UuFJ4
# acsslFfWpSZY3oOnEd4M75GFiYWdCwYiDzCBmDCBgKR+MHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwAhMzAAACFtaTzvuTH+3hAAEAAAIWMCIEIKW91lxCBY+r
# q1EsaM/Kg6TcLuJ4I5DVB4hKyuFVu5EWMA0GCSqGSIb3DQEBCwUABIICAHjb+dWH
# zR3bXFrH4Bd7bppiK3ceZb9+S9HJvIIz21rGDzueUATlc3aDoT8JHJ/pao6NbmEU
# QF5lpiZ7lHZrEbTvYkHjJKMtP+RNl6EjMbIkyjPHn4T39fR0EKB5EWdVSKLtdpgJ
# 8KjQ2XqdOQ4rDkeeTzCtajzOcdz1uua1aMmuqr2BOjYAyX+bbLlU2a4Atgzuyio9
# 9WP8YjLImRgfNMq0H7aWKfSmDviMFJpJ8hrXn/R1lIqhTALH4FnBlqnwOQ08qoj0
# QFB6o0CIeEfArS3c/hwh/Lh9M5RwKmZ+Zlt32Z/BvBUnDpJbuvLB+Y6LsrgnSv6p
# VhxWxbQYKTvRQ7mQ+wy+z8US26dpyh0PcGIVNMQx4CKYUQ10nAKD2LDgGjS5eBO6
# H3bmiLqyRuCw642xaPjciCiBc8wo61RZu7f9LlwBqEn1TXnYrYOTuNYl3iWZ3Ji4
# bK2al0yS0ulA2McrMPo6Z6dwAGAncnMACp6xaExOGs2WLc1Xlv3Y+tV1K+ULRCRa
# BJgWtdJxTNZctEW6sK7HjQxvVRSpnz+qkPd2+jepcQcj3cxUpIWhDUq1bjsDyyxg
# XLxn3hDojBghPFjmRcTYFNcXRRd+FqwMJbPyLVrTTpYrgdfhxHVwVSA01/hOqvi+
# 9s8X65uitDj/6K0n/JvPIlyP4qUvCvm7Hlgj
# SIG # End Windows Authenticode signature block