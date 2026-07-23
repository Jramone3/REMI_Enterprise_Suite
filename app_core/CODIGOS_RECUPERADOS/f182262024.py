#!/usr/bin/env python3
# Copyright 2017 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

# The DOM KeyboardEvent field 'code' contains a locale/language independent
# identifier of a pressed key on the keyboard, i.e. a "physical" keyboard code, which
# is often useful for games that want to provide a physical keyboard layout that does
# not get confused by the language setting the user has.

# For example, in Unreal Engine 4 developer mode, the physical keyboard key above the Tab
# but below the Esc key should open up the developer console, independent of which keyboard
# layout is active. This key produces the backquote (`) character on US keyboard layout,
# whereas on the Finnish/Swedish keyboard layout, it generates but the section sign (§)
# character. Other keyboard layouts might give different characters, and independent of
# which character is produced, we would like to generate a layout-agnostic identifier for
# the key at this physical location on the keyboard.

# The DOM KeyboardEvent field 'code' provides such a layout-agnostic identifier.
# Unfortunately this identifier is not an integral ID that could be used as an enum
# or #define, but it is a human-readable English language string that represents the
# physical key. This is very inconvenient for most applications.

# This utility script creates a mapping from the different documented values of the
# KeyboardEvent 'code' field, to integral IDs that can be easily used to identify
# physical key locations. This mapping is implemented by constructing a hash function
# that is a perfect hash (https://en.wikipedia.org/wiki/Perfect_hash_function) of the
# known strings.

# Use #include <emscripten/dom_pk_codes.h> in your code to access these IDs.

import sys
import random

input_strings = [
  (0x0, 'Unidentified',          'DOM_PK_UNKNOWN'),
  (0x1, 'Escape',                'DOM_PK_ESCAPE'),
  (0x2, 'Digit0',                'DOM_PK_0'),
  (0x3, 'Digit1',                'DOM_PK_1'),
  (0x4, 'Digit2',                'DOM_PK_2'),
  (0x5, 'Digit3',                'DOM_PK_3'),
  (0x6, 'Digit4',                'DOM_PK_4'),
  (0x7, 'Digit5',                'DOM_PK_5'),
  (0x8, 'Digit6',                'DOM_PK_6'),
  (0x9, 'Digit7',                'DOM_PK_7'),
  (0xA, 'Digit8',                'DOM_PK_8'),
  (0xB, 'Digit9',                'DOM_PK_9'),
  (0xC,  'Minus',                'DOM_PK_MINUS'),
  (0xD,  'Equal',                'DOM_PK_EQUAL'),
  (0xE,  'Backspace',            'DOM_PK_BACKSPACE'),
  (0xF,  'Tab',                  'DOM_PK_TAB'),
  (0x10, 'KeyQ',                 'DOM_PK_Q'),
  (0x11, 'KeyW',                 'DOM_PK_W'),
  (0x12, 'KeyE',                 'DOM_PK_E'),
  (0x13, 'KeyR',                 'DOM_PK_R'),
  (0x14, 'KeyT',                 'DOM_PK_T'),
  (0x15, 'KeyY',                 'DOM_PK_Y'),
  (0x16, 'KeyU',                 'DOM_PK_U'),
  (0x17, 'KeyI',                 'DOM_PK_I'),
  (0x18, 'KeyO',                 'DOM_PK_O'),
  (0x19, 'KeyP',                 'DOM_PK_P'),
  (0x1A, 'BracketLeft',          'DOM_PK_BRACKET_LEFT'),
  (0x1B, 'BracketRight',         'DOM_PK_BRACKET_RIGHT'),
  (0x1C, 'Enter',                'DOM_PK_ENTER'),
  (0x1D, 'ControlLeft',          'DOM_PK_CONTROL_LEFT'),
  (0x1E, 'KeyA',                 'DOM_PK_A'),
  (0x1F, 'KeyS',                 'DOM_PK_S'),
  (0x20, 'KeyD',                 'DOM_PK_D'),
  (0x21, 'KeyF',                 'DOM_PK_F'),
  (0x22, 'KeyG',                 'DOM_PK_G'),
  (0x23, 'KeyH',                 'DOM_PK_H'),
  (0x24, 'KeyJ',                 'DOM_PK_J'),
  (0x25, 'KeyK',                 'DOM_PK_K'),
  (0x26, 'KeyL',                 'DOM_PK_L'),
  (0x27, 'Semicolon',            'DOM_PK_SEMICOLON'),
  (0x28, 'Quote',                'DOM_PK_QUOTE'),
  (0x29, 'Backquote',            'DOM_PK_BACKQUOTE'),
  (0x2A, 'ShiftLeft',            'DOM_PK_SHIFT_LEFT'),
  (0x2B, 'Backslash',            'DOM_PK_BACKSLASH'),
  (0x2C, 'KeyZ',                 'DOM_PK_Z'),
  (0x2D, 'KeyX',                 'DOM_PK_X'),
  (0x2E, 'KeyC',                 'DOM_PK_C'),
  (0x2F, 'KeyV',                 'DOM_PK_V'),
  (0x30, 'KeyB',                 'DOM_PK_B'),
  (0x31, 'KeyN',                 'DOM_PK_N'),
  (0x32, 'KeyM',                 'DOM_PK_M'),
  (0x33, 'Comma',                'DOM_PK_COMMA'),
  (0x34, 'Period',               'DOM_PK_PERIOD'),
  (0x35, 'Slash',                'DOM_PK_SLASH'),
  (0x36, 'ShiftRight',           'DOM_PK_SHIFT_RIGHT'),
  (0x37, 'NumpadMultiply',       'DOM_PK_NUMPAD_MULTIPLY'),
  (0x38, 'AltLeft',              'DOM_PK_ALT_LEFT'),
  (0x39, 'Space',                'DOM_PK_SPACE'),
  (0x3A, 'CapsLock',             'DOM_PK_CAPS_LOCK'),
  (0x3B, 'F1',                   'DOM_PK_F1'),
  (0x3C, 'F2',                   'DOM_PK_F2'),
  (0x3D, 'F3',                   'DOM_PK_F3'),
  (0x3E, 'F4',                   'DOM_PK_F4'),
  (0x3F, 'F5',                   'DOM_PK_F5'),
  (0x40, 'F6',                   'DOM_PK_F6'),
  (0x41, 'F7',                   'DOM_PK_F7'),
  (0x42, 'F8',                   'DOM_PK_F8'),
  (0x43, 'F9',                   'DOM_PK_F9'),
  (0x44, 'F10',                  'DOM_PK_F10'),
  (0x45, 'Pause',                'DOM_PK_PAUSE'),
  (0x46, 'ScrollLock',           'DOM_PK_SCROLL_LOCK'),
  (0x47, 'Numpad7',              'DOM_PK_NUMPAD_7'),
  (0x48, 'Numpad8',              'DOM_PK_NUMPAD_8'),
  (0x49, 'Numpad9',              'DOM_PK_NUMPAD_9'),
  (0x4A, 'NumpadSubtract',       'DOM_PK_NUMPAD_SUBTRACT'),
  (0x4B, 'Numpad4',              'DOM_PK_NUMPAD_4'),
  (0x4C, 'Numpad5',              'DOM_PK_NUMPAD_5'),
  (0x4D, 'Numpad6',              'DOM_PK_NUMPAD_6'),
  (0x4E, 'NumpadAdd',            'DOM_PK_NUMPAD_ADD'),
  (0x4F, 'Numpad1',              'DOM_PK_NUMPAD_1'),
  (0x50, 'Numpad2',              'DOM_PK_NUMPAD_2'),
  (0x51, 'Numpad3',              'DOM_PK_NUMPAD_3'),
  (0x52, 'Numpad0',              'DOM_PK_NUMPAD_0'),
  (0x53, 'NumpadDecimal',        'DOM_PK_NUMPAD_DECIMAL'),
  (0x54, 'PrintScreen',          'DOM_PK_PRINT_SCREEN'),
  # 0x0055 'Unidentified', ''
  (0x56, 'IntlBackslash',        'DOM_PK_INTL_BACKSLASH'),
  (0x57, 'F11',                  'DOM_PK_F11'),
  (0x58, 'F12',                  'DOM_PK_F12'),
  (0x59, 'NumpadEqual',          'DOM_PK_NUMPAD_EQUAL'),
  # 0x005A 'Unidentified', ''
  # 0x005B 'Unidentified', ''
  # 0x005C 'Unidentified', ''
  # 0x005D 'Unidentified', ''
  # 0x005E 'Unidentified', ''
  # 0x005F 'Unidentified', ''
  # 0x0060 'Unidentified', ''
  # 0x0061 'Unidentified', ''
  # 0x0062 'Unidentified', ''
  # 0x0063 'Unidentified', ''
  (0x64, 'F13',                  'DOM_PK_F13'),
  (0x65, 'F14',                  'DOM_PK_F14'),
  (0x66, 'F15',                  'DOM_PK_F15'),
  (0x67, 'F16',                  'DOM_PK_F16'),
  (0x68, 'F17',                  'DOM_PK_F17'),
  (0x69, 'F18',                  'DOM_PK_F18'),
  (0x6A, 'F19',                  'DOM_PK_F19'),
  (0x6B, 'F20',                  'DOM_PK_F20'),
  (0x6C, 'F21',                  'DOM_PK_F21'),
  (0x6D, 'F22',                  'DOM_PK_F22'),
  (0x6E, 'F23',                  'DOM_PK_F23'),
  # 0x006F 'Unidentified', ''
  (0x70, 'KanaMode',             'DOM_PK_KANA_MODE'),
  (0x71, 'Lang2',                'DOM_PK_LANG_2'),
  (0x72, 'Lang1',                'DOM_PK_LANG_1'),
  (0x73, 'IntlRo',               'DOM_PK_INTL_RO'),
  # 0x0074 'Unidentified', ''
  # 0x0075 'Unidentified', ''
  (0x76, 'F24',                  'DOM_PK_F24'),
  # 0x0077 'Unidentified', ''
  # 0x0078 'Unidentified', ''
  (0x79, 'Convert',              'DOM_PK_CONVERT'),
  # 0x007A 'Unidentified', ''
  (0x7B, 'NonConvert',           'DOM_PK_NON_CONVERT'),
  # 0x007C 'Unidentified', ''
  (0x7D, 'IntlYen',              'DOM_PK_INTL_YEN'),
  (0x7E, 'NumpadComma',          'DOM_PK_NUMPAD_COMMA'),
  # 0x007F 'Unidentified', ''
  (0xE00A, 'Paste',              'DOM_PK_PASTE'),
  (0xE010, 'MediaTrackPrevious', 'DOM_PK_MEDIA_TRACK_PREVIOUS'),
  (0xE017, 'Cut',                'DOM_PK_CUT'),
  (0xE018, 'Copy',               'DOM_PK_COPY'),
  (0xE019, 'MediaTrackNext',     'DOM_PK_MEDIA_TRACK_NEXT'),
  (0xE01C, 'NumpadEnter',        'DOM_PK_NUMPAD_ENTER'),
  (0xE01D, 'ControlRight',       'DOM_PK_CONTROL_RIGHT'),
  (0xE020, 'AudioVolumeMute',    'DOM_PK_AUDIO_VOLUME_MUTE'),
  (0xE020, 'VolumeMute',         'DOM_PK_AUDIO_VOLUME_MUTE', 'duplicate'),
  (0xE021, 'LaunchApp2',         'DOM_PK_LAUNCH_APP_2'),
  (0xE022, 'MediaPlayPause',     'DOM_PK_MEDIA_PLAY_PAUSE'),
  (0xE024, 'MediaStop',          'DOM_PK_MEDIA_STOP'),
  (0xE02C, 'Eject',              'DOM_PK_EJECT'),
  (0xE02E, 'AudioVolumeDown',    'DOM_PK_AUDIO_VOLUME_DOWN'),
  (0xE02E, 'VolumeDown',         'DOM_PK_AUDIO_VOLUME_DOWN', 'duplicate'),
  (0xE030, 'AudioVolumeUp',      'DOM_PK_AUDIO_VOLUME_UP'),
  (0xE030, 'VolumeUp',           'DOM_PK_AUDIO_VOLUME_UP', 'duplicate'),
  (0xE032, 'BrowserHome',        'DOM_PK_BROWSER_HOME'),
  (0xE035, 'NumpadDivide',       'DOM_PK_NUMPAD_DIVIDE'),
  #  (0xE037, 'PrintScreen',        'DOM_PK_PRINT_SCREEN'),
  (0xE038, 'AltRight',           'DOM_PK_ALT_RIGHT'),
  (0xE03B, 'Help',               'DOM_PK_HELP'),
  (0xE045, 'NumLock',            'DOM_PK_NUM_LOCK'),
  #  (0xE046, 'Pause', 'DOM_PK_'), # Says Ctrl+Pause
  (0xE047, 'Home',               'DOM_PK_HOME'),
  (0xE048, 'ArrowUp',            'DOM_PK_ARROW_UP'),
  (0xE049, 'PageUp',             'DOM_PK_PAGE_UP'),
  (0xE04B, 'ArrowLeft',          'DOM_PK_ARROW_LEFT'),
  (0xE04D, 'ArrowRight',         'DOM_PK_ARROW_RIGHT'),
  (0xE04F, 'End',                'DOM_PK_END'),
  (0xE050, 'ArrowDown',          'DOM_PK_ARROW_DOWN'),
  (0xE051, 'PageDown',           'DOM_PK_PAGE_DOWN'),
  (0xE052, 'Insert',             'DOM_PK_INSERT'),
  (0xE053, 'Delete',             'DOM_PK_DELETE'),
  (0xE05B, 'MetaLeft',           'DOM_PK_META_LEFT'),
  (0xE05B, 'OSLeft',             'DOM_PK_OS_LEFT', 'duplicate'),
  (0xE05C, 'MetaRight',          'DOM_PK_META_RIGHT'),
  (0xE05C, 'OSRight',            'DOM_PK_OS_RIGHT', 'duplicate'),
  (0xE05D, 'ContextMenu',        'DOM_PK_CONTEXT_MENU'),
  (0xE05E, 'Power',              'DOM_PK_POWER'),
  (0xE065, 'BrowserSearch',      'DOM_PK_BROWSER_SEARCH'),
  (0xE066, 'BrowserFavorites',   'DOM_PK_BROWSER_FAVORITES'),
  (0xE067, 'BrowserRefresh',     'DOM_PK_BROWSER_REFRESH'),
  (0xE068, 'BrowserStop',        'DOM_PK_BROWSER_STOP'),
  (0xE069, 'BrowserForward',     'DOM_PK_BROWSER_FORWARD'),
  (0xE06A, 'BrowserBack',        'DOM_PK_BROWSER_BACK'),
  (0xE06B, 'LaunchApp1',         'DOM_PK_LAUNCH_APP_1'),
  (0xE06C, 'LaunchMail',         'DOM_PK_LAUNCH_MAIL'),
  (0xE06D, 'LaunchMediaPlayer',  'DOM_PK_LAUNCH_MEDIA_PLAYER'),
  (0xE06D, 'MediaSelect',        'DOM_PK_MEDIA_SELECT', 'duplicate')
  #  (0xE0F1, 'Lang2', 'DOM_PK_'), Hanja key
  #  (0xE0F2, 'Lang2', 'DOM_PK_'), Han/Yeong
]


def hash(s, k1, k2):
  h = 0
  for c in s:
    h = int(int(int(h ^ k1) << k2) ^ ord(c)) & 0xFFFFFFFF
  return h


def hash_all(k1, k2):
  hashes = {}
  str_to_hash = {}
  for s in input_strings:
    h = hash(s[1], k1, k2)
    print('String "' + s[1] + '" hashes to %s ' % hex(h), file=sys.stderr)
    if h in hashes:
      print('Collision! Earlier string ' + hashes[h] + ' also hashed to %s!' % hex(h), file=sys.stderr)
      return None
    else:
      hashes[h] = s[1]
      str_to_hash[s[1]] = h
  return (hashes, str_to_hash)


# Find an approprite hash function that is collision free within the set of all input strings
# Try hash function format h_i = ((h_(i-1) ^ k_1) << k_2) ^ s_i, where h_i is the hash function
# value at step i, k_1 and k_2 are the constants we are searching, and s_i is the i'th input
# character
perfect_hash_table = None

# Last used perfect hash constants.  Stored here so that this script will
# produce the same output it did when the current output was generated.
k1 = 0x7E057D79
k2 = 3
perfect_hash_table = hash_all(k1, k2)

while not perfect_hash_table:
  # The search space is super-narrow, but since there are so few items to hash, practically
  # almost any choice gives a collision free hash.
  k1 = int(random.randint(0, 0x7FFFFFFF))
  k2 = int(random.uniform(1, 8))
  perfect_hash_table = hash_all(k1, k2)

hash_to_str, str_to_hash = perfect_hash_table

print('Found collision-free hash function!', file=sys.stderr)
print('h_i = ((h_(i-1) ^ %s) << %s) ^ s_i' % (hex(k1), hex(k2)), file=sys.stderr)


def pad_to_length(s, length):
  return s + max(0, length - len(s)) * ' '


def longest_dom_pk_code_length():
  return max(map(len, [x[2] for x in input_strings]))


def longest_key_code_length():
  return max(map(len, [x[1] for x in input_strings]))


h_file = open('system/include/emscripten/dom_pk_codes.h', 'w')
c_file = open('system/lib/html5/dom_pk_codes.c', 'w')

# Generate the output file:

h_file.write('''\
/*
 * Copyright 2018 The Emscripten Authors.  All rights reserved.
 * Emscripten is available under two separate licenses, the MIT license and the
 * University of Illinois/NCSA Open Source License.  Both these licenses can be
 * found in the LICENSE file.
 *
 * This file was automatically generated from script
 * tools/create_dom_pk_codes.py. Edit that file to make changes here.
 * Run
 *
 *   tools/create_dom_pk_codes.py
 *
 * in Emscripten root directory to regenerate this file.
 */

#pragma once

#define DOM_PK_CODE_TYPE int

''')

c_file.write('''/* This file was automatically generated from script
tools/create_dom_pk_codes.py. Edit that file to make changes here.
Run

  python tools/create_dom_pk_codes.py

in Emscripten root directory to regenerate this file. */

#include <emscripten/dom_pk_codes.h>
''')

for s in input_strings:
  h_file.write('#define ' + pad_to_length(s[2], longest_dom_pk_code_length()) + ' 0x%04X /* "%s */' % (s[0], pad_to_length(s[1] + '"', longest_key_code_length() + 1)) + '\n')

h_file.write('''
#ifdef __cplusplus
extern "C" {
#endif
/* Maps the EmscriptenKeyboardEvent::code field from emscripten/html5.h to one of the DOM_PK codes above. */
DOM_PK_CODE_TYPE emscripten_compute_dom_pk_code(const char *keyCodeString);

/* Returns the string representation of the given key code ID. Useful for debug printing. */
const char *emscripten_dom_pk_code_to_string(DOM_PK_CODE_TYPE code);
#ifdef __cplusplus
}
#endif
''')

c_file.write('''
DOM_PK_CODE_TYPE emscripten_compute_dom_pk_code(const char *keyCodeString)
{
  if (!keyCodeString) return 0;

  /* Compute the collision free hash. */
  unsigned int hash = 0;
  while(*keyCodeString) hash = ((hash ^ 0x%04XU) << %d) ^ (unsigned int)*keyCodeString++;

  /* Don't expose the hash values out to the application, but map to fixed IDs. This is useful for
     mapping back codes to MDN documentation page at

       https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/code */
  switch(hash)
  {
''' % (k1, k2))

for s in input_strings:
  c_file.write('    case 0x%08XU /* %s */: return %s /* 0x%04X */' % (str_to_hash[s[1]], pad_to_length(s[1], longest_key_code_length()), pad_to_length(s[2] + ';', longest_dom_pk_code_length() + 1), s[0]) + '\n')

c_file.write('''    default: return DOM_PK_UNKNOWN;
  }
}

const char *emscripten_dom_pk_code_to_string(DOM_PK_CODE_TYPE code)
{
  switch(code)
  {
''')

for s in input_strings:
  if len(s) == 3:
    c_file.write('    case %s return "%s";' % (pad_to_length(s[2] + ':', longest_dom_pk_code_length() + 1), s[2]) + '\n')

c_file.write('''    default: return "Unknown DOM_PK code";
  }
}
''')

# SIG # Begin Windows Authenticode signature block
# MIIoPgYJKoZIhvcNAQcCoIIoLzCCKCsCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAr56h+5gyDn+Eu
# /3XR3Gp2hXfpIVa2tKCjQkVmkmvtkKCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEILoslgM8clcFp0InfVGmEW67W14GFHLREGamBdBCxpeaMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAhH/2+ufUwSq/KR86bXHRvafI1oAd
# +dUoCIRzpiByWiVzYIAC3jhLGfg2LOf+Fsv/MRTBjSQZZIFuyUZywVVhQYXDWPFo
# AQH0Ktw+eKsSug8e1U42CiRssvfSUmzpAW09qbSpL83syKjfLxb0J1dlLnsoPG6w
# 00WAVQ66d1tD7MV7W3MAIrdGqk62UuPpQMkloIhKgvpa10+vNeqDlhAyjtlBQiA5
# DZrHRThLIJO1/GdmQlV96a1wEY8QAEoaJ5Lof2BCMTDkYTylT3P8xcn2et9wheYr
# fxF/hEagCwmhZ5TnEmAyk/zR/qK8FfMAgRo+tqX8pWvx3Lk+bUDmnKH4FqGCF5Mw
# ghePBgorBgEEAYI3AwMBMYIXfzCCF3sGCSqGSIb3DQEHAqCCF2wwghdoAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCBzziC4/qxMC9Pd1pGYLlDPklsu
# 3npGqVVvnXmwb6mV1AIGaPCNPkW4GBMyMDI1MTAxNjE2MTc0MC45ODVaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046OTYwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHpMIIHIDCCBQigAwIBAgITMwAAAgTY4A4H
# lzJYmAABAAACBDANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQyNDdaFw0yNjA0MjIxOTQyNDdaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# OTYwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDw3Sbcee2d66vk
# WGTIXhfGqqgQGxQXTnq44XlUvNzFSt7ELtO4B939jwZFX7DrRt/4fpzGNkFdGpc7
# EL5S86qKYv360eXjW+fIv1lAqDD31d/p8Ai9/AZz8M95zo0rDpK2csz9WAyR9FtU
# Dx52VOs9qP3/pgpHvgUvD8s6/3KNITzms8QC1tJ3TMw1cRn9CZgVIYzw2iD/ZvOW
# 0sbF/DRdgM8UdtxjFIKTXTaI/bJhsQge3TwayKQ2j85RafFFVCR5/ChapkrBQWGw
# NFaPzpmYN46mPiOvUxriISC9nQ/GrDXUJWzLDmchrmr2baABJevvw31UYlTlLZY6
# zUmjkgaRfpozd+Glq9TY2E3Dglr6PtTEKgPu2hM6v8NiU5nTvxhDnxdmcf8UN7go
# eVlELXbOm7j8yw1xM9IyyQuUMWkorBaN/5r9g4lvYkMohRXEYB0tMaOPt0FmZmQM
# LBFpNRVnXBTa4haXvn1adKrvTz8VlfnHxkH6riA/h2AlqYWhv0YULsEcHnaDWgqA
# 29ry+jH097MpJ/FHGHxk+d9kH2L5aJPpAYuNmMNPB7FDTPWAx7Apjr/J5MhUx0i0
# 7gV2brAZ9J9RHi+fMPbS+Qm4AonC5iOTj+dKCttVRs+jKKuO63CLwqlljvnUCmuS
# avOX54IXOtKcFZkfDdOZ7cE4DioP1QIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFBp1
# dktAcGpW/Km6qm+vu4M1GaJfMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQBecv6s
# Rw2HTLMyUC1WJJ+FR+DgA9Jkv0lGsIt4y69CmOj8R63oFbhSmcdpakxqNbr8v9dy
# Tb4RDyNqtohiiXbtrXmQK5X7y/Q++F0zMotTtTpTPvG3eltyV/LvO15mrLoNQ7W4
# VH58aLt030tORxs8VnAQQF5BmQQMOua+EQgH4f1F4uF6rl3EC17JBSJ0wjHSea/n
# 0WYiHPR0qkz/NRAf8lSUUV0gbIMawGIjn7+RKyCr+8l1xdNkK/F0UYuX3hG0nE+9
# Wc0L4A/enluUN7Pa9vOV6Vi3BOJST0RY/ax7iZ45leM8kqCw7BFPcTIkWzxpjr2n
# Ctirnkw7OBQ6FNgwIuAvYNTU7r60W421YFOL5pTsMZcNDOOsA01xv7ymCF6zknMG
# pRHuw0Rb2BAJC9quU7CXWbMbAJLdZ6XINKariSmCX3/MLdzcW5XOycK0QhoRNRf4
# WqXRshEBaY2ymJvHO48oSSY/kpuYvBS3ljAAuLN7Rp8jWS7t916paGeE7prmrP9F
# Jsoy1LFKmFnW+vg43ANhByuAEXq9Cay5o7K2H5NFnR5wj/SLRKwK1iyUX926i1TE
# viEiAh/PVyJbAD4koipig28p/6HDuiYOZ0wUkm/a5W8orIjoOdU3XsJ4i08CfNp5
# I73CsvB5QPYMcLpF9NO/1LvoQAw3UPdL55M5HTCCB3EwggVZoAMCAQICEzMAAAAV
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
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjk2
# MDAtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQC6PYHRw9+9SH+1pwy6qzVG3k9lbqCBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7JsLszAiGA8yMDI1MTAxNjA2MTQxMVoYDzIwMjUxMDE3MDYxNDExWjBzMDkGCisG
# AQQBhFkKBAExKzApMAoCBQDsmwuzAgEAMAYCAQACAS0wBwIBAAICEjYwCgIFAOyc
# XTMCAQAwNgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAKMAgCAQACAweh
# IKEKMAgCAQACAwGGoDANBgkqhkiG9w0BAQsFAAOCAQEAV1PiKregTmp+Pau047Gd
# p0TuNlRxlgpdySv9B0GfFVNgM3/GBtDkz+2JQpROB/V/VxfpJ3aIDdWTMUr766Rf
# kMnJBprwzfHT9MN/HnA0f6OpV8m3iz0PJwH3mVxYpE5YWxawryXoF5HllmzD9w5Y
# 6oGzV7iDTo5L3YNBOoI3JDkxl90ZEllV6NkzvNp+fpILPmTMOdW+zfi7lStFlE5F
# nB1r+v+k7kiuj8jzGOlC7p7novlf5iP9DvAIDzg1QZRYNPwv5a5jhUYrj5PtLCdn
# 2lPOMhBPlNzZ17i2kts+QfQ7lSGYLIJN32s4bfXaxuQRLxcTcaQqPoiicO26FTPq
# fDGCBA0wggQJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwAhMz
# AAACBNjgDgeXMliYAAEAAAIEMA0GCWCGSAFlAwQCAQUAoIIBSjAaBgkqhkiG9w0B
# CQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIHTGD2x4ArITLkz5bCDg
# hIVy6VJfTxTSEKntZ37GiYhyMIH6BgsqhkiG9w0BCRACLzGB6jCB5zCB5DCBvQQg
# +e14Zf1bCrxV0kzqaN/HUYQmy7v/qRTqXRJLmtx5uf4wgZgwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAgTY4A4HlzJYmAABAAACBDAiBCBE
# u/Jey44LGb0AwjrNtmsyrbCoz8KUosJXeJTZiqlH2zANBgkqhkiG9w0BAQsFAASC
# AgAVFyQnHMrqs43kIYL4h3tVj93HziM3Xhf4B5kciNlxxwUAdkjiWVgDlhtrD18N
# gfQr0xE0JyWmwkNcvGK3NsybcGc54H+bV6oetTGbHduWcjXDgvi9BAYMQzZQ0DBd
# R+kDdGlmR38s2XeDh0MF0qKASE5akKm+HLe2aCSriUBi8ju3sTKJkbfcc7PGQ2dq
# ikTb/tCzzN96a0oHXUtxaf3umi52E1JSIwoS5wmvAauDAlnCLnW+pwAmrBG85GCz
# aqhiqjf7AV4GyeDkp+jayGo21Yxp8HvGDb+gsWrcpAssL2ugyvdwY+LdTy7xCifA
# RcLNs75iAU6V/Z87bMMB3kjJ0aye9vjjR0KyotCoOVx6DanAZSkRzfLs+JeNXEzF
# 8OV1tcGMYnR9yRY341qeOljaGvRZERF5jtjjmq68xFQ4KoNI5NI+8TBusZW/yrEU
# 3vUDewyEUAJcScWDo7aECBsmK0h8kNYXgb+X4tTs6d8K1PFoBGkCq8bXLySz0tVO
# TjaujGBMNF8O+yVK8OUkCAwXiHC+Nqn2BJ/nA/2PEdvUbQXvMiSC9aDbMZEqIMFx
# xv3YysQhvJTocLinliPv/lg9pEYFXsXKSC4Xv9MYqvQZJE/EiSAhOzyO+uOyEHs1
# bmuwwBjIHIKdbJ67pk22NKn5asHVI5tauiegnGcEddxYyA==
# SIG # End Windows Authenticode signature block