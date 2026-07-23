#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-
# Originally written by Barry Warsaw <barry@python.org>
#
# Minimally patched to make it even more xgettext compatible
# by Peter Funk <pf@artcom-gmbh.de>
#
# 2002-11-22 Jürgen Hermann <jh@web.de>
# Added checks that _() only contains string literals, and
# command line args are resolved to module lists, i.e. you
# can now pass a filename, a module or package name, or a
# directory (including globbing chars, important for Win32).
# Made docstring fit in 80 chars wide displays using pydoc.
#

# for selftesting
try:
    import fintl
    _ = fintl.gettext
except ImportError:
    _ = lambda s: s

__doc__ = _("""pygettext -- Python equivalent of xgettext(1)

Many systems (Solaris, Linux, Gnu) provide extensive tools that ease the
internationalization of C programs. Most of these tools are independent of
the programming language and can be used from within Python programs.
Martin von Loewis' work[1] helps considerably in this regard.

There's one problem though; xgettext is the program that scans source code
looking for message strings, but it groks only C (or C++). Python
introduces a few wrinkles, such as dual quoting characters, triple quoted
strings, and raw strings. xgettext understands none of this.

Enter pygettext, which uses Python's standard tokenize module to scan
Python source code, generating .pot files identical to what GNU xgettext[2]
generates for C and C++ code. From there, the standard GNU tools can be
used.

A word about marking Python strings as candidates for translation. GNU
xgettext recognizes the following keywords: gettext, dgettext, dcgettext,
and gettext_noop. But those can be a lot of text to include all over your
code. C and C++ have a trick: they use the C preprocessor. Most
internationalized C source includes a #define for gettext() to _() so that
what has to be written in the source is much less. Thus these are both
translatable strings:

    gettext("Translatable String")
    _("Translatable String")

Python of course has no preprocessor so this doesn't work so well.  Thus,
pygettext searches only for _() by default, but see the -k/--keyword flag
below for how to augment this.

 [1] https://www.python.org/workshops/1997-10/proceedings/loewis.html
 [2] https://www.gnu.org/software/gettext/gettext.html

NOTE: pygettext attempts to be option and feature compatible with GNU
xgettext where ever possible. However some options are still missing or are
not fully implemented. Also, xgettext's use of command line switches with
option arguments is broken, and in these cases, pygettext just defines
additional switches.

Usage: pygettext [options] inputfile ...

Options:

    -a
    --extract-all
        Extract all strings.

    -d name
    --default-domain=name
        Rename the default output file from messages.pot to name.pot.

    -E
    --escape
        Replace non-ASCII characters with octal escape sequences.

    -D
    --docstrings
        Extract module, class, method, and function docstrings.  These do
        not need to be wrapped in _() markers, and in fact cannot be for
        Python to consider them docstrings. (See also the -X option).

    -h
    --help
        Print this help message and exit.

    -k word
    --keyword=word
        Keywords to look for in addition to the default set, which are:
        %(DEFAULTKEYWORDS)s

        You can have multiple -k flags on the command line.

    -K
    --no-default-keywords
        Disable the default set of keywords (see above).  Any keywords
        explicitly added with the -k/--keyword option are still recognized.

    --no-location
        Do not write filename/lineno location comments.

    -n
    --add-location
        Write filename/lineno location comments indicating where each
        extracted string is found in the source.  These lines appear before
        each msgid.  The style of comments is controlled by the -S/--style
        option.  This is the default.

    -o filename
    --output=filename
        Rename the default output file from messages.pot to filename.  If
        filename is `-' then the output is sent to standard out.

    -p dir
    --output-dir=dir
        Output files will be placed in directory dir.

    -S stylename
    --style stylename
        Specify which style to use for location comments.  Two styles are
        supported:

        Solaris  # File: filename, line: line-number
        GNU      #: filename:line

        The style name is case insensitive.  GNU style is the default.

    -v
    --verbose
        Print the names of the files being processed.

    -V
    --version
        Print the version of pygettext and exit.

    -w columns
    --width=columns
        Set width of output to columns.

    -x filename
    --exclude-file=filename
        Specify a file that contains a list of strings that are not be
        extracted from the input files.  Each string to be excluded must
        appear on a line by itself in the file.

    -X filename
    --no-docstrings=filename
        Specify a file that contains a list of files (one per line) that
        should not have their docstrings extracted.  This is only useful in
        conjunction with the -D option above.

If `inputfile' is -, standard input is read.
""")

import os
import importlib.machinery
import importlib.util
import sys
import glob
import time
import getopt
import ast
import token
import tokenize

__version__ = '1.5'

default_keywords = ['_']
DEFAULTKEYWORDS = ', '.join(default_keywords)

EMPTYSTRING = ''


