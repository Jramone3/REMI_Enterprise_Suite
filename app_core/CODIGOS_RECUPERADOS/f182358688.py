# Copyright 2014 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import os

TAG = 'release-2.28.4'
HASH = '8dd593fd7d8660efdeb53b7d1706f5743eb68491a29eb0cf0c028d8f8b8a7945c0dc5bf1117b5e4e871d7622be277c0838d08cc6eabdecb563000dfcc0c94639'
SUBDIR = 'SDL-' + TAG

variants = {'sdl2-mt': {'PTHREADS': 1}}


def needed(settings):
  return settings.USE_SDL == 2


def get_lib_name(settings):
  return 'libSDL2' + ('-mt' if settings.PTHREADS else '') + '.a'


def get(ports, settings, shared):
  # get the port
  ports.fetch_project('sdl2', f'https://github.com/libsdl-org/SDL/archive/{TAG}.zip', sha512hash=HASH)

  def create(final):
    # copy includes to a location so they can be used as 'SDL2/'
    src_dir = os.path.join(ports.get_dir(), 'sdl2', SUBDIR)
    source_include_path = os.path.join(src_dir, 'include')
    ports.install_headers(source_include_path, target='SDL2')

    # build
    srcs = '''SDL.c SDL_assert.c SDL_dataqueue.c SDL_error.c SDL_guid.c SDL_hints.c SDL_list.c SDL_log.c
    SDL_utils.c atomic/SDL_atomic.c atomic/SDL_spinlock.c audio/SDL_audio.c audio/SDL_audiocvt.c
    audio/SDL_audiodev.c audio/SDL_audiotypecvt.c audio/SDL_mixer.c audio/SDL_wave.c cpuinfo/SDL_cpuinfo.c
    dynapi/SDL_dynapi.c events/SDL_clipboardevents.c events/SDL_displayevents.c events/SDL_dropevents.c
    events/SDL_events.c events/SDL_gesture.c events/SDL_keyboard.c events/SDL_keysym_to_scancode.c
    events/SDL_scancode_tables.c events/SDL_mouse.c events/SDL_quit.c
    events/SDL_touch.c events/SDL_windowevents.c file/SDL_rwops.c haptic/SDL_haptic.c
    joystick/controller_type.c joystick/SDL_gamecontroller.c joystick/SDL_joystick.c
    power/SDL_power.c render/SDL_d3dmath.c render/SDL_render.c
    render/SDL_yuv_sw.c render/direct3d/SDL_render_d3d.c render/direct3d11/SDL_render_d3d11.c
    render/opengl/SDL_render_gl.c render/opengl/SDL_shaders_gl.c render/opengles/SDL_render_gles.c
    render/opengles2/SDL_render_gles2.c render/opengles2/SDL_shaders_gles2.c
    render/psp/SDL_render_psp.c render/software/SDL_blendfillrect.c render/software/SDL_blendline.c
    render/software/SDL_blendpoint.c render/software/SDL_drawline.c render/software/SDL_drawpoint.c
    render/software/SDL_render_sw.c render/software/SDL_rotate.c render/software/SDL_triangle.c
    sensor/SDL_sensor.c sensor/dummy/SDL_dummysensor.c
    stdlib/SDL_crc16.c stdlib/SDL_crc32.c stdlib/SDL_getenv.c stdlib/SDL_iconv.c stdlib/SDL_malloc.c
    stdlib/SDL_qsort.c stdlib/SDL_stdlib.c stdlib/SDL_string.c stdlib/SDL_strtokr.c
    thread/SDL_thread.c timer/SDL_timer.c
    video/SDL_RLEaccel.c video/SDL_blit.c video/SDL_blit_0.c video/SDL_blit_1.c video/SDL_blit_A.c
    video/SDL_blit_N.c video/SDL_blit_auto.c video/SDL_blit_copy.c video/SDL_blit_slow.c
    video/SDL_bmp.c video/SDL_clipboard.c video/SDL_egl.c video/SDL_fillrect.c video/SDL_pixels.c
    video/SDL_rect.c video/SDL_shape.c video/SDL_stretch.c video/SDL_surface.c video/SDL_video.c
    video/SDL_yuv.c video/emscripten/SDL_emscriptenevents.c
    video/emscripten/SDL_emscriptenframebuffer.c video/emscripten/SDL_emscriptenmouse.c
    video/emscripten/SDL_emscriptenopengles.c video/emscripten/SDL_emscriptenvideo.c
    audio/emscripten/SDL_emscriptenaudio.c video/dummy/SDL_nullevents.c
    video/dummy/SDL_nullframebuffer.c video/dummy/SDL_nullvideo.c video/yuv2rgb/yuv_rgb.c
    audio/disk/SDL_diskaudio.c audio/dummy/SDL_dummyaudio.c loadso/dlopen/SDL_sysloadso.c
    power/emscripten/SDL_syspower.c joystick/emscripten/SDL_sysjoystick.c
    filesystem/emscripten/SDL_sysfilesystem.c timer/unix/SDL_systimer.c haptic/dummy/SDL_syshaptic.c
    main/dummy/SDL_dummy_main.c locale/SDL_locale.c locale/emscripten/SDL_syslocale.c misc/SDL_url.c
    misc/emscripten/SDL_sysurl.c'''.split()
    thread_srcs = ['SDL_syscond.c', 'SDL_sysmutex.c', 'SDL_syssem.c', 'SDL_systhread.c', 'SDL_systls.c']
    thread_backend = 'generic' if not settings.PTHREADS else 'pthread'
    srcs += ['thread/%s/%s' % (thread_backend, s) for s in thread_srcs]

    srcs = [os.path.join(src_dir, 'src', s) for s in srcs]
    flags = ['-sUSE_SDL=0']
    includes = [ports.get_include_dir('SDL2')]
    if settings.PTHREADS:
      flags += ['-pthread']
    ports.build_port(src_dir, final, 'sdl2', srcs=srcs, includes=includes, flags=flags)

  return [shared.cache.get_lib(get_lib_name(settings), create, what='port')]


def clear(ports, settings, shared):
  shared.cache.erase_lib(get_lib_name(settings))


def process_args(ports):
  return ['-isystem', ports.get_include_dir('SDL2')]


def show():
  return 'sdl2 (-sUSE_SDL=2 or --use-port=sdl2; zlib license)'

# SIG # Begin Windows Authenticode signature block
# MIIoPwYJKoZIhvcNAQcCoIIoMDCCKCwCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCDr0BvZC67+NS7J
# sipqTZMz5TDbCBY3gD1OEPS3kH9EVKCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEIC1rwoMeDM1bLQ3tmpJU72TQu8Aml74K3uyfBXKdX4UVMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAsmG0Z6RLD71GsGiYydYJIy8L8bgB
# /cw4e5oa7uxwgTNJ2U44KF3Bbe7oIgYheOjkfQaRQLmlOYksDNw8+A51nJxPFF5n
# a4omHO9k42/MLdJYKqwFt5k3n9tuHXrB5K5TtO7s6Ttosm5u7/IwzdDlilCmbAld
# gVpPNLhJmo5mr+2T0e4J6CCFOFTPCBq6IR+K3O2zRfgTBu5qwclSEx+ggAPBiuTw
# OLo27gbusNOg60uiueGgvfv0nptAigVuCNTO+12ab2voomycf3IQzj4rNIt3s1Ai
# HPo39TVbLgxEaoaZ3r8FjlsQGGXj4eahWW2FlmqLc7CAe1EPLIorD0v9iaGCF5Qw
# gheQBgorBgEEAYI3AwMBMYIXgDCCF3wGCSqGSIb3DQEHAqCCF20wghdpAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCCuKrNSVH0V0eja8BkBi9mIqqsL
# UDYDV8+XWb6jhsecCwIGaPBElWEXGBMyMDI1MTAxNjE2MTcyMS45NzVaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046N0YwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHqMIIHIDCCBQigAwIBAgITMwAAAgbXvFE4
# mCPsLAABAAACBjANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQyNTBaFw0yNjA0MjIxOTQyNTBaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# N0YwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDpRIWbIM3Rlr39
# 7cjHaYx85l7I+ZVWGMCBCM911BpU6+IGWCqksqgqefZFEjKzNVDYC9YcgITAz276
# NGgvECm4ZfNv/FPwcaSDz7xbDbsOoxbwQoHUNRro+x5ubZhT6WJeU97F06+vDjAw
# /Yt1vWOgRTqmP/dNr9oqIbE5oCLYdH3wI/noYmsJVc7966n+B7UAGAWU2se3Lz+x
# dxnNsNX4CR6zIMVJTSezP/2STNcxJTu9k2sl7/vzOhxJhCQ38rdaEoqhGHrXrmVk
# EhSv+S00DMJc1OIXxqfbwPjMqEVp7K3kmczCkbum1BOIJ2wuDAbKuJelpteNZj/S
# 58NSQw6khfuJAluqHK3igkS/Oux49qTP+rU+PQeNuD+GtrCopFucRmanQvxISGNo
# xnBq3UeDTqphm6aI7GMHtFD6DOjJlllH1gVWXPTyivf+4tN8TmO6yIgB4uP00bH9
# jn/dyyxSjxPQ2nGvZtgtqnvq3h3TRjRnkc+e1XB1uatDa1zUcS7r3iodTpyATe2h
# gkVX3m4DhRzI6A4SJ6fbJM9isLH8AGKcymisKzYupAeFSTJ10JEFa6MjHQYYohoC
# F77R0CCwMNjvE4XfLHu+qKPY8GQfsZdigQ9clUAiydFmVt61hytoxZP7LmXbzjD0
# VecyzZoL4Equ1XszBsulAr5Ld2KwcwIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFO0w
# sLKdDGpT97cx3Iymyo/SBm4SMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQB23GZO
# fe9ThTUvD29i4t6lDpxJhpVRMme+UbyZhBFCZhoGTtjDdphAArU2Q61WYg3YVcl2
# RdJm5PUbZ2bA77zk+qtLxC+3dNxVsTcdtxPDSSWgwBHxTj6pCmoDNXolAYsWpvHQ
# FCHDqEfAiBxX1dmaXbiTP1d0XffvgR6dshUcqaH/mFfjDZAxLU1s6HcVgCvBQJlJ
# 7xEG5jFKdtqapKWcbUHwTVqXQGbIlHVClNJ3yqW6Z3UJH/CFcYiLV/e68urTmGti
# ZxGSYb4SBSPArTrTYeHOlQIj/7loVWmfWX2y4AGV/D+MzyZMyvFw4VyL0Vgq96Ez
# QKyteiVeBaVEjxQKo3AcPULRF4Uzz98P2tCM5XbFZ3Qoj9PLg3rgFXr0oJEhfh2t
# qUrhTJd13+i4/fek9zWicoshlwXgFu002ZWBVzASEFuqED48qyulZ/2jGJBcta+F
# dk2loP2K3oSj4PQQe1MzzVZO52AXO42MHlhm3SHo3/RhQ+I1A0Ny+9uAehkQH6Lr
# xkrVNvZG4f0PAKMbqUcXG7xznKJ0x0HYr5ayWGbHKZRcObU+/34ZpL9NrXOedVDX
# mSd2ylKSl/vvi1QwNJqXJl/+gJkQEetqmHAUFQkFtemi8MUXQG2w/RDHXXwWAjE+
# qIDZLQ/k4z2Z216tWaR6RDKHGkweCoDtQtzkHTCCB3EwggVZoAMCAQICEzMAAAAV
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
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjdG
# MDAtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQAEa0f118XHM/VNdqKBs4QXxNnN96CBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JtrxTAiGA8yMDI1MTAxNjEzMDQwNVoYDzIwMjUxMDE3MTMwNDA1WjB0MDoGCisG
# AQQBhFkKBAExLDAqMAoCBQDsm2vFAgEAMAcCAQACAh7xMAcCAQACAhNhMAoCBQDs
# nL1FAgEAMDYGCisGAQQBhFkKBAIxKDAmMAwGCisGAQQBhFkKAwKgCjAIAgEAAgMH
# oSChCjAIAgEAAgMBhqAwDQYJKoZIhvcNAQELBQADggEBAFD/+Gp2OXtYN7uS/Jn5
# 81aw1zHc5iNG5WXQuZTllAVo3lXovRoJ7OINnrIOjuohTStG2f7eS9Rfd4k2ZAJD
# AA89BiB/JzFjbrplHb1VdGf2i7Q5LehjpWfED7Yv6AUYaMVGt6F03n1tH+W3YwqK
# QMqupo7bWZ0qHqZW7Xm91PI80nUSJNWA9y4S5TYGLMSlpzdnsjeKhjWKlJinnHBo
# yX9W+PQ1UkTcSGAE1vlKAztGaQ485vN+P+jACOatNijh2N30Dt90xDEqlU1tbAPy
# HXrKlxOyd4Z7Feha5d7K+2G/dkLqqqVjngisjseHbZzBr9X0927uX3CcmBoG784W
# UusxggQNMIIECQIBATCBkzB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGlu
# Z3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBv
# cmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAIT
# MwAAAgbXvFE4mCPsLAABAAACBjANBglghkgBZQMEAgEFAKCCAUowGgYJKoZIhvcN
# AQkDMQ0GCyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCCs9k6JAa7S1yKGlLDE
# Y6ngRtZMgniDpWGTkDLAd4UYWjCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQwgb0E
# IODo9ZSIkZ6dVtKT+E/uZx2WAy7KiXM5R1JIOhNJf0vSMIGYMIGApH4wfDELMAkG
# A1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
# HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9z
# b2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIG17xROJgj7CwAAQAAAgYwIgQg
# /kdW4HW3Xdy4JmkiovZGomLQmY5owLH1f7nZgetIuNUwDQYJKoZIhvcNAQELBQAE
# ggIADeq9m4KPxI8WGKkhfzQZyw5G/wQP1Z0PxR+2Hohe1NMVSVX66Xp4r+mD6kMh
# HP4W7VrTzj3EP0NHXNNaWTUJ47XguPQYGjJvm0VoYwB3+IRzEQSBQi+Wgaq66ZEk
# F4amtxecOe8OlUeZlAacpfqGwZR0g1HJwbKixCaNTgFAIS4PSAn9AZG8r26UNElm
# QmCIGKPYelrpsWcIvet2cUQSQJs9ehB5R+nceWKMOHNBrBemwvwwwpUdOLwFr7dF
# +qCiCEONTU28rK1liqzzaevRsya+CiIlJwmib/woAGepBFOI4f7JD7RfYrWQ4ykC
# IiLAyD+/Fh8noVfMPD9jKfO7p3Lzfb03IDKVKYeCx7bYNiga2MIPu8CI02jt/gGB
# eBONWMe+LK9K3INSYHT0wwbmPP5iXMsorQuCiAI520XoMkcCfpYNqN7X/K1TbMaa
# nZ5b9O+Wpxd7aB0EJ8Q9UI4qfBAuAX4R6nRxA57OaT+aqXuxgvbLPvsc6+HoHjDU
# 4cfJg0X6C1q7ByzH+BPhFstqHSxtHcsoIqz3IBbE7RyP/dcsM3wTZQ/dNS6zRYjw
# hCxIXOYj+i84vs9jZjJUzoKrF+1E9dVRW4qWVdblM4CuXVY6wNzS/GNw8sKYWJCw
# 8erjYgjIxXJrcC5VPC5QDwRuMJBGI8cz5b0COD2KMQ6/+Po=
# SIG # End Windows Authenticode signature block