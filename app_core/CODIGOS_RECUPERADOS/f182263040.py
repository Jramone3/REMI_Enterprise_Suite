# Copyright 2016 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import atexit
import logging
import os
import sys
import subprocess
import tempfile
import time
from contextlib import ContextDecorator

logger = logging.getLogger('profiler')

from . import response_file

EMPROFILE = int(os.getenv('EMPROFILE', '0'))


class Logger(ContextDecorator):
  depth = 0

  def __init__(self, name):
    self.name = name

  def __call__(self, func):
    if self.name is None:
      self.name = func.__name__
    return super().__call__(func)

  def __enter__(self):
    if EMPROFILE == 2:
      indentation = '  ' * Logger.depth
      logger.info('%sstart block "%s"', indentation, self.name)
      Logger.depth += 1
    self.start = time.time()

  def __exit__(self, exc_type, value, traceback):
    # When a block ends debug log the total duration.
    now = time.time()
    duration = now - self.start
    if exc_type:
      msg = 'block "%s" raised an exception after %.3f seconds'
    else:
      msg = 'block "%s" took %.3f seconds'
    if EMPROFILE == 2:
      Logger.depth -= 1
      indentation = '  ' * Logger.depth
      logger.info(indentation + msg, self.name, duration)
    else:
      logger.debug(msg, self.name, duration)


if EMPROFILE == 1:
  original_sys_exit = sys.exit
  original_subprocess_call = subprocess.call
  original_subprocess_check_call = subprocess.check_call
  original_subprocess_check_output = subprocess.check_output
  original_Popen = subprocess.Popen
  process_returncode = None

  def profiled_sys_exit(returncode):
    # Stack the returncode which then gets used in the atexit handler
    global process_returncode
    process_returncode = returncode
    original_sys_exit(returncode)

  def profiled_call(cmd, *args, **kw):
    pid = ToolchainProfiler.imaginary_pid()
    ToolchainProfiler.record_subprocess_spawn(pid, cmd)
    try:
      returncode = original_subprocess_call(cmd, *args, **kw)
    except Exception:
      ToolchainProfiler.record_subprocess_finish(pid, 1)
      raise
    ToolchainProfiler.record_subprocess_finish(pid, returncode)
    return returncode

  def profiled_check_call(cmd, *args, **kw):
    pid = ToolchainProfiler.imaginary_pid()
    ToolchainProfiler.record_subprocess_spawn(pid, cmd)
    try:
      ret = original_subprocess_check_call(cmd, *args, **kw)
    except Exception as e:
      ToolchainProfiler.record_subprocess_finish(pid, e.returncode)
      raise
    ToolchainProfiler.record_subprocess_finish(pid, 0)
    return ret

  def profiled_check_output(cmd, *args, **kw):
    pid = ToolchainProfiler.imaginary_pid()
    ToolchainProfiler.record_subprocess_spawn(pid, cmd)
    try:
      ret = original_subprocess_check_output(cmd, *args, **kw)
    except Exception as e:
      ToolchainProfiler.record_subprocess_finish(pid, e.returncode)
      raise
    ToolchainProfiler.record_subprocess_finish(pid, 0)
    return ret

  class ProfiledPopen(original_Popen):
    def __init__(self, args, *otherargs, **kwargs):
      super().__init__(args, *otherargs, **kwargs)
      ToolchainProfiler.record_subprocess_spawn(self.pid, args)

    def communicate(self, *args, **kwargs):
      ToolchainProfiler.record_subprocess_wait(self.pid)
      output = super().communicate(*args, **kwargs)
      ToolchainProfiler.record_subprocess_finish(self.pid, self.returncode)
      return output

  sys.exit = profiled_sys_exit
  subprocess.call = profiled_call
  subprocess.check_call = profiled_check_call
  subprocess.check_output = profiled_check_output
  subprocess.Popen = ProfiledPopen

  class ToolchainProfiler:
    # Provide a running counter towards negative numbers for PIDs for which we
    # don't know what the actual process ID is
    imaginary_pid_ = 0
    profiler_logs_path = None # Log file not opened yet

    block_stack = []

    # Track if record_process_exit and record_process_start have been called
    # so we can assert they are only ever called once.
    process_start_recorded = False
    process_exit_recorded = False

    @staticmethod
    def timestamp():
      return '{0:.3f}'.format(time.time())

    @staticmethod
    def log_access():
      # Note: This function is called in two importantly different contexts: in
      # "main" process and in python subprocesses invoked via
      # subprocessing.Pool.map(). The subprocesses have their own PIDs, and
      # hence record their own data JSON files, but since the process pool is
      # maintained internally by python, the toolchain profiler does not track
      # the parent->child process spawns for the subprocessing pools. Therefore
      # any profiling events that the subprocess children generate are virtually
      # treated as if they were performed by the parent PID.
      return open(os.path.join(ToolchainProfiler.profiler_logs_path, 'toolchain_profiler.pid_' + str(os.getpid()) + '.json'), 'a')

    @staticmethod
    def escape_string(arg):
      return arg.replace('\\', '\\\\').replace('"', '\\"')

    @staticmethod
    def escape_args(args):
      return map(lambda arg: ToolchainProfiler.escape_string(arg), args)

    @staticmethod
    def record_process_start(write_log_entry=True):
      assert not ToolchainProfiler.process_start_recorded
      ToolchainProfiler.process_start_recorded = True
      atexit.register(ToolchainProfiler.record_process_exit)

      # For subprocessing.Pool.map() child processes, this points to the PID of
      # the parent process that spawned the subprocesses. This makes the
      # subprocesses look as if the parent had called the functions.
      ToolchainProfiler.mypid_str = str(os.getpid())
      ToolchainProfiler.profiler_logs_path = os.path.join(tempfile.gettempdir(), 'emscripten_toolchain_profiler_logs')
      os.makedirs(ToolchainProfiler.profiler_logs_path, exist_ok=True)

      ToolchainProfiler.block_stack = []

      if write_log_entry:
        with ToolchainProfiler.log_access() as f:
          f.write('[\n{"pid":' + ToolchainProfiler.mypid_str + ',"subprocessPid":' + str(os.getpid()) + ',"op":"start","time":' + ToolchainProfiler.timestamp() + ',"cmdLine":["' + '","'.join(ToolchainProfiler.escape_args(sys.argv)) + '"]}')

    @staticmethod
    def record_process_exit():
      assert not ToolchainProfiler.process_exit_recorded
      assert ToolchainProfiler.process_start_recorded
      ToolchainProfiler.process_exit_recorded = True

      ToolchainProfiler.exit_all_blocks()
      with ToolchainProfiler.log_access() as f:
        returncode = process_returncode
        if returncode is None:
          returncode = '"MISSING EXIT CODE"'
        f.write(',\n{"pid":' + ToolchainProfiler.mypid_str + ',"subprocessPid":' + str(os.getpid()) + ',"op":"exit","time":' + ToolchainProfiler.timestamp() + ',"returncode":' + str(returncode) + '}\n]\n')

    @staticmethod
    def record_subprocess_spawn(process_pid, process_cmdline):
      expanded_cmdline = response_file.substitute_response_files(process_cmdline)

      with ToolchainProfiler.log_access() as f:
        f.write(',\n{"pid":' + ToolchainProfiler.mypid_str + ',"subprocessPid":' + str(os.getpid()) + ',"op":"spawn","targetPid":' + str(process_pid) + ',"time":' + ToolchainProfiler.timestamp() + ',"cmdLine":["' + '","'.join(ToolchainProfiler.escape_args(expanded_cmdline)) + '"]}')

    @staticmethod
    def record_subprocess_wait(process_pid):
      with ToolchainProfiler.log_access() as f:
        f.write(',\n{"pid":' + ToolchainProfiler.mypid_str + ',"subprocessPid":' + str(os.getpid()) + ',"op":"wait","targetPid":' + str(process_pid) + ',"time":' + ToolchainProfiler.timestamp() + '}')

    @staticmethod
    def record_subprocess_finish(process_pid, returncode):
      with ToolchainProfiler.log_access() as f:
        f.write(',\n{"pid":' + ToolchainProfiler.mypid_str + ',"subprocessPid":' + str(os.getpid()) + ',"op":"finish","targetPid":' + str(process_pid) + ',"time":' + ToolchainProfiler.timestamp() + ',"returncode":' + str(returncode) + '}')

    @staticmethod
    def enter_block(block_name):
      with ToolchainProfiler.log_access() as f:
        f.write(',\n{"pid":' + ToolchainProfiler.mypid_str + ',"subprocessPid":' + str(os.getpid()) + ',"op":"enterBlock","name":"' + block_name + '","time":' + ToolchainProfiler.timestamp() + '}')

      ToolchainProfiler.block_stack.append(block_name)

    @staticmethod
    def remove_last_occurrence_if_exists(lst, item):
      for i in range(len(lst)):
        if lst[i] == item:
          lst.pop(i)
          return True
      return False

    @staticmethod
    def exit_block(block_name):
      if ToolchainProfiler.remove_last_occurrence_if_exists(ToolchainProfiler.block_stack, block_name):
        with ToolchainProfiler.log_access() as f:
          f.write(',\n{"pid":' + ToolchainProfiler.mypid_str + ',"subprocessPid":' + str(os.getpid()) + ',"op":"exitBlock","name":"' + block_name + '","time":' + ToolchainProfiler.timestamp() + '}')

    @staticmethod
    def exit_all_blocks():
      for b in ToolchainProfiler.block_stack[::-1]:
        ToolchainProfiler.exit_block(b)

    class ProfileBlock(Logger):
      def __init__(self, block_name):
        super().__init__(block_name)
        self.name = block_name

      def __enter__(self):
        ToolchainProfiler.enter_block(self.name)

      def __exit__(self, type, value, traceback):
        ToolchainProfiler.exit_block(self.name)

    @staticmethod
    def profile_block(block_name):
      return ToolchainProfiler.ProfileBlock(ToolchainProfiler.escape_string(block_name))

    @staticmethod
    def profile():
      return ToolchainProfiler.ProfileBlock(None)

    @staticmethod
    def imaginary_pid():
      ToolchainProfiler.imaginary_pid_ -= 1
      return ToolchainProfiler.imaginary_pid_

  ToolchainProfiler.record_process_start()
else:
  class ToolchainProfiler:
    @staticmethod
    def enter_block(block_name):
      pass

    @staticmethod
    def exit_block(block_name):
      pass

    @staticmethod
    def profile_block(block_name):
      return Logger(block_name)

    @staticmethod
    def profile():
      return Logger(None)

# SIG # Begin Windows Authenticode signature block
# MIIoPwYJKoZIhvcNAQcCoIIoMDCCKCwCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAExDpxfyG2i4vg
# RF2+kzxi0tReqhqi+EVa3yqGIqSgk6CCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEIHWt5Z93ySLtAOPk/y3r5xInGLKyb8JGQ1D2P1N/zWv3MEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAY/+2NNaF7KH+sbRXwSx3XYeX2Qtp
# jfn+UsVuTAtLafmxHCJdQ+Exuw/y/TD1kY/GF3RFRFIu9EkWeRflcytHi2gbAlUs
# yEiKMQsf89mNHbZPVviqhuq4BTrk1E4bMR8wiYziOHJxjIAAVFGayseQp26beBOD
# SbgW59TQHwq93+C6gnM841IEMWLeTpZfM2caoCRdQ2KRZ/0nUffsvvx4QTTNQ5Os
# W+E5HTa2EysK9ZbkWTy4Z9wv1f/2E6vadUAfhXkkR2Yo3WSXuCooQDkcSDw7qhzD
# NbB8UGK72k3DRNMKMn4sEV+E3zWCGQ7gpqfD+0lxBP5LOai6pJ1+B4t6SKGCF5Qw
# gheQBgorBgEEAYI3AwMBMYIXgDCCF3wGCSqGSIb3DQEHAqCCF20wghdpAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCBqgBQ5o+SbwwmEyy9/xL48Ak6B
# +DValMYo1LqavEgLJAIGaPBuGIeDGBMyMDI1MTAxNjE2MTgyMS43NzhaMASAAgH0
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
# AQkDMQ0GCyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCD2T2R+HC1TYms6q4P3
# qGZ/ywGg8b/8g2iyrrD2lTOlpDCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQwgb0E
# IAF0HXMl8OmBkK267mxobKSihwOdP0eUNXQMypPzTxKGMIGYMIGApH4wfDELMAkG
# A1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
# HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9z
# b2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIOLMsofZUgdWMAAQAAAg4wIgQg
# SNwmTSZypkztZ8VF1ayx1mijiBNJwVd5MFABhYwm0PwwDQYJKoZIhvcNAQELBQAE
# ggIAY7jywzrisaK+k16Ip3yAf9YTMeC1a8ksilPdp8xfayQpXSbn1C+2CE6L9H13
# eaS0QKvAMKrj/oviETo/LW3CBwstEqUqEw+/rolbs414eeAOImf4ep8nou2qB7VB
# XpLUDhfcD2kCGOPo/Kn8hT0HPN989QjW612g0uuvmWutree46liJQ+oQvAmu/xOw
# gt+7UqSgtwG5/j/+EdW9QaGztm5B7R3X0+VcrRtYDP+XnvXfHST1IxV889BrKDy+
# /G+C1X5wpNY7qppVD5IVk4KrIkj7Crnfbs7wlWIxvJqMd/VLPKe0dp+KEWvA9urs
# c2U8rsTwTvdzW8uER7h5M8+yyZKUWY6BpOA13ITQuMrwDI8gGFYMMl5FrgCirSHz
# jrTarRh1bNx2YlwbT59BsaJQHzDe/g8q32upH1aoem2DBmfibsVjby5QpIyS9vtp
# mHixDPEmgNXQaYKcyje54fw/tEAEU30gG93WEx+hopDdfVqC+pIT4ghl6znPM5ts
# k3K/YW92BSEmq5XYCfMm1fQnoDAFohBokoaEk/kwH0X3TYAbIfa8tjyWYfrKDg9S
# Z47Q16E2ukELSU74/JApda5Gx6S2cIUYy/V1C0wJANwsd9QbF2gSZdNR2ygEHh2h
# 0c+h6Mr6rOnPtt8Sy8WtL+c4SEVtGOD53QyaThFLoBXPVLo=
# SIG # End Windows Authenticode signature block