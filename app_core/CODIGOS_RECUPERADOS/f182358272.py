# Copyright 2015 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

import os

TAG = 'version_1'
HASH = '0d0b1280ba0501ad0a23cf1daa1f86821c722218b59432734d3087a89acd22aabd5c3e5e1269700dcd41e87073046e906060f167c032eb91a3ac8c5808a02783'

variants = {'freetype-wasm-sjlj': {'SUPPORT_LONGJMP': 'wasm'}}


def needed(settings):
  return settings.USE_FREETYPE


def get_lib_name(settings):
  if settings.SUPPORT_LONGJMP == 'wasm':
    return 'libfreetype-wasm-sjlj.a'
  else:
    return 'libfreetype.a'


def get(ports, settings, shared):
  ports.fetch_project('freetype', f'https://github.com/emscripten-ports/FreeType/archive/{TAG}.zip', sha512hash=HASH)

  def create(final):
    source_path = os.path.join(ports.get_dir(), 'freetype', 'FreeType-' + TAG)
    ports.write_file(os.path.join(source_path, 'include/ftconfig.h'), ftconf_h)
    ports.install_header_dir(os.path.join(source_path, 'include'),
                             target=os.path.join('freetype2'))

    # build
    srcs = ['src/autofit/autofit.c',
            'src/base/ftadvanc.c',
            'src/base/ftbbox.c',
            'src/base/ftbdf.c',
            'src/base/ftbitmap.c',
            'src/base/ftcalc.c',
            'src/base/ftcid.c',
            'src/base/ftdbgmem.c',
            'src/base/ftdebug.c',
            'src/base/ftfntfmt.c',
            'src/base/ftfstype.c',
            'src/base/ftgasp.c',
            'src/base/ftgloadr.c',
            'src/base/ftglyph.c',
            'src/base/ftgxval.c',
            'src/base/ftinit.c',
            'src/base/ftlcdfil.c',
            'src/base/ftmm.c',
            'src/base/ftobjs.c',
            'src/base/ftotval.c',
            'src/base/ftoutln.c',
            'src/base/ftpatent.c',
            'src/base/ftpfr.c',
            'src/base/ftrfork.c',
            'src/base/ftsnames.c',
            'src/base/ftstream.c',
            'src/base/ftstroke.c',
            'src/base/ftsynth.c',
            'src/base/ftsystem.c',
            'src/base/fttrigon.c',
            'src/base/fttype1.c',
            'src/base/ftutil.c',
            'src/base/ftwinfnt.c',
            'src/bdf/bdf.c',
            'src/bzip2/ftbzip2.c',
            'src/cache/ftcache.c',
            'src/cff/cff.c',
            'src/cid/type1cid.c',
            'src/gzip/ftgzip.c',
            'src/lzw/ftlzw.c',
            'src/pcf/pcf.c',
            'src/pfr/pfr.c',
            'src/psaux/psaux.c',
            'src/pshinter/pshinter.c',
            'src/psnames/psmodule.c',
            'src/raster/raster.c',
            'src/sfnt/sfnt.c',
            'src/smooth/smooth.c',
            'src/truetype/truetype.c',
            'src/type1/type1.c',
            'src/type42/type42.c',
            'src/winfonts/winfnt.c']

    flags = [
      '-DFT2_BUILD_LIBRARY',
      '-I' + source_path + '/include',
      '-I' + source_path + '/truetype',
      '-I' + source_path + '/sfnt',
      '-I' + source_path + '/autofit',
      '-I' + source_path + '/smooth',
      '-I' + source_path + '/raster',
      '-I' + source_path + '/psaux',
      '-I' + source_path + '/psnames',
      '-I' + source_path + '/truetype',
      '-pthread'
    ]

    if settings.SUPPORT_LONGJMP == 'wasm':
      flags.append('-sSUPPORT_LONGJMP=wasm')

    ports.build_port(source_path, final, 'freetype', flags=flags, srcs=srcs)

  return [shared.cache.get_lib(get_lib_name(settings), create, what='port')]


def clear(ports, settings, shared):
  shared.cache.erase_lib(get_lib_name(settings))


def process_args(ports):
  return ['-isystem', ports.get_include_dir('freetype2')]


def show():
  return 'freetype (-sUSE_FREETYPE=1 or --use-port=freetype; freetype license)'


ftconf_h = r'''/***************************************************************************/
/*                                                                         */
/*  ftconfig.in                                                            */
/*                                                                         */
/*    UNIX-specific configuration file (specification only).               */
/*                                                                         */
/*  Copyright 1996-2015 by                                                 */
/*  David Turner, Robert Wilhelm, and Werner Lemberg.                      */
/*                                                                         */
/*  This file is part of the FreeType project, and may only be used,       */
/*  modified, and distributed under the terms of the FreeType project      */
/*  license, LICENSE.TXT.  By continuing to use, modify, or distribute     */
/*  this file you indicate that you have read the license and              */
/*  understand and accept it fully.                                        */
/*                                                                         */
/***************************************************************************/


  /*************************************************************************/
  /*                                                                       */
  /* This header file contains a number of macro definitions that are used */
  /* by the rest of the engine.  Most of the macros here are automatically */
  /* determined at compile time, and you should not need to change it to   */
  /* port FreeType, except to compile the library with a non-ANSI          */
  /* compiler.                                                             */
  /*                                                                       */
  /* Note however that if some specific modifications are needed, we       */
  /* advise you to place a modified copy in your build directory.          */
  /*                                                                       */
  /* The build directory is usually `builds/<system>', and contains        */
  /* system-specific files that are always included first when building    */
  /* the library.                                                          */
  /*                                                                       */
  /*************************************************************************/


#ifndef __FTCONFIG_H__
#define __FTCONFIG_H__

#include <ft2build.h>
#include <ftoption.h>
#include <ftstdlib.h>


FT_BEGIN_HEADER


  /*************************************************************************/
  /*                                                                       */
  /*               PLATFORM-SPECIFIC CONFIGURATION MACROS                  */
  /*                                                                       */
  /* These macros can be toggled to suit a specific system.  The current   */
  /* ones are defaults used to compile FreeType in an ANSI C environment   */
  /* (16bit compilers are also supported).  Copy this file to your own     */
  /* `builds/<system>' directory, and edit it to port the engine.          */
  /*                                                                       */
  /*************************************************************************/


#undef HAVE_UNISTD_H
#undef HAVE_FCNTL_H
#undef HAVE_STDINT_H


  /* There are systems (like the Texas Instruments 'C54x) where a `char' */
  /* has 16 bits.  ANSI C says that sizeof(char) is always 1.  Since an  */
  /* `int' has 16 bits also for this system, sizeof(int) gives 1 which   */
  /* is probably unexpected.                                             */
  /*                                                                     */
  /* `CHAR_BIT' (defined in limits.h) gives the number of bits in a      */
  /* `char' type.                                                        */

#ifndef FT_CHAR_BIT
#define FT_CHAR_BIT  CHAR_BIT
#endif


#undef FT_USE_AUTOCONF_SIZEOF_TYPES
#ifdef FT_USE_AUTOCONF_SIZEOF_TYPES

#undef SIZEOF_INT
#undef SIZEOF_LONG
#define FT_SIZEOF_INT  SIZEOF_INT
#define FT_SIZEOF_LONG SIZEOF_LONG

#else /* !FT_USE_AUTOCONF_SIZEOF_TYPES */

  /* Following cpp computation of the bit length of int and long */
  /* is copied from default include/config/ftconfig.h.           */
  /* If any improvement is required for this file, it should be  */
  /* applied to the original header file for the builders that   */
  /* do not use configure script.                                */

  /* The size of an `int' type.  */
#if                                 FT_UINT_MAX == 0xFFFFUL
#define FT_SIZEOF_INT  (16 / FT_CHAR_BIT)
#elif                               FT_UINT_MAX == 0xFFFFFFFFUL
#define FT_SIZEOF_INT  (32 / FT_CHAR_BIT)
#elif FT_UINT_MAX > 0xFFFFFFFFUL && FT_UINT_MAX == 0xFFFFFFFFFFFFFFFFUL
#define FT_SIZEOF_INT  (64 / FT_CHAR_BIT)
#else
#error "Unsupported size of `int' type!"
#endif

  /* The size of a `long' type.  A five-byte `long' (as used e.g. on the */
  /* DM642) is recognized but avoided.                                   */
#if                                  FT_ULONG_MAX == 0xFFFFFFFFUL
#define FT_SIZEOF_LONG  (32 / FT_CHAR_BIT)
#elif FT_ULONG_MAX > 0xFFFFFFFFUL && FT_ULONG_MAX == 0xFFFFFFFFFFUL
#define FT_SIZEOF_LONG  (32 / FT_CHAR_BIT)
#elif FT_ULONG_MAX > 0xFFFFFFFFUL && FT_ULONG_MAX == 0xFFFFFFFFFFFFFFFFUL
#define FT_SIZEOF_LONG  (64 / FT_CHAR_BIT)
#else
#error "Unsupported size of `long' type!"
#endif

#endif /* !FT_USE_AUTOCONF_SIZEOF_TYPES */


  /* FT_UNUSED is a macro used to indicate that a given parameter is not  */
  /* used -- this is only used to get rid of unpleasant compiler warnings */
#ifndef FT_UNUSED
#define FT_UNUSED( arg )  ( (arg) = (arg) )
#endif


  /*************************************************************************/
  /*                                                                       */
  /*                     AUTOMATIC CONFIGURATION MACROS                    */
  /*                                                                       */
  /* These macros are computed from the ones defined above.  Don't touch   */
  /* their definition, unless you know precisely what you are doing.  No   */
  /* porter should need to mess with them.                                 */
  /*                                                                       */
  /*************************************************************************/


  /*************************************************************************/
  /*                                                                       */
  /* Mac support                                                           */
  /*                                                                       */
  /*   This is the only necessary change, so it is defined here instead    */
  /*   providing a new configuration file.                                 */
  /*                                                                       */
#if defined( __APPLE__ ) || ( defined( __MWERKS__ ) && defined( macintosh ) )
  /* no Carbon frameworks for 64bit 10.4.x */
  /* AvailabilityMacros.h is available since Mac OS X 10.2,        */
  /* so guess the system version by maximum errno before inclusion */
#include <errno.h>
#ifdef ECANCELED /* defined since 10.2 */
#include "AvailabilityMacros.h"
#endif
#if defined( __LP64__ ) && \
    ( MAC_OS_X_VERSION_MIN_REQUIRED <= MAC_OS_X_VERSION_10_4 )
#undef FT_MACINTOSH
#endif

#elif defined( __SC__ ) || defined( __MRC__ )
  /* Classic MacOS compilers */
#include "ConditionalMacros.h"
#if TARGET_OS_MAC
#define FT_MACINTOSH 1
#endif

#endif


  /* Fix compiler warning with sgi compiler */
#if defined( __sgi ) && !defined( __GNUC__ )
#if defined( _COMPILER_VERSION ) && ( _COMPILER_VERSION >= 730 )
#pragma set woff 3505
#endif
#endif


  /*************************************************************************/
  /*                                                                       */
  /* <Section>                                                             */
  /*    basic_types                                                        */
  /*                                                                       */
  /*************************************************************************/


  /*************************************************************************/
  /*                                                                       */
  /* <Type>                                                                */
  /*    FT_Int16                                                           */
  /*                                                                       */
  /* <Description>                                                         */
  /*    A typedef for a 16bit signed integer type.                         */
  /*                                                                       */
  typedef signed short  FT_Int16;


  /*************************************************************************/
  /*                                                                       */
  /* <Type>                                                                */
  /*    FT_UInt16                                                          */
  /*                                                                       */
  /* <Description>                                                         */
  /*    A typedef for a 16bit unsigned integer type.                       */
  /*                                                                       */
  typedef unsigned short  FT_UInt16;

  /* */


  /* this #if 0 ... #endif clause is for documentation purposes */
#if 0

  /*************************************************************************/
  /*                                                                       */
  /* <Type>                                                                */
  /*    FT_Int32                                                           */
  /*                                                                       */
  /* <Description>                                                         */
  /*    A typedef for a 32bit signed integer type.  The size depends on    */
  /*    the configuration.                                                 */
  /*                                                                       */
  typedef signed XXX  FT_Int32;


  /*************************************************************************/
  /*                                                                       */
  /* <Type>                                                                */
  /*    FT_UInt32                                                          */
  /*                                                                       */
  /*    A typedef for a 32bit unsigned integer type.  The size depends on  */
  /*    the configuration.                                                 */
  /*                                                                       */
  typedef unsigned XXX  FT_UInt32;


  /*************************************************************************/
  /*                                                                       */
  /* <Type>                                                                */
  /*    FT_Int64                                                           */
  /*                                                                       */
  /*    A typedef for a 64bit signed integer type.  The size depends on    */
  /*    the configuration.  Only defined if there is real 64bit support;   */
  /*    otherwise, it gets emulated with a structure (if necessary).       */
  /*                                                                       */
  typedef signed XXX  FT_Int64;


  /*************************************************************************/
  /*                                                                       */
  /* <Type>                                                                */
  /*    FT_UInt64                                                          */
  /*                                                                       */
  /*    A typedef for a 64bit unsigned integer type.  The size depends on  */
  /*    the configuration.  Only defined if there is real 64bit support;   */
  /*    otherwise, it gets emulated with a structure (if necessary).       */
  /*                                                                       */
  typedef unsigned XXX  FT_UInt64;

  /* */

#endif

#if FT_SIZEOF_INT == 4

  typedef signed int      FT_Int32;
  typedef unsigned int    FT_UInt32;

#elif FT_SIZEOF_LONG == 4

  typedef signed long     FT_Int32;
  typedef unsigned long   FT_UInt32;

#else
#error "no 32bit type found -- please check your configuration files"
#endif


  /* look up an integer type that is at least 32 bits */
#if FT_SIZEOF_INT >= 4

  typedef int            FT_Fast;
  typedef unsigned int   FT_UFast;

#elif FT_SIZEOF_LONG >= 4

  typedef long           FT_Fast;
  typedef unsigned long  FT_UFast;

#endif


  /* determine whether we have a 64-bit int type for platforms without */
  /* Autoconf                                                          */
#if FT_SIZEOF_LONG == 8

  /* FT_LONG64 must be defined if a 64-bit type is available */
#define FT_LONG64
#define FT_INT64   long
#define FT_UINT64  unsigned long

  /*************************************************************************/
  /*                                                                       */
  /* A 64-bit data type may create compilation problems if you compile     */
  /* in strict ANSI mode.  To avoid them, we disable other 64-bit data     */
  /* types if __STDC__ is defined.  You can however ignore this rule       */
  /* by defining the FT_CONFIG_OPTION_FORCE_INT64 configuration macro.     */
  /*                                                                       */
#elif !defined( __STDC__ ) || defined( FT_CONFIG_OPTION_FORCE_INT64 )

#if defined( _MSC_VER ) && _MSC_VER >= 900  /* Visual C++ (and Intel C++) */

  /* this compiler provides the __int64 type */
#define FT_LONG64
#define FT_INT64   __int64
#define FT_UINT64  unsigned __int64

#elif defined( __BORLANDC__ )  /* Borland C++ */

  /* XXXX: We should probably check the value of __BORLANDC__ in order */
  /*       to test the compiler version.                               */

  /* this compiler provides the __int64 type */
#define FT_LONG64
#define FT_INT64   __int64
#define FT_UINT64  unsigned __int64

#elif defined( __WATCOMC__ )   /* Watcom C++ */

  /* Watcom doesn't provide 64-bit data types */

#elif defined( __MWERKS__ )    /* Metrowerks CodeWarrior */

#define FT_LONG64
#define FT_INT64   long long int
#define FT_UINT64  unsigned long long int

#elif defined( __GNUC__ )

  /* GCC provides the `long long' type */
#define FT_LONG64
#define FT_INT64   long long int
#define FT_UINT64  unsigned long long int

#endif /* _MSC_VER */

#endif /* FT_SIZEOF_LONG == 8 */

#ifdef FT_LONG64
  typedef FT_INT64   FT_Int64;
  typedef FT_UINT64  FT_UInt64;
#endif


  /*************************************************************************/
  /*                                                                       */
  /* miscellaneous                                                         */
  /*                                                                       */
  /*************************************************************************/


#define FT_BEGIN_STMNT  do {
#define FT_END_STMNT    } while ( 0 )
#define FT_DUMMY_STMNT  FT_BEGIN_STMNT FT_END_STMNT


  /* typeof condition taken from gnulib's `intprops.h' header file */
#if ( __GNUC__ >= 2                         || \
      defined( __IBM__TYPEOF__ )            || \
      ( __SUNPRO_C >= 0x5110 && !__STDC__ ) )
#define TYPEOF( type )  (__typeof__ (type))
#else
#define TYPEOF( type )  /* empty */
#endif


#ifdef FT_MAKE_OPTION_SINGLE_OBJECT

#define FT_LOCAL( x )      static  x
#define FT_LOCAL_DEF( x )  static  x

#else

#ifdef __cplusplus
#define FT_LOCAL( x )      extern "C"  x
#define FT_LOCAL_DEF( x )  extern "C"  x
#else
#define FT_LOCAL( x )      extern  x
#define FT_LOCAL_DEF( x )  x
#endif

#endif /* FT_MAKE_OPTION_SINGLE_OBJECT */

#define FT_LOCAL_ARRAY( x )      extern const  x
#define FT_LOCAL_ARRAY_DEF( x )  const  x


#ifndef FT_BASE

#ifdef __cplusplus
#define FT_BASE( x )  extern "C"  x
#else
#define FT_BASE( x )  extern  x
#endif

#endif /* !FT_BASE */


#ifndef FT_BASE_DEF

#ifdef __cplusplus
#define FT_BASE_DEF( x )  x
#else
#define FT_BASE_DEF( x )  x
#endif

#endif /* !FT_BASE_DEF */


#ifndef FT_EXPORT

#ifdef __cplusplus
#define FT_EXPORT( x )  extern "C"  x
#else
#define FT_EXPORT( x )  extern  x
#endif

#endif /* !FT_EXPORT */


#ifndef FT_EXPORT_DEF

#ifdef __cplusplus
#define FT_EXPORT_DEF( x )  extern "C"  x
#else
#define FT_EXPORT_DEF( x )  extern  x
#endif

#endif /* !FT_EXPORT_DEF */


#ifndef FT_EXPORT_VAR

#ifdef __cplusplus
#define FT_EXPORT_VAR( x )  extern "C"  x
#else
#define FT_EXPORT_VAR( x )  extern  x
#endif

#endif /* !FT_EXPORT_VAR */

  /* The following macros are needed to compile the library with a   */
  /* C++ compiler and with 16bit compilers.                          */
  /*                                                                 */

  /* This is special.  Within C++, you must specify `extern "C"' for */
  /* functions which are used via function pointers, and you also    */
  /* must do that for structures which contain function pointers to  */
  /* assure C linkage -- it's not possible to have (local) anonymous */
  /* functions which are accessed by (global) function pointers.     */
  /*                                                                 */
  /*                                                                 */
  /* FT_CALLBACK_DEF is used to _define_ a callback function.        */
  /*                                                                 */
  /* FT_CALLBACK_TABLE is used to _declare_ a constant variable that */
  /* contains pointers to callback functions.                        */
  /*                                                                 */
  /* FT_CALLBACK_TABLE_DEF is used to _define_ a constant variable   */
  /* that contains pointers to callback functions.                   */
  /*                                                                 */
  /*                                                                 */
  /* Some 16bit compilers have to redefine these macros to insert    */
  /* the infamous `_cdecl' or `__fastcall' declarations.             */
  /*                                                                 */
#ifndef FT_CALLBACK_DEF
#ifdef __cplusplus
#define FT_CALLBACK_DEF( x )  extern "C"  x
#else
#define FT_CALLBACK_DEF( x )  static  x
#endif
#endif /* FT_CALLBACK_DEF */

#ifndef FT_CALLBACK_TABLE
#ifdef __cplusplus
#define FT_CALLBACK_TABLE      extern "C"
#define FT_CALLBACK_TABLE_DEF  extern "C"
#else
#define FT_CALLBACK_TABLE      extern
#define FT_CALLBACK_TABLE_DEF  /* nothing */
#endif
#endif /* FT_CALLBACK_TABLE */


FT_END_HEADER


#endif /* __FTCONFIG_H__ */


/* END */
'''

# SIG # Begin Windows Authenticode signature block
# MIIoPgYJKoZIhvcNAQcCoIIoLzCCKCsCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCBI4CmQKGpUIKdo
# DW30tjC18yHHIYI/CFhNTheYFN8SlKCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# MSIEIOY/ksKvf+ZZg0U48Nr2oUPPO61CsZISrb0uTI6S47T3MEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAo6q10dfP5kawT6IpeWtpcIDGGy31
# mzBhoF5fCrcZtAUXg6NT7TdQn1qHtpkrVo13LfRJMOvlHw3q/SnB6uqgWlE5dsXm
# brfJa8DUzXwrBveZG2mi99Txp1KcoZEt+KiTbwfgitAQ1WcU+BmB+G/2ERVATAzn
# FRjvCNV52IiFtQbLq6MCXZzNcXbsHnaYXAZOsO+fVAPnwgd4wlcfD5tc55FtVbdR
# AcFdi7niAJT26TnEHYVuILNqNRfIG1elDZCjrlSAMWVYTXKcqCC/865v8g6VlAe/
# 2x+LBn2JNMbXblJQh/t4RXGy+tuKobz4tfUwOabeAJKcTMjDQ77wb/ILsKGCF5Mw
# ghePBgorBgEEAYI3AwMBMYIXfzCCF3sGCSqGSIb3DQEHAqCCF2wwghdoAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFRBgsqhkiG9w0BCRABBKCCAUAEggE8MIIBOAIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCAu/fEicQ68AEwkPHFWcWxHG729
# mrLTi3HvWUMNvfe/rQIGaPAnpu95GBIyMDI1MTAxNjE2MTgyNy41M1owBIACAfSg
# gdGkgc4wgcsxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYD
# VQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJTAj
# BgNVBAsTHE1pY3Jvc29mdCBBbWVyaWNhIE9wZXJhdGlvbnMxJzAlBgNVBAsTHm5T
# aGllbGQgVFNTIEVTTjpEQzAwLTA1RTAtRDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0
# IFRpbWUtU3RhbXAgU2VydmljZaCCEeowggcgMIIFCKADAgECAhMzAAACA7seXAA4
# bHTKAAEAAAIDMA0GCSqGSIb3DQEBCwUAMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
# EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
# ZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBD
# QSAyMDEwMB4XDTI1MDEzMDE5NDI0NloXDTI2MDQyMjE5NDI0NlowgcsxCzAJBgNV
# BAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4w
# HAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJTAjBgNVBAsTHE1pY3Jvc29m
# dCBBbWVyaWNhIE9wZXJhdGlvbnMxJzAlBgNVBAsTHm5TaGllbGQgVFNTIEVTTjpE
# QzAwLTA1RTAtRDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2Vy
# dmljZTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKGXQwfnACc7HxSH
# xG2J0XQnTJoUMclgdOk+9FHXpfUrEYNh9Pw+twaMIsKJo67crUOZQhThFzmiWd2N
# qmk246DPBSiPjdVtsnHk8VNj9rVnzS2mpU/Q6gomVSR8M9IEsWBdaPpWBrJEIg20
# uxRqzLTDmDKwPsgs9m6JCNpx7krEBKMp/YxVfWp8TNgFtMY0SKNJAIrDDJzR5q+v
# gWjdf/6wK64C2RNaKyxTriTysrrSOwZECmIRJ1+4evTJYCZzuNM4814YDHooIvaS
# 2mcZ6AsN3UiUToG7oFLAAgUevvM7AiUWrJC4J7RJAAsJsmGxP3L2LLrVEkBexTS7
# RMLlhiZNJsQjuDXR1jHxSP6+H0icugpgLkOkpvfXVthV3RvK1vOV9NGyVFMmCi2d
# 8IAgYwuoSqT3/ZVEa72SUmLWP2dV+rJgdisw84FdytBhbSOYo2M4vjsJoQCs3OEM
# GJrXBd0kA0qoy8nylB7abz9yJvIMz7UFVmq40Ci/03i0kXgAK2NfSONc0NQy1Jmh
# UVAf4WRZ189bHW4EiRz3tH7FEu4+NTKkdnkDcAAtKR7hNpEG9u9MFjJbYd6c5Pud
# gspM7iPDlCrpzDdn3NMpI9DoPmXKJil6zlFHYx0y8lLh8Jw8kV5pU6+5YVJD8Qa1
# UFKGGYsH7l7DMXN2l/VS4ma45BNPAgMBAAGjggFJMIIBRTAdBgNVHQ4EFgQUsilZ
# QH4R55Db2xZ7RV3PFZAYkn0wHwYDVR0jBBgwFoAUn6cVXQBeYl2D9OXSZacbUzUZ
# 6XIwXwYDVR0fBFgwVjBUoFKgUIZOaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3Br
# aW9wcy9jcmwvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUyMFBDQSUyMDIwMTAoMSku
# Y3JsMGwGCCsGAQUFBwEBBGAwXjBcBggrBgEFBQcwAoZQaHR0cDovL3d3dy5taWNy
# b3NvZnQuY29tL3BraW9wcy9jZXJ0cy9NaWNyb3NvZnQlMjBUaW1lLVN0YW1wJTIw
# UENBJTIwMjAxMCgxKS5jcnQwDAYDVR0TAQH/BAIwADAWBgNVHSUBAf8EDDAKBggr
# BgEFBQcDCDAOBgNVHQ8BAf8EBAMCB4AwDQYJKoZIhvcNAQELBQADggIBAJAQxt6w
# PpMLTxHShgJ1ILjnYBCsZ/87z0ZDngK2ASxvHPAYNVRyaNcVydolJM150EpVeQGB
# rBGic/UuDEfhvPNWPZ5Y2bMYjA7UWWGV0A84cDMsEQdGhJnil10W1pDGhptT83W9
# bIgKI3rQi3zmCcXkkPgwxfJ3qlLx4AMiLpO2N+Ao+i6ZZrQEVD9oTONSt883Wvty
# sr6qSYvO3D8Q1LvN6Z/LHiQZGDBjVYF8Wqb+cWUkM9AGJyp5Td06n2GPtaoPRFz7
# /hVnrBCN6wjIKS/m6FQ3LYuE0OLaV5i0CIgWmaN82TgaeAu8LZOP0is4y/bRKvKb
# kn8WHvJYCI94azfIDdBqmNlO1+vs1/OkEglDjFP+JzhYZaqEaVGVUEjm7o6PDdnF
# JkIuDe9ELgpjKmSHwV0hagqKuOJ0QaVew06j5Q/9gbkqF5uK51MHEZ5x8kK65Syk
# h1GFK0cBCyO/90CpYEuWGiurY4Jo/7AWETdY+CefHml+W+W6Ohw+Cw3bj7510euX
# c7UUVptbybRSQMdIoKHxBPBORg7C732ITEFVaVthlHPao4gGMv+jMSG0IHRq4qF9
# Mst640YFRoHP6hln5f1QAQKgyGQRONvph81ojVPu9UBqK6EGhX8kI5BP5FhmuDKT
# I+nOmbAw0UEPW91b/b2r2eRNagSFwQ47Qv03MIIHcTCCBVmgAwIBAgITMwAAABXF
# 52ueAptJmQAAAAAAFTANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UEBhMCVVMxEzAR
# BgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1p
# Y3Jvc29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWljcm9zb2Z0IFJvb3QgQ2Vy
# dGlmaWNhdGUgQXV0aG9yaXR5IDIwMTAwHhcNMjEwOTMwMTgyMjI1WhcNMzAwOTMw
# MTgzMjI1WjB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYw
# JAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDCCAiIwDQYJKoZI
# hvcNAQEBBQADggIPADCCAgoCggIBAOThpkzntHIhC3miy9ckeb0O1YLT/e6cBwfS
# qWxOdcjKNVf2AX9sSuDivbk+F2Az/1xPx2b3lVNxWuJ+Slr+uDZnhUYjDLWNE893
# MsAQGOhgfWpSg0S3po5GawcU88V29YZQ3MFEyHFcUTE3oAo4bo3t1w/YJlN8OWEC
# esSq/XJprx2rrPY2vjUmZNqYO7oaezOtgFt+jBAcnVL+tuhiJdxqD89d9P6OU8/W
# 7IVWTe/dvI2k45GPsjksUZzpcGkNyjYtcI4xyDUoveO0hyTD4MmPfrVUj9z6BVWY
# bWg7mka97aSueik3rMvrg0XnRm7KMtXAhjBcTyziYrLNueKNiOSWrAFKu75xqRdb
# Z2De+JKRHh09/SDPc31BmkZ1zcRfNN0Sidb9pSB9fvzZnkXftnIv231fgLrbqn42
# 7DZM9ituqBJR6L8FA6PRc6ZNN3SUHDSCD/AQ8rdHGO2n6Jl8P0zbr17C89XYcz1D
# TsEzOUyOArxCaC4Q6oRRRuLRvWoYWmEBc8pnol7XKHYC4jMYctenIPDC+hIK12Nv
# DMk2ZItboKaDIV1fMHSRlJTYuVD5C4lh8zYGNRiER9vcG9H9stQcxWv2XFJRXRLb
# JbqvUAV6bMURHXLvjflSxIUXk8A8FdsaN8cIFRg/eKtFtvUeh17aj54WcmnGrnu3
# tz5q4i6tAgMBAAGjggHdMIIB2TASBgkrBgEEAYI3FQEEBQIDAQABMCMGCSsGAQQB
# gjcVAgQWBBQqp1L+ZMSavoKRPEY1Kc8Q/y8E7jAdBgNVHQ4EFgQUn6cVXQBeYl2D
# 9OXSZacbUzUZ6XIwXAYDVR0gBFUwUzBRBgwrBgEEAYI3TIN9AQEwQTA/BggrBgEF
# BQcCARYzaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9Eb2NzL1JlcG9z
# aXRvcnkuaHRtMBMGA1UdJQQMMAoGCCsGAQUFBwMIMBkGCSsGAQQBgjcUAgQMHgoA
# UwB1AGIAQwBBMAsGA1UdDwQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB8GA1UdIwQY
# MBaAFNX2VsuP6KJcYmjRPZSQW9fOmhjEMFYGA1UdHwRPME0wS6BJoEeGRWh0dHA6
# Ly9jcmwubWljcm9zb2Z0LmNvbS9wa2kvY3JsL3Byb2R1Y3RzL01pY1Jvb0NlckF1
# dF8yMDEwLTA2LTIzLmNybDBaBggrBgEFBQcBAQROMEwwSgYIKwYBBQUHMAKGPmh0
# dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9wa2kvY2VydHMvTWljUm9vQ2VyQXV0XzIw
# MTAtMDYtMjMuY3J0MA0GCSqGSIb3DQEBCwUAA4ICAQCdVX38Kq3hLB9nATEkW+Ge
# ckv8qW/qXBS2Pk5HZHixBpOXPTEztTnXwnE2P9pkbHzQdTltuw8x5MKP+2zRoZQY
# Iu7pZmc6U03dmLq2HnjYNi6cqYJWAAOwBb6J6Gngugnue99qb74py27YP0h1AdkY
# 3m2CDPVtI1TkeFN1JFe53Z/zjj3G82jfZfakVqr3lbYoVSfQJL1AoL8ZthISEV09
# J+BAljis9/kpicO8F7BUhUKz/AyeixmJ5/ALaoHCgRlCGVJ1ijbCHcNhcy4sa3tu
# PywJeBTpkbKpW99Jo3QMvOyRgNI95ko+ZjtPu4b6MhrZlvSP9pEB9s7GdP32THJv
# EKt1MMU0sHrYUP4KWN1APMdUbZ1jdEgssU5HLcEUBHG/ZPkkvnNtyo4JvbMBV0lU
# ZNlz138eW0QBjloZkWsNn6Qo3GcZKCS6OEuabvshVGtqRRFHqfG3rsjoiV5PndLQ
# THa1V1QJsWkBRH58oWFsc/4Ku+xBZj1p/cvBQUl+fpO+y/g75LcVv7TOPqUxUYS8
# vwLBgqJ7Fx0ViY1w/ue10CgaiQuPNtq6TPmb/wrpNPgkNWcr4A245oyZ1uEi6vAn
# Qj0llOZ0dFtq0Z4+7X6gMTN9vMvpe784cETRkPHIqzqKOghif9lwY1NNje6CbaUF
# EMFxBmoQtB1VM1izoXBm8qGCA00wggI1AgEBMIH5oYHRpIHOMIHLMQswCQYDVQQG
# EwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwG
# A1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3NvZnQg
# QW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046REMw
# MC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNlcnZp
# Y2WiIwoBATAHBgUrDgMCGgMVAM2vFFf+LPqyzWUEJcbw/UsXEPR7oIGDMIGApH4w
# fDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1Jl
# ZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMd
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTAwDQYJKoZIhvcNAQELBQACBQDs
# m07UMCIYDzIwMjUxMDE2MTEwMDM2WhgPMjAyNTEwMTcxMTAwMzZaMHQwOgYKKwYB
# BAGEWQoEATEsMCowCgIFAOybTtQCAQAwBwIBAAICFQwwBwIBAAICEiwwCgIFAOyc
# oFQCAQAwNgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAKMAgCAQACAweh
# IKEKMAgCAQACAwGGoDANBgkqhkiG9w0BAQsFAAOCAQEAYb2wNFGx0GXCqvH6DpTx
# 5nGEy49LOab7AHwHIMn0lXpCL1GYXUUqx+DwJiCJghPTIls/Udd5LaFS8qK7uHJa
# 0og3W1a4Rc5iF3+L7bWnq4mYz+E/6yQLzdFtSHAp7ecTlxPA9w3QcjCpUU6OQAkk
# 3t4b1lf3knbOVJGogupuAZ/FnT8T5c0LZmeDmOiFfXrteDr1aOvoTXf5/UwGqUzB
# TDAnBHmVohjoEzoaLOkQYCvxCnN0RwXPjnL3+6YQpr6GHrFk40fu08SLU010tSCH
# MSOD3hU0LT6OZFDCuDzeJc8yXh+stjwkVSqQCTHOZFEie+dQ0ZKSEsqcR99pAbMF
# ADGCBA0wggQJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5n
# dG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
# YXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwAhMz
# AAACA7seXAA4bHTKAAEAAAIDMA0GCWCGSAFlAwQCAQUAoIIBSjAaBgkqhkiG9w0B
# CQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIKZD2k0IwWgzzgvuMO7b
# wEQUvAI/EhMoE57T5U+DHTiPMIH6BgsqhkiG9w0BCRACLzGB6jCB5zCB5DCBvQQg
# SwPdG3GW9pPEU5lmelDDQOSw+ZV26jlLIr2H3D76Ey0wgZgwgYCkfjB8MQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAgO7HlwAOGx0ygABAAACAzAiBCBX
# rwA+B5P8D6eov7HkUguh7XNkYVDlfBRnVeSMUkl+WDANBgkqhkiG9w0BAQsFAASC
# AgB1vYECrtKEny5+xkMzl3eQmGVYvURJ8qPAzfMA0+LQxcYpcRRZvuHweFgV9oSp
# 05JH22fKAgLmS73nPU3iIg12Av7/AW29tbGaaDVNNKu8Ge9L4yN6DFczw9UiOrTQ
# xCoGVtIvH+4uT6EMXTD8ZyqElkWvmSASNHx44abUuWqqMYdgygoFhoAx58HoPA/E
# 866Ya3V/8RgdrOGqZk3avYgtZdCikshMHYoeSGltKlATl+otflt54R6i8nOMvkFm
# A4UFOZME2sQUUIlAX2e+YOJYdfHMiZUdEgmU1opq4aVo1HOuDQPWFnUiPxeq/yVU
# TOV4AYSQwWNIqX9/J5n2bYFAOjrlUun3cmbxTKzl+0p8SxIL97IXIRkOzY9zisaT
# drWT1AXi5rJC/QCKpWyVj7UnhIy6B+fAGv0miQlidbtEQBOnBd5BkbuAYcR6wZEl
# xRytd6pGUzF81EKajimH1WvBG8NoPDiBEEv4KwoaEVLEzeDJqaEUHB3fXOpq86Y9
# r3GONZo5n+46ORQTWW/kHDbMNrgURjwMbUaag38VC/9y8gE8wOSd4X30n5dhNrHC
# KM+MAkuUQmxglbqypmaGXW6sIgx6VxdI4cymTwRVhjP+RbuL0/PCwptIRnX0k7Q8
# aiu2jIIEKPW1HkpeQnN7rpy+gaW+/MQ7w2GpeQPNxE/1Rw==
# SIG # End Windows Authenticode signature block