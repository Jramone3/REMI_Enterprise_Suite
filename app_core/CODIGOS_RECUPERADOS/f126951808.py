#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
imdbpy2sql.py script.

This script puts the data of the plain text data files into a
SQL database.

Copyright 2005-2020 Davide Alberani <da@erlug.linux.it>
               2006 Giuseppe "Cowo" Corbelli <cowo --> lugbs.linux.it>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import os
import sys
import getopt
import time
import re
import warnings
import operator
import dbm
from itertools import islice, chain
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
from gzip import GzipFile

from imdb.parser.sql.dbschema import DB_SCHEMA, dropTables, createTables, createIndexes
from imdb.parser.sql import soundex
from imdb.utils import analyze_title, analyze_name, date_and_notes, \
    build_name, build_title, normalizeName, normalizeTitle, _articles, \
        build_company_name, analyze_company_name, canonicalTitle
from imdb._exceptions import IMDbParserError, IMDbError
from imdb.parser.sql.alchemyadapter import getDBTables, setConnection


HELP = """imdbpy2sql.py usage:
    %s -d /directory/with/PlainTextDataFiles/ -u URI [-c /directory/for/CSV_files] [-i table,dbm] [--CSV-OPTIONS] [--COMPATIBILITY-OPTIONS]

        # NOTE: URI is something along the line:
                scheme://[user[:password]@]host[:port]/database[?parameters]

                Examples:
                mysql://user:password@host/database
                postgres://user:password@host/database
                sqlite:/tmp/imdb.db
                sqlite:/C|/full/path/to/database

        # NOTE: CSV mode (-c path):
                A directory is used to store CSV files; on supported
                database servers it should be really fast.

        # NOTE: imdbIDs store/restore (-i method):
                Valid options are 'table' (imdbIDs stored in a temporary
                table of the database) or 'dbm' (imdbIDs stored on a dbm
                file - this is the default if CSV is used).

        # NOTE: --CSV-OPTIONS can be:
            --csv-ext STRING        files extension (.csv)
            --csv-only-write        exit after the CSV files are written.
            --csv-only-load         load an existing set of CSV files.

        # NOTE: --COMPATIBILITY-OPTIONS can be one of:
            --mysql-innodb          insert data into a MySQL MyISAM db,
                                    and then convert it to InnoDB.
            --mysql-force-myisam    force the creation of MyISAM tables.
            --ms-sqlserver          compatibility mode for Microsoft SQL Server
                                    and SQL Express.
            --sqlite-transactions   uses transactions, to speed-up SQLite.


                See README.sqldb for more information.
""" % sys.argv[0]

# Directory containing the IMDb's Plain Text Data Files.
IMDB_PTDF_DIR = None
# URI used to connect to the database.
URI = None
# List of tables of the database.
DB_TABLES = []
# Max allowed recursion, inserting data.
MAX_RECURSION = 10
# Method used to (re)store imdbIDs.
IMDBIDS_METHOD = None
# If set, this directory is used to output CSV files.
CSV_DIR = None
CSV_CURS = None
CSV_ONLY_WRITE = False
CSV_ONLY_LOAD = False
CSV_EXT = '.csv'
CSV_EOL = '\n'
CSV_DELIMITER = ','
CSV_QUOTE = '"'
CSV_ESCAPE = '"'
CSV_NULL = 'NULL'
CSV_QUOTEINT = False
CSV_LOAD_SQL = None
CSV_MYSQL = "LOAD DATA LOCAL INFILE '%(file)s' INTO TABLE `%(table)s` FIELDS TERMINATED BY '%(delimiter)s' ENCLOSED BY '%(quote)s' ESCAPED BY '%(escape)s' LINES TERMINATED BY '%(eol)s'"
CSV_PGSQL = "COPY %(table)s FROM '%(file)s' WITH DELIMITER AS '%(delimiter)s' NULL AS '%(null)s' QUOTE AS '%(quote)s' ESCAPE AS '%(escape)s' CSV"
CSV_DB2 = "CALL SYSPROC.ADMIN_CMD('LOAD FROM %(file)s OF del MODIFIED BY lobsinfile INSERT INTO %(table)s')"

# Temporary fix for old style titles.
# FIX_OLD_STYLE_TITLES = True

# Store custom queries specified on the command line.
CUSTOM_QUERIES = {}
# Allowed time specification, for custom queries.
ALLOWED_TIMES = ('BEGIN', 'BEFORE_DROP', 'BEFORE_CREATE', 'AFTER_CREATE',
                 'BEFORE_MOVIES', 'BEFORE_COMPANIES', 'BEFORE_CAST',
                 'BEFORE_RESTORE', 'BEFORE_INDEXES', 'END', 'BEFORE_MOVIES_TODB',
                 'AFTER_MOVIES_TODB', 'BEFORE_PERSONS_TODB',
                 'AFTER_PERSONS_TODB', 'BEFORE_SQLDATA_TODB',
                 'AFTER_SQLDATA_TODB', 'BEFORE_AKAMOVIES_TODB',
                 'AFTER_AKAMOVIES_TODB', 'BEFORE_CHARACTERS_TODB',
                 'AFTER_CHARACTERS_TODB', 'BEFORE_COMPANIES_TODB',
                 'AFTER_COMPANIES_TODB', 'BEFORE_EVERY_TODB',
                 'AFTER_EVERY_TODB', 'BEFORE_CSV_LOAD', 'BEFORE_CSV_TODB',
                 'AFTER_CSV_TODB')

# Shortcuts for some compatibility options.
MYSQLFORCEMYISAM_OPTS = ['-e',
                         'AFTER_CREATE:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=MyISAM;']
MYSQLINNODB_OPTS = ['-e',
                    'AFTER_CREATE:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=MyISAM;',
                    '-e',
                    'BEFORE_INDEXES:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=InnoDB;']
SQLSERVER_OPTS = ['-e', 'BEFORE_MOVIES_TODB:SET IDENTITY_INSERT %(table)s ON;',
                  '-e', 'AFTER_MOVIES_TODB:SET IDENTITY_INSERT %(table)s OFF;',
                  '-e', 'BEFORE_PERSONS_TODB:SET IDENTITY_INSERT %(table)s ON;',
                  '-e', 'AFTER_PERSONS_TODB:SET IDENTITY_INSERT %(table)s OFF;',
                  '-e', 'BEFORE_COMPANIES_TODB:SET IDENTITY_INSERT %(table)s ON;',
                  '-e', 'AFTER_COMPANIES_TODB:SET IDENTITY_INSERT %(table)s OFF;',
                  '-e', 'BEFORE_CHARACTERS_TODB:SET IDENTITY_INSERT %(table)s ON;',
                  '-e', 'AFTER_CHARACTERS_TODB:SET IDENTITY_INSERT %(table)s OFF;',
                  '-e', 'BEFORE_AKAMOVIES_TODB:SET IDENTITY_INSERT %(table)s ON;',
                  '-e', 'AFTER_AKAMOVIES_TODB:SET IDENTITY_INSERT %(table)s OFF;']
SQLITE_OPTS = ['-e', 'BEGIN:PRAGMA synchronous = OFF;',
               '-e', 'BEFORE_EVERY_TODB:BEGIN TRANSACTION;',
               '-e', 'AFTER_EVERY_TODB:COMMIT;',
               '-e', 'BEFORE_INDEXES:BEGIN TRANSACTION;',
               'e', 'END:COMMIT;']

if '--mysql-innodb' in sys.argv[1:]:
    sys.argv += MYSQLINNODB_OPTS
if '--mysql-force-myisam' in sys.argv[1:]:
    sys.argv += MYSQLFORCEMYISAM_OPTS
if '--ms-sqlserver' in sys.argv[1:]:
    sys.argv += SQLSERVER_OPTS
if '--sqlite-transactions' in sys.argv[1:]:
    sys.argv += SQLITE_OPTS

# Manage arguments list.
try:
    optlist, args = getopt.getopt(sys.argv[1:], 'u:d:e:c:i:h',
                                                ['uri=', 'data=', 'execute=',
                                                 'mysql-innodb', 'ms-sqlserver',
                                                 'sqlite-transactions',
                                                 'fix-old-style-titles',
                                                 'mysql-force-myisam',
                                                 'csv-only-write',
                                                 'csv-only-load',
                                                 'csv=', 'csv-ext=',
                                                 'imdbids=', 'help'])
except getopt.error as e:
    print('Troubles with arguments.')
    print(HELP)
    sys.exit(2)

for opt in optlist:
    if opt[0] in ('-d', '--data'):
        IMDB_PTDF_DIR = opt[1]
    elif opt[0] in ('-u', '--uri'):
        URI = opt[1]
    elif opt[0] in ('-c', '--csv'):
        CSV_DIR = opt[1]
    elif opt[0] == '--csv-ext':
        CSV_EXT = opt[1]
    elif opt[0] in ('-i', '--imdbids'):
        IMDBIDS_METHOD = opt[1]
    elif opt[0] in ('-e', '--execute'):
        if opt[1].find(':') == -1:
            print('WARNING: wrong command syntax: "%s"' % opt[1])
            continue
        when, cmd = opt[1].split(':', 1)
        if when not in ALLOWED_TIMES:
            print('WARNING: unknown time: "%s"' % when)
            continue
        if when == 'BEFORE_EVERY_TODB':
            for nw in ('BEFORE_MOVIES_TODB', 'BEFORE_PERSONS_TODB',
                       'BEFORE_SQLDATA_TODB', 'BEFORE_AKAMOVIES_TODB',
                       'BEFORE_CHARACTERS_TODB', 'BEFORE_COMPANIES_TODB'):
                CUSTOM_QUERIES.setdefault(nw, []).append(cmd)
        elif when == 'AFTER_EVERY_TODB':
            for nw in ('AFTER_MOVIES_TODB', 'AFTER_PERSONS_TODB',
                       'AFTER_SQLDATA_TODB', 'AFTER_AKAMOVIES_TODB',
                       'AFTER_CHARACTERS_TODB', 'AFTER_COMPANIES_TODB'):
                CUSTOM_QUERIES.setdefault(nw, []).append(cmd)
        else:
            CUSTOM_QUERIES.setdefault(when, []).append(cmd)
    elif opt[0] == '--fix-old-style-titles':
        warnings.warn('The --fix-old-style-titles argument is obsolete.')
    elif opt[0] == '--csv-only-write':
        CSV_ONLY_WRITE = True
    elif opt[0] == '--csv-only-load':
        CSV_ONLY_LOAD = True
    elif opt[0] in ('-h', '--help'):
        print(HELP)
        sys.exit(0)

if IMDB_PTDF_DIR is None:
    print('You must supply the directory with the plain text data files')
    print(HELP)
    sys.exit(2)

if URI is None:
    print('You must supply the URI for the database connection')
    print(HELP)
    sys.exit(2)

if IMDBIDS_METHOD not in (None, 'dbm', 'table'):
    print('the method to (re)store imdbIDs must be one of "dbm" or "table"')
    print(HELP)
    sys.exit(2)

if (CSV_ONLY_WRITE or CSV_ONLY_LOAD) and not CSV_DIR:
    print('You must specify the CSV directory with the -c argument')
    print(HELP)
    sys.exit(3)


# Some warnings and notices.
URIlower = URI.lower()

if URIlower.startswith('mysql'):
    if '--mysql-force-myisam' in sys.argv[1:] and \
            '--mysql-innodb' in sys.argv[1:]:
        print('\nWARNING: there is no sense in mixing the --mysql-innodb and\n'
              '--mysql-force-myisam command line options!\n')
    elif '--mysql-innodb' in sys.argv[1:]:
        print("\nNOTICE: you've specified the --mysql-innodb command line\n"
              "option; you should do this ONLY IF your system uses InnoDB\n"
              "tables or you really want to use InnoDB; if you're running\n"
              "a MyISAM-based database, please omit any option; if you\n"
              "want to force MyISAM usage on a InnoDB-based database,\n"
              "try the --mysql-force-myisam command line option, instead.\n")
    elif '--mysql-force-myisam' in sys.argv[1:]:
        print("\nNOTICE: you've specified the --mysql-force-myisam command\n"
              "line option; you should do this ONLY IF your system uses\n"
              "InnoDB tables and you want to use MyISAM tables, instead.\n")
    else:
        print("\nNOTICE: IF you're using InnoDB tables, data insertion can\n"
              "be very slow; you can switch to MyISAM tables - forcing it\n"
              "with the --mysql-force-myisam option - OR use the\n"
              "--mysql-innodb command line option, but DON'T USE these if\n"
              "you're already working on MyISAM tables, because it will\n"
              "force MySQL to use InnoDB, and performances will be poor.\n")
elif URIlower.startswith('mssql') and \
        '--ms-sqlserver' not in sys.argv[1:]:
    print("\nWARNING: you're using MS SQLServer without the --ms-sqlserver\n"
          "command line option: if something goes wrong, try using it.\n")
elif URIlower.startswith('sqlite') and \
        '--sqlite-transactions' not in sys.argv[1:]:
    print("\nWARNING: you're using SQLite without the --sqlite-transactions\n"
          "command line option: you'll have very poor performances!  Try\n"
          "using it.\n")
if ('--mysql-force-myisam' in sys.argv[1:] and
        not URIlower.startswith('mysql')) or ('--mysql-innodb' in
   sys.argv[1:] and not URIlower.startswith('mysql')) or ('--ms-sqlserver'
                                                          in sys.argv[1:] and not URIlower.startswith('mssql')) or \
        ('--sqlite-transactions' in sys.argv[1:] and
         not URIlower.startswith('sqlite')):
    print("\nWARNING: you've specified command line options that don't\n"
          "belong to the database server you're using: proceed at your\n"
          "own risk!\n")


if CSV_DIR:
    if URIlower.startswith('mysql'):
        CSV_LOAD_SQL = CSV_MYSQL
    elif URIlower.startswith('postgres'):
        CSV_LOAD_SQL = CSV_PGSQL
    elif URIlower.startswith('ibm'):
        CSV_LOAD_SQL = CSV_DB2
        CSV_NULL = ''
    else:
        print("\nERROR: importing CSV files is not supported for this database")
        if not CSV_ONLY_WRITE:
            sys.exit(3)


DB_TABLES = getDBTables(URI)
for t in DB_TABLES:
    globals()[t._imdbpyName] = t


#-----------------------
# CSV Handling.


class CSVCursor(object):

    """Emulate a cursor object, but instead it writes data to a set
    of CSV files."""

    def __init__(self, csvDir, csvExt=CSV_EXT, csvEOL=CSV_EOL,
                 delimeter=CSV_DELIMITER, quote=CSV_QUOTE, escape=CSV_ESCAPE,
                 null=CSV_NULL, quoteInteger=CSV_QUOTEINT):
        """Initialize a CSVCursor object; csvDir is the directory where the
        CSV files will be stored."""
        self.csvDir = csvDir
        self.csvExt = csvExt
        self.csvEOL = csvEOL
        self.delimeter = delimeter
        self.quote = quote
        self.escape = escape
        self.escaped = '%s%s' % (escape, quote)
        self.null = null
        self.quoteInteger = quoteInteger
        self._fdPool = {}
        self._lobFDPool = {}
        self._counters = {}

    def buildLine(self, items, tableToAddID=False, rawValues=(),
                  lobFD=None, lobFN=None):
        """Build a single text line for a set of information."""
        # FIXME: there are too many special cases to handle, and that
        #        affects performances: management of LOB files, at least,
        #        must be moved away from here.
        quote = self.quote
        null = self.null
        escaped = self.escaped
        quoteInteger = self.quoteInteger
        if not tableToAddID:
            r = []
        else:
            _counters = self._counters
            r = [_counters[tableToAddID]]
            _counters[tableToAddID] += 1
        r += list(items)
        for idx, val in enumerate(r):
            if val is None:
                r[idx] = null
                continue
            if (not quoteInteger) and isinstance(val, int):
                r[idx] = str(val)
                continue
            if lobFD and idx == 3:
                continue
            val = str(val)
            if quote:
                val = '%s%s%s' % (quote, val.replace(quote, escaped), quote)
            r[idx] = val
        # Add RawValue(s), if present.
        rinsert = r.insert
        if tableToAddID:
            shift = 1
        else:
            shift = 0
        for idx, item in rawValues:
            rinsert(idx + shift, item)
        if lobFD:
            # XXX: totally tailored to suit person_info.info column!
            val3 = r[3]
            val3len = len(val3 or '') or -1
            if val3len == -1:
                val3off = 0
            else:
                val3off = lobFD.tell()
            r[3] = '%s.%d.%d/' % (lobFN, val3off, val3len)
            lobFD.write(val3)
        # Build the line and add the end-of-line.
        ret = '%s%s' % (self.delimeter.join(r), self.csvEOL)
        ret = ret.encode('latin1', 'ignore')
        return ret

    def executemany(self, sqlstr, items):
        """Emulate the executemany method of a cursor, but writes the
        data in a set of CSV files."""
        # XXX: find a safer way to get the table/file name!
        tName = sqlstr.split()[2]
        lobFD = None
        lobFN = None
        doLOB = False
        # XXX: ugly special case, to create the LOB file.
        if URIlower.startswith('ibm') and tName == 'person_info':
            doLOB = True
        # Open the file descriptor or get it from the pool.
        if tName in self._fdPool:
            tFD = self._fdPool[tName]
            lobFD = self._lobFDPool.get(tName)
            lobFN = getattr(lobFD, 'name', None)
            if lobFN:
                lobFN = os.path.basename(lobFN)
        else:
            tFD = open(os.path.join(CSV_DIR, tName + self.csvExt), 'wb')
            self._fdPool[tName] = tFD
            if doLOB:
                lobFN = '%s.lob' % tName
                lobFD = open(os.path.join(CSV_DIR, lobFN), 'wb')
                self._lobFDPool[tName] = lobFD
        buildLine = self.buildLine
        tableToAddID = False
        if tName in ('cast_info', 'movie_info', 'person_info',
                     'movie_companies', 'movie_link', 'aka_name',
                     'complete_cast', 'movie_info_idx', 'movie_keyword'):
            tableToAddID = tName
            if tName not in self._counters:
                self._counters[tName] = 1
        # Identify if there are RawValue in the VALUES (...) portion of
        # the query.
        parIdx = sqlstr.rfind('(')
        rawValues = []
        vals = sqlstr[parIdx + 1:-1]
        if parIdx != 0:
            vals = sqlstr[parIdx + 1:-1]
            for idx, item in enumerate(vals.split(', ')):
                if item[0] in ('%', '?', ':'):
                    continue
                rawValues.append((idx, item))
        # Write these lines.
        tFD.writelines(buildLine(i, tableToAddID=tableToAddID,
                                 rawValues=rawValues, lobFD=lobFD, lobFN=lobFN)
                       for i in items)
        # Flush to disk, so that no truncaded entries are ever left.
        # XXX: is this a good idea?
        tFD.flush()

    def fileNames(self):
        """Return the list of file names."""
        return [fd.name for fd in list(self._fdPool.values())]

    def buildFakeFileNames(self):
        """Populate the self._fdPool dictionary with fake objects
        taking file names from the content of the self.csvDir directory."""
        class _FakeFD(object):
            pass
        for fname in os.listdir(self.csvDir):
            if not fname.endswith(CSV_EXT):
                continue
            fpath = os.path.join(self.csvDir, fname)
            if not os.path.isfile(fpath):
                continue
            fd = _FakeFD()
            fd.name = fname
            self._fdPool[fname[:-len(CSV_EXT)]] = fd

    def close(self, tName):
        """Close a given table/file."""
        if tName in self._fdPool:
            self._fdPool[tName].close()

    def closeAll(self):
        """Close all open file descriptors."""
        for fd in list(self._fdPool.values()):
            fd.close()
        for fd in list(self._lobFDPool.values()):
            fd.close()


def loadCSVFiles():
    """Load every CSV file into the database."""
    CSV_REPL = {'quote': CSV_QUOTE, 'delimiter': CSV_DELIMITER,
                'escape': CSV_ESCAPE, 'null': CSV_NULL, 'eol': CSV_EOL}
    for fName in CSV_CURS.fileNames():
        connectObject.commit()
        tName = os.path.basename(fName[:-len(CSV_EXT)])
        cfName = os.path.join(CSV_DIR, fName)
        CSV_REPL['file'] = cfName
        CSV_REPL['table'] = tName
        sqlStr = CSV_LOAD_SQL % CSV_REPL
        print(' * LOADING CSV FILE %s...' % cfName)
        sys.stdout.flush()
        executeCustomQueries('BEFORE_CSV_TODB')
        try:
            CURS.execute(sqlStr)
            try:
                res = CURS.fetchall()
                if res:
                    print('LOADING OUTPUT:', res)
            except:
                pass
        except Exception as e:
            print('ERROR: unable to import CSV file %s: %s' % (cfName, str(e)))
            continue
        connectObject.commit()
        executeCustomQueries('AFTER_CSV_TODB')

#-----------------------


conn = setConnection(URI, DB_TABLES)
if CSV_DIR:
    # Go for a CSV ride...
    CSV_CURS = CSVCursor(CSV_DIR)

# Extract exceptions to trap.
try:
    OperationalError = conn.module.OperationalError
except AttributeError as e:
    warnings.warn('Unable to import OperationalError; report this as a bug, '
                  'since it will mask important exceptions: %s' % e)
    OperationalError = Exception
try:
    IntegrityError = conn.module.IntegrityError
except AttributeError as e:
    warnings.warn('Unable to import IntegrityError')
    IntegrityError = Exception

connectObject = conn.getConnection()

# Cursor object.
CURS = connectObject.cursor()

# Name of the database and style of the parameters.
DB_NAME = conn.dbName
PARAM_STYLE = conn.paramstyle


def _get_imdbids_method():
    """Return the method to be used to (re)store
    imdbIDs (one of 'dbm' or 'table')."""
    if IMDBIDS_METHOD:
        return IMDBIDS_METHOD
    if CSV_DIR:
        return 'dbm'
    return 'table'


def tableName(table):
    """Return a string with the name of the table in the current db."""
    return table.sqlmeta.table


def colName(table, column):
    """Return a string with the name of the column in the current db."""
    if column == 'id':
        return table.sqlmeta.idName
    return table.sqlmeta.columns[column].dbName


class RawValue(object):

    """String-like objects to store raw SQL parameters, that are not
    intended to be replaced with positional parameters, in the query."""

    def __init__(self, s, v):
        self.string = s
        self.value = v

    def __str__(self):
        return self.string


def _makeConvNamed(cols):
    """Return a function to be used to convert a list of parameters
    from positional style to named style (convert from a list of
    tuples to a list of dictionaries."""
    nrCols = len(cols)

    def _converter(params):
        for paramIndex, paramSet in enumerate(params):
            d = {}
            for i in range(nrCols):
                d[cols[i]] = paramSet[i]
            params[paramIndex] = d
        return params
    return _converter


def createSQLstr(table, cols, command='INSERT'):
    """Given a table and a list of columns returns a sql statement
    useful to insert a set of data in the database.
    Along with the string, also a function useful to convert parameters
    from positional to named style is returned."""
    sqlstr = '%s INTO %s ' % (command, tableName(table))
    colNames = []
    values = []
    convCols = []
    count = 1

    def _valStr(s, index):
        if DB_NAME in ('mysql', 'postgres'):
            return '%s'
        elif PARAM_STYLE == 'format':
            return '%s'
        elif PARAM_STYLE == 'qmark':
            return '?'
        elif PARAM_STYLE == 'numeric':
            return ':%s' % index
        elif PARAM_STYLE == 'named':
            return ':%s' % s
        elif PARAM_STYLE == 'pyformat':
            return '%(' + s + ')s'
        return '%s'
    for col in cols:
        if isinstance(col, RawValue):
            colNames.append(colName(table, col.string))
            values.append(str(col.value))
        elif col == 'id':
            colNames.append(table.sqlmeta.idName)
            values.append(_valStr('id', count))
            convCols.append(col)
            count += 1
        else:
            colNames.append(colName(table, col))
            values.append(_valStr(col, count))
            convCols.append(col)
            count += 1
    sqlstr += '(%s) ' % ', '.join(colNames)
    sqlstr += 'VALUES (%s)' % ', '.join(values)
    if DB_NAME not in ('mysql', 'postgres') and \
            PARAM_STYLE in ('named', 'pyformat'):
        converter = _makeConvNamed(convCols)
    else:
        # Return the list itself.
        converter = lambda x: x
    return sqlstr, converter


def _(s, truncateAt=None):
    """Nicely print a string to sys.stdout, optionally
    truncating it a the given char."""
    if truncateAt is not None:
        s = s[:truncateAt]
    return s

if not hasattr(os, 'times'):
    def times():
        """Fake times() function."""
        return 0.0, 0.0, 0.0, 0.0, 0.0
    os.times = times

# Show time consumed by the single function call.
CTIME = int(time.time())
BEGIN_TIME = CTIME
CTIMES = os.times()
BEGIN_TIMES = CTIMES


def _minSec(*t):
    """Return a tuple of (mins, secs, ...) - two for every item passed."""
    l = []
    for i in t:
        l.extend(divmod(int(i), 60))
    return tuple(l)


def t(s, sinceBegin=False):
    """Pretty-print timing information."""
    global CTIME, CTIMES
    nt = int(time.time())
    ntimes = os.times()
    if not sinceBegin:
        ct = CTIME
        cts = CTIMES
    else:
        ct = BEGIN_TIME
        cts = BEGIN_TIMES
    print('# TIME', s,
          ': %dmin, %dsec (wall) %dmin, %dsec (user) %dmin, %dsec (system)'
          % _minSec(nt - ct, ntimes[0] - cts[0], ntimes[1] - cts[1]))
    if not sinceBegin:
        CTIME = nt
        CTIMES = ntimes


def title_soundex(title):
    """Return the soundex code for the given title; the (optional) starting
    article is pruned.  It assumes to receive a title without year/imdbIndex
    or kind indications, but just the title string, as the one in the
    analyze_title(title)['title'] value."""
    if not title:
        return None
    # Convert to canonical format.
    title = canonicalTitle(title)
    ts = title.split(', ')
    # Strip the ending article, if any.
    if ts[-1].lower() in _articles:
        title = ', '.join(ts[:-1])
    return soundex(title)


def name_soundexes(name, character=False):
    """Return three soundex codes for the given name; the name is assumed
    to be in the 'surname, name' format, without the imdbIndex indication,
    as the one in the analyze_name(name)['name'] value.
    The first one is the soundex of the name in the canonical format.
    The second is the soundex of the name in the normal format, if different
    from the first one.
    The third is the soundex of the surname, if different from the
    other two values."""
    if not name:
        return None, None, None
    s1 = soundex(name)
    name_normal = normalizeName(name)
    s2 = soundex(name_normal)
    if s1 == s2:
        s2 = None
    if not character:
        namesplit = name.split(', ')
        s3 = soundex(namesplit[0])
    else:
        s3 = soundex(name.split(' ')[-1])
    if s3 and s3 in (s1, s2):
        s3 = None
    return s1, s2, s3


# Tags to identify where the meaningful data begin/end in files.
MOVIES = 'movies.list.gz'
MOVIES_START = ('MOVIES LIST', '===========', '')
MOVIES_STOP = '--------------------------------------------------'
CAST_START = ('Name', '----')
CAST_STOP = '-----------------------------'
RAT_START = ('MOVIE RATINGS REPORT', '',
             'New  Distribution  Votes  Rank  Title')
RAT_STOP = '\n'
RAT_TOP250_START = ('note: for this top 250', '', 'New  Distribution')
RAT_BOT10_START = ('BOTTOM 10 MOVIES', '', 'New  Distribution')
TOPBOT_STOP = '\n'
AKAT_START = ('AKA TITLES LIST', '=============', '', '', '')
AKAT_IT_START = ('AKA TITLES LIST ITALIAN', '=======================', '', '')
AKAT_DE_START = ('AKA TITLES LIST GERMAN', '======================', '')
AKAT_ISO_START = ('AKA TITLES LIST ISO', '===================', '')
AKAT_HU_START = ('AKA TITLES LIST HUNGARIAN', '=========================', '')
AKAT_NO_START = ('AKA TITLES LIST NORWEGIAN', '=========================', '')
AKAN_START = ('AKA NAMES LIST', '=============', '')
AV_START = ('ALTERNATE VERSIONS LIST', '=======================', '', '')
MINHASH_STOP = '-------------------------'
GOOFS_START = ('GOOFS LIST', '==========', '')
QUOTES_START = ('QUOTES LIST', '=============')
CC_START = ('CRAZY CREDITS', '=============')
BIO_START = ('BIOGRAPHY LIST', '==============')
BUS_START = ('BUSINESS LIST', '=============', '')
BUS_STOP = '                                    ====='
CER_START = ('CERTIFICATES LIST', '=================')
COL_START = ('COLOR INFO LIST', '===============')
COU_START = ('COUNTRIES LIST', '==============')
DIS_START = ('DISTRIBUTORS LIST', '=================', '')
GEN_START = ('8: THE GENRES LIST', '==================', '')
KEY_START = ('8: THE KEYWORDS LIST', '====================', '')
LAN_START = ('LANGUAGE LIST', '=============')
LOC_START = ('LOCATIONS LIST', '==============', '')
MIS_START = ('MISCELLANEOUS COMPANY LIST', '============================')
MIS_STOP = '--------------------------------------------------------------------------------'
PRO_START = ('PRODUCTION COMPANIES LIST', '=========================', '')
RUN_START = ('RUNNING TIMES LIST', '==================')
SOU_START = ('SOUND-MIX LIST', '==============')
SFX_START = ('SFXCO COMPANIES LIST', '====================', '')
TCN_START = ('TECHNICAL LIST', '==============', '', '')
LSD_START = ('LASERDISC LIST', '==============', '------------------------')
LIT_START = ('LITERATURE LIST', '===============', '')
LIT_STOP = 'COPYING POLICY'
LINK_START = ('MOVIE LINKS LIST', '================', '')
MPAA_START = ('MPAA RATINGS REASONS LIST', '=========================')
PLOT_START = ('PLOT SUMMARIES LIST', '===================', '')
RELDATE_START = ('RELEASE DATES LIST', '==================')
SNDT_START = ('SOUNDTRACKS', '=============', '', '', '')
TAGL_START = ('TAG LINES LIST', '==============', '', '')
TAGL_STOP = '-----------------------------------------'
TRIV_START = ('FILM TRIVIA', '===========', '')
COMPCAST_START = ('CAST COVERAGE TRACKING LIST', '===========================')
COMPCREW_START = ('CREW COVERAGE TRACKING LIST', '===========================')
COMP_STOP = '---------------'

GzipFileRL = GzipFile.readline


class SourceFile(GzipFile):

    """Instances of this class are used to read gzipped files,
    starting from a defined line to a (optionally) given end."""

    def __init__(self, filename=None, mode=None, start=(), stop=None,
                 pwarning=1, *args, **kwds):
        filename = os.path.join(IMDB_PTDF_DIR, filename)
        try:
            GzipFile.__init__(self, filename, mode, *args, **kwds)
        except IOError as e:
            if not pwarning:
                raise
            print('WARNING WARNING WARNING')
            print('WARNING unable to read the "%s" file.' % filename)
            print('WARNING The file will be skipped, and the contained')
            print('WARNING information will NOT be stored in the database.')
            print('WARNING Complete error: ', e)
            # re-raise the exception.
            raise
        self.start = start
        for item in start:
            itemlen = len(item)
            for line in self:
                line = line.decode('latin1')
                if line[:itemlen] == item:
                    break
        self.set_stop(stop)

    def set_stop(self, stop):
        if stop is not None:
            self.stop = stop
            self.stoplen = len(self.stop)
            self.readline = self.readline_checkEnd
        else:
            self.readline = self.readline_NOcheckEnd

    def readline_NOcheckEnd(self, size=-1):
        line = GzipFile.readline(self, size)
        return str(line, 'latin_1', 'ignore')

    def readline_checkEnd(self, size=-1):
        line = GzipFile.readline(self, size)
        if self.stop is not None and line[:self.stoplen] == self.stop:
            return ''
        return str(line, 'latin_1', 'ignore')

    def getByHashSections(self):
        return getSectionHash(self)

    def getByNMMVSections(self):
        return getSectionNMMV(self)


def getSectionHash(fp):
    """Return sections separated by lines starting with #."""
    curSectList = []
    curSectListApp = curSectList.append
    curTitle = ''
    joiner = ''.join
    for line in fp:
        if line and line[0] == '#':
            if curSectList and curTitle:
                yield curTitle, joiner(curSectList)
                curSectList[:] = []
                curTitle = ''
            curTitle = line[2:]
        else:
            curSectListApp(line)
    if curSectList and curTitle:
        yield curTitle, joiner(curSectList)
        curSectList[:] = []
        curTitle = ''

NMMVSections = dict([(x, None) for x in ('MV: ', 'NM: ', 'OT: ', 'MOVI')])


def getSectionNMMV(fp):
    """Return sections separated by lines starting with 'NM: ', 'MV: ',
    'OT: ' or 'MOVI'."""
    curSectList = []
    curSectListApp = curSectList.append
    curNMMV = ''
    joiner = ''.join
    for line in fp:
        if line[:4] in NMMVSections:
            if curSectList and curNMMV:
                yield curNMMV, joiner(curSectList)
                curSectList[:] = []
                curNMMV = ''
            if line[:4] == 'MOVI':
                curNMMV = line[6:]
            else:
                curNMMV = line[4:]
        elif not (line and line[0] == '-'):
            curSectListApp(line)
    if curSectList and curNMMV:
        yield curNMMV, joiner(curSectList)
        curSectList[:] = []
        curNMMV = ''


def counter(initValue=1):
    """A counter implemented using a generator."""
    i = initValue
    while 1:
        yield i
        i += 1


class _BaseCache(dict):

    """Base class for Movie and Person basic information."""

    def __init__(self, d=None, flushEvery=100000):
        dict.__init__(self)
        # Flush data into the SQL database every flushEvery entries.
        self.flushEvery = flushEvery
        self._tmpDict = {}
        self._flushing = 0
        self._deferredData = {}
        self._recursionLevel = 0
        self._table_name = ''
        self._id_for_custom_q = ''
        if d is not None:
            for k, v in d.items():
                self[k] = v

    def __setitem__(self, key, counter):
        """Every time a key is set, its value is the counter;
        every flushEvery, the temporary dictionary is
        flushed to the database, and then zeroed."""
        if counter % self.flushEvery == 0:
            self.flush()
        dict.__setitem__(self, key, counter)
        if not self._flushing:
            self._tmpDict[key] = counter
        else:
            self._deferredData[key] = counter

    def flush(self, quiet=0, _recursionLevel=0):
        """Flush to the database."""
        if self._flushing:
            return
        self._flushing = 1
        if _recursionLevel >= MAX_RECURSION:
            print('WARNING recursion level exceded trying to flush data')
            print('WARNING this batch of data is lost (%s).' % self.className)
            self._tmpDict.clear()
            return
        if self._tmpDict:
            # Horrible hack to know if AFTER_%s_TODB has run.
            _after_has_run = False
            keys = {'table': self._table_name}
            try:
                executeCustomQueries('BEFORE_%s_TODB' % self._id_for_custom_q,
                                     _keys=keys, _timeit=False)
                self._toDB(quiet)
                executeCustomQueries('AFTER_%s_TODB' % self._id_for_custom_q,
                                     _keys=keys, _timeit=False)
                _after_has_run = True
                self._tmpDict.clear()
            except OperationalError as e:
                # XXX: I'm not sure this is the right thing (and way)
                #      to proceed.
                if not _after_has_run:
                    executeCustomQueries('AFTER_%s_TODB' % self._id_for_custom_q,
                                         _keys=keys, _timeit=False)
                # Dataset too large; split it in two and retry.
                # XXX: new code!
                # the same class instance (self) is used, instead of
                # creating two separated objects.
                _recursionLevel += 1
                self._flushing = 0
                firstHalf = {}
                poptmpd = self._tmpDict.popitem
                originalLength = len(self._tmpDict)
                for x in range(1, 1 + originalLength // 2):
                    k, v = poptmpd()
                    firstHalf[k] = v
                self._secondHalf = self._tmpDict
                self._tmpDict = firstHalf
                print(' * TOO MANY DATA (%s items in %s), recursion: %s' %
                      (originalLength,
                       self.className,
                       _recursionLevel))
                print('   * SPLITTING (run 1 of 2), recursion: %s' %
                      _recursionLevel)
                self.flush(quiet=quiet, _recursionLevel=_recursionLevel)
                self._tmpDict = self._secondHalf
                print('   * SPLITTING (run 2 of 2), recursion: %s' %
                      _recursionLevel)
                self.flush(quiet=quiet, _recursionLevel=_recursionLevel)
                self._tmpDict.clear()
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    raise
                print('WARNING: %s; unknown exception caught committing the data' % self.className)
                print('WARNING: to the database; report this as a bug, since')
                print('WARNING: many data (%d items) were lost: %s' %
                      (len(self._tmpDict), e))
        self._flushing = 0
        try:
            connectObject.commit()
        except:
            pass
        # Flush also deferred data.
        if self._deferredData:
            self._tmpDict = self._deferredData
            self.flush(quiet=1)
            self._deferredData = {}
        connectObject.commit()

    def populate(self):
        """Populate the dictionary from the database."""
        raise NotImplementedError

    def _toDB(self, quiet=0):
        """Write the dictionary to the database."""
        raise NotImplementedError

    def add(self, key, miscData=None):
        """Insert a new key and return its value."""
        c = next(self.counter)
        if miscData is not None:
            for d_name, data in miscData:
                getattr(self, d_name)[c] = data
        self[key] = c
        return c

    def addUnique(self, key, miscData=None):
        """Insert a new key and return its value; if the key is already
        in the dictionary, its previous  value is returned."""
        if key in self:
            return self[key]
        else:
            return self.add(key, miscData)


def fetchsome(curs, size=20000):
    """Yes, I've read the Python Cookbook! :-)"""
    while 1:
        res = curs.fetchmany(size)
        if not res:
            break
        for r in res:
            yield r


class MoviesCache(_BaseCache):

    """Manage the movies list."""
    className = 'MoviesCache'
    counter = counter()

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self.movieYear = {}
        self._table_name = tableName(Title)
        self._id_for_custom_q = 'MOVIES'
        self.sqlstr, self.converter = createSQLstr(Title, ('id', 'title',
                                                           'imdbIndex', 'kindID', 'productionYear',
                                                           'imdbID', 'phoneticCode', 'episodeOfID',
                                                           'seasonNr', 'episodeNr', 'seriesYears',
                                                           'md5sum'))

    def populate(self):
        print(' * POPULATING %s...' % self.className)
        titleTbl = tableName(Title)
        movieidCol = colName(Title, 'id')
        titleCol = colName(Title, 'title')
        kindidCol = colName(Title, 'kindID')
        yearCol = colName(Title, 'productionYear')
        imdbindexCol = colName(Title, 'imdbIndex')
        episodeofidCol = colName(Title, 'episodeOfID')
        seasonNrCol = colName(Title, 'seasonNr')
        episodeNrCol = colName(Title, 'episodeNr')
        sqlPop = 'SELECT %s, %s, %s, %s, %s, %s, %s, %s FROM %s;' % \
            (movieidCol, titleCol, kindidCol, yearCol, imdbindexCol,
                episodeofidCol, seasonNrCol, episodeNrCol, titleTbl)
        CURS.execute(sqlPop)
        _oldcacheValues = Title.sqlmeta.cacheValues
        Title.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            mdict = {'title': x[1], 'kind': KIND_STRS[x[2]],
                     'year': x[3], 'imdbIndex': x[4]}
            if mdict['imdbIndex'] is None:
                del mdict['imdbIndex']
            if mdict['year'] is None:
                del mdict['year']
            else:
                mdict['year'] = str(mdict['year'])
            episodeOfID = x[5]
            if episodeOfID is not None:
                s = Title.get(episodeOfID)
                series_d = {'title': s.title,
                            'kind': str(KIND_STRS[s.kindID]),
                            'year': s.productionYear, 'imdbIndex': s.imdbIndex}
                if series_d['imdbIndex'] is None:
                    del series_d['imdbIndex']
                if series_d['year'] is None:
                    del series_d['year']
                else:
                    series_d['year'] = str(series_d['year'])
                mdict['episode of'] = series_d
            title = build_title(mdict, ptdf=True)
            dict.__setitem__(self, title, x[0])
        self.counter = counter(Title.select().count() + 1)
        Title.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print(' * FLUSHING %s...' % self.className)
            sys.stdout.flush()
        l = []
        lapp = l.append
        for k, v in self._tmpDict.items():
            try:
                t = analyze_title(k)
            except IMDbParserError:
                if k and k.strip():
                    print('WARNING %s._toDB() invalid title:' % self.className, end=' ')
                    print(_(k))
                continue
            tget = t.get
            episodeOf = None
            kind = tget('kind')
            if kind == 'episode':
                # Series title.
                stitle = build_title(tget('episode of'), ptdf=True)
                episodeOf = self.addUnique(stitle)
                del t['episode of']
                year = self.movieYear.get(v)
                if year is not None and year != '????':
                    try:
                        t['year'] = int(year)
                    except ValueError:
                        pass
            elif kind in ('tv series', 'tv mini series'):
                t['series years'] = self.movieYear.get(v)
            title = tget('title')
            soundex = title_soundex(title)
            lapp((v, title, tget('imdbIndex'), KIND_IDS[kind],
                  tget('year'), None, soundex, episodeOf,
                  tget('season'), tget('episode'), tget('series years'),
                  md5(k.encode('latin1')).hexdigest()))
        self._runCommand(l)

    def _runCommand(self, dataList):
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(dataList))
        else:
            CSV_CURS.executemany(self.sqlstr, dataList)

    def addUnique(self, key, miscData=None):
        """Insert a new key and return its value; if the key is already
        in the dictionary, its previous  value is returned."""
        if key.endswith('{{SUSPENDED}}'):
            return None
        if key in self:
            return self[key]
        else:
            return self.add(key, miscData)


class PersonsCache(_BaseCache):

    """Manage the persons list."""
    className = 'PersonsCache'
    counter = counter()

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self.personGender = {}
        self._table_name = tableName(Name)
        self._id_for_custom_q = 'PERSONS'
        self.sqlstr, self.converter = createSQLstr(Name, ['id', 'name',
                                                          'imdbIndex', 'imdbID', 'gender', 'namePcodeCf',
                                                          'namePcodeNf', 'surnamePcode', 'md5sum'])

    def populate(self):
        print(' * POPULATING PersonsCache...')
        nameTbl = tableName(Name)
        personidCol = colName(Name, 'id')
        nameCol = colName(Name, 'name')
        imdbindexCol = colName(Name, 'imdbIndex')
        CURS.execute('SELECT %s, %s, %s FROM %s;' % (personidCol, nameCol,
                                                     imdbindexCol, nameTbl))
        _oldcacheValues = Name.sqlmeta.cacheValues
        Name.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            nd = {'name': x[1]}
            if x[2]:
                nd['imdbIndex'] = x[2]
            name = build_name(nd)
            dict.__setitem__(self, name, x[0])
        self.counter = counter(Name.select().count() + 1)
        Name.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print(' * FLUSHING PersonsCache...')
            sys.stdout.flush()
        l = []
        lapp = l.append
        for k, v in self._tmpDict.items():
            try:
                t = analyze_name(k)
            except IMDbParserError:
                if k and k.strip():
                    print('WARNING PersonsCache._toDB() invalid name:', _(k))
                continue
            tget = t.get
            name = tget('name')
            namePcodeCf, namePcodeNf, surnamePcode = name_soundexes(name)
            gender = self.personGender.get(v)
            lapp((v, name, tget('imdbIndex'), None, gender,
                  namePcodeCf, namePcodeNf, surnamePcode,
                  md5(k.encode('latin1')).hexdigest()))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class CharactersCache(_BaseCache):

    """Manage the characters list."""
    counter = counter()
    className = 'CharactersCache'

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self._table_name = tableName(CharName)
        self._id_for_custom_q = 'CHARACTERS'
        self.sqlstr, self.converter = createSQLstr(CharName, ['id', 'name',
                                                              'imdbIndex', 'imdbID', 'namePcodeNf',
                                                              'surnamePcode', 'md5sum'])

    def populate(self):
        print(' * POPULATING CharactersCache...')
        nameTbl = tableName(CharName)
        personidCol = colName(CharName, 'id')
        nameCol = colName(CharName, 'name')
        imdbindexCol = colName(CharName, 'imdbIndex')
        CURS.execute('SELECT %s, %s, %s FROM %s;' % (personidCol, nameCol,
                                                     imdbindexCol, nameTbl))
        _oldcacheValues = CharName.sqlmeta.cacheValues
        CharName.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            nd = {'name': x[1]}
            if x[2]:
                nd['imdbIndex'] = x[2]
            name = build_name(nd)
            dict.__setitem__(self, name, x[0])
        self.counter = counter(CharName.select().count() + 1)
        CharName.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print(' * FLUSHING CharactersCache...')
            sys.stdout.flush()
        l = []
        lapp = l.append
        for k, v in self._tmpDict.items():
            try:
                t = analyze_name(k)
            except IMDbParserError:
                if k and k.strip():
                    print('WARNING CharactersCache._toDB() invalid name:', _(k))
                continue
            tget = t.get
            name = tget('name')
            namePcodeCf, namePcodeNf, surnamePcode = name_soundexes(name,
                                                                    character=True)
            lapp((v, name, tget('imdbIndex'), None,
                  namePcodeCf, surnamePcode, md5(k.encode('latin1')).hexdigest()))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class CompaniesCache(_BaseCache):

    """Manage the companies list."""
    counter = counter()
    className = 'CompaniesCache'

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self._table_name = tableName(CompanyName)
        self._id_for_custom_q = 'COMPANIES'
        self.sqlstr, self.converter = createSQLstr(CompanyName, ['id', 'name',
                                                                 'countryCode', 'imdbID', 'namePcodeNf',
                                                                 'namePcodeSf', 'md5sum'])

    def populate(self):
        print(' * POPULATING CharactersCache...')
        nameTbl = tableName(CompanyName)
        companyidCol = colName(CompanyName, 'id')
        nameCol = colName(CompanyName, 'name')
        countryCodeCol = colName(CompanyName, 'countryCode')
        CURS.execute('SELECT %s, %s, %s FROM %s;' % (companyidCol, nameCol,
                                                     countryCodeCol, nameTbl))
        _oldcacheValues = CompanyName.sqlmeta.cacheValues
        CompanyName.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            nd = {'name': x[1]}
            if x[2]:
                nd['country'] = x[2]
            name = build_company_name(nd)
            dict.__setitem__(self, name, x[0])
        self.counter = counter(CompanyName.select().count() + 1)
        CompanyName.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print(' * FLUSHING CompaniesCache...')
            sys.stdout.flush()
        l = []
        lapp = l.append
        for k, v in self._tmpDict.items():
            try:
                t = analyze_company_name(k)
            except IMDbParserError:
                if k and k.strip():
                    print('WARNING CompaniesCache._toDB() invalid name:', _(k))
                continue
            tget = t.get
            name = tget('name')
            namePcodeNf = soundex(name)
            namePcodeSf = None
            country = tget('country')
            if k != name:
                namePcodeSf = soundex(k)
            lapp((v, name, country, None, namePcodeNf, namePcodeSf,
                  md5(k.encode('latin1')).hexdigest()))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class KeywordsCache(_BaseCache):

    """Manage the list of keywords."""
    counter = counter()
    className = 'KeywordsCache'

    def __init__(self, *args, **kwds):
        _BaseCache.__init__(self, *args, **kwds)
        self._table_name = tableName(CompanyName)
        self._id_for_custom_q = 'KEYWORDS'
        self.flushEvery = 10000
        self.sqlstr, self.converter = createSQLstr(Keyword, ['id', 'keyword',
                                                             'phoneticCode'])

    def populate(self):
        print(' * POPULATING KeywordsCache...')
        nameTbl = tableName(CompanyName)
        keywordidCol = colName(Keyword, 'id')
        keyCol = colName(Keyword, 'name')
        CURS.execute('SELECT %s, %s FROM %s;' % (keywordidCol, keyCol,
                                                 nameTbl))
        _oldcacheValues = Keyword.sqlmeta.cacheValues
        Keyword.sqlmeta.cacheValues = False
        for x in fetchsome(CURS, self.flushEvery):
            dict.__setitem__(self, x[1], x[0])
        self.counter = counter(Keyword.select().count() + 1)
        Keyword.sqlmeta.cacheValues = _oldcacheValues

    def _toDB(self, quiet=0):
        if not quiet:
            print(' * FLUSHING KeywordsCache...')
            sys.stdout.flush()
        l = []
        lapp = l.append
        for k, v in self._tmpDict.items():
            keySoundex = soundex(k)
            lapp((v, k, keySoundex))
        if not CSV_DIR:
            CURS.executemany(self.sqlstr, self.converter(l))
        else:
            CSV_CURS.executemany(self.sqlstr, l)


class SQLData(dict):

    """Variable set of information, to be stored from time to time
    to the SQL database."""

    def __init__(self, table=None, cols=None, sqlString='', converter=None,
                 d={}, flushEvery=20000, counterInit=1):
        if not sqlString:
            if not (table and cols):
                raise TypeError('"table" or "cols" unspecified')
            sqlString, converter = createSQLstr(table, cols)
        elif converter is None:
            raise TypeError('"sqlString" or "converter" unspecified')
        dict.__init__(self)
        self.counterInit = counterInit
        self.counter = counterInit
        self.flushEvery = flushEvery
        self.sqlString = sqlString
        self.converter = converter
        self._recursionLevel = 1
        self._table = table
        self._table_name = tableName(table)
        for k, v in list(d.items()):
            self[k] = v

    def __setitem__(self, key, value):
        """The value is discarded, the counter is used as the 'real' key
        and the user's 'key' is used as its values."""
        counter = self.counter
        if counter % self.flushEvery == 0:
            self.flush()
        dict.__setitem__(self, counter, key)
        self.counter += 1

    def add(self, key):
        self[key] = None

    def flush(self, _resetRecursion=1):
        if not self:
            return
        # XXX: it's safer to flush MoviesCache and PersonsCache, to preserve consistency
        CACHE_MID.flush(quiet=1)
        CACHE_PID.flush(quiet=1)
        if _resetRecursion:
            self._recursionLevel = 1
        if self._recursionLevel >= MAX_RECURSION:
            print('WARNING recursion level exceded trying to flush data')
            print('WARNING this batch of data is lost.')
            self.clear()
            self.counter = self.counterInit
            return
        keys = {'table': self._table_name}
        _after_has_run = False
        try:
            executeCustomQueries('BEFORE_SQLDATA_TODB', _keys=keys,
                                 _timeit=False)
            self._toDB()
            executeCustomQueries('AFTER_SQLDATA_TODB', _keys=keys,
                                 _timeit=False)
            _after_has_run = True
            self.clear()
            self.counter = self.counterInit
        except OperationalError as e:
            if not _after_has_run:
                executeCustomQueries('AFTER_SQLDATA_TODB', _keys=keys,
                                     _timeit=False)
            print(' * TOO MANY DATA (%s items), SPLITTING (run #%d)...' %
                  (len(self), self._recursionLevel))
            self._recursionLevel += 1
            newdata = self.__class__(table=self._table,
                                     sqlString=self.sqlString,
                                     converter=self.converter)
            newdata._recursionLevel = self._recursionLevel
            newflushEvery = self.flushEvery // 2
            if newflushEvery < 1:
                print('WARNING recursion level exceded trying to flush data')
                print('WARNING this batch of data is lost.')
                self.clear()
                self.counter = self.counterInit
                return
            self.flushEvery = newflushEvery
            newdata.flushEvery = newflushEvery
            popitem = self.popitem
            dsi = dict.__setitem__
            for x in range(len(self) // 2):
                k, v = popitem()
                dsi(newdata, k, v)
            newdata.flush(_resetRecursion=0)
            del newdata
            self.flush(_resetRecursion=0)
            self.clear()
            self.counter = self.counterInit
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            print('WARNING: SQLData; unknown exception caught committing the data')
            print('WARNING: to the database; report this as a bug, since')
            print('WARNING: many data (%d items) were lost: %s' %
                  (len(self), e))
        connectObject.commit()

    def _toDB(self):
        print(' * FLUSHING SQLData...')
        if not CSV_DIR:
            CURS.executemany(self.sqlString, self.converter(list(self.values())))
        else:
            CSV_CURS.executemany(self.sqlString, list(self.values()))


# Miscellaneous functions.

def unpack(line, headers, sep='\t'):
    """Given a line, split at seps and return a dictionary with key
    from the header list.
    E.g.:
        line = '      0000000124    8805   8.4  Incredibles, The (2004)'
        header = ('votes distribution', 'votes', 'rating', 'title')
        seps=('  ',)

    will returns: {'votes distribution': '0000000124', 'votes': '8805',
                    'rating': '8.4', 'title': 'Incredibles, The (2004)'}
    """
    r = {}
    ls1 = [_f for _f in line.split(sep) if _f]
    for index, item in enumerate(ls1):
        try:
            name = headers[index]
        except IndexError:
            name = 'item%s' % index
        r[name] = item.strip()
    return r


def _parseMinusList(fdata):
    """Parse a list of lines starting with '- '."""
    rlist = []
    tmplist = []
    for line in fdata:
        if line and line[:2] == '- ':
            if tmplist:
                rlist.append(' '.join(tmplist))
            l = line[2:].strip()
            if l:
                tmplist[:] = [l]
            else:
                tmplist[:] = []
        else:
            l = line.strip()
            if l:
                tmplist.append(l)
    if tmplist:
        rlist.append(' '.join(tmplist))
    return rlist


def _parseColonList(lines, replaceKeys):
    """Parser for lists with "TAG: value" strings."""
    out = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cols = line.split(':', 1)
        if len(cols) < 2:
            continue
        k = cols[0]
        k = replaceKeys.get(k, k)
        v = ' '.join(cols[1:]).strip()
        if k not in out:
            out[k] = []
        out[k].append(v)
    return out


# Functions used to manage data files.

def readMovieList():
    """Read the movies.list.gz file."""
    try:
        mdbf = SourceFile(MOVIES, start=MOVIES_START, stop=MOVIES_STOP)
    except IOError:
        return
    count = 0
    for line in mdbf:
        line_d = unpack(line, ('title', 'year'))
        title = line_d['title']
        yearData = None
        # Collect 'year' column for tv "series years" and episodes' year.
        if title[0] == '"':
            yearData = [('movieYear', line_d['year'])]
        mid = CACHE_MID.addUnique(title, yearData)
        if mid is None:
            continue
        if count % 10000 == 0:
            print('SCANNING movies:', _(title), end=' ')
            print('(movieID: %s)' % mid)
        count += 1
    CACHE_MID.flush()
    CACHE_MID.movieYear.clear()
    mdbf.close()


def doCast(fp, roleid, rolename):
    """Populate the cast table."""
    pid = None
    count = 0
    name = ''
    roleidVal = RawValue('roleID', roleid)
    sqldata = SQLData(table=CastInfo, cols=['personID', 'movieID',
                                            'personRoleID', 'note', 'nrOrder', roleidVal])
    if rolename == 'miscellaneous crew':
        sqldata.flushEvery = 10000
    for line in fp:
        if line and line[0] != '\t':
            if line[0] == '\n':
                continue
            sl = [_f for _f in line.split('\t') if _f]
            if len(sl) != 2:
                continue
            name, line = sl
            miscData = None
            if rolename == 'actor':
                miscData = [('personGender', 'm')]
            elif rolename == 'actress':
                miscData = [('personGender', 'f')]
            pid = CACHE_PID.addUnique(name.strip(), miscData)
        line = line.strip()
        ll = line.split('  ')
        title = ll[0]
        note = None
        role = None
        order = None
        for item in ll[1:]:
            if not item:
                continue
            if item[0] == '[':
                # Quite inefficient, but there are some very strange
                # cases of garbage in the plain text data files to handle...
                role = item[1:]
                if role[-1:] == ']':
                    role = role[:-1]
                if role[-1:] == ')':
                    nidx = role.find('(')
                    if nidx != -1:
                        note = role[nidx:]
                        role = role[:nidx].rstrip()
                        if not role:
                            role = None
            elif item[0] == '(':
                if note is None:
                    note = item
                else:
                    note = '%s %s' % (note, item)
            elif item[0] == '<':
                textor = item[1:-1]
                try:
                    order = int(textor)
                except ValueError:
                    os = textor.split(',')
                    if len(os) == 3:
                        try:
                            order = ((int(os[2]) - 1) * 1000) + \
                                    ((int(os[1]) - 1) * 100) + (int(os[0]) - 1)
                        except ValueError:
                            pass
        movieid = CACHE_MID.addUnique(title)
        if movieid is None:
            continue
        if role is not None:
            roles = [_f for _f in [x.strip() for x in role.split('/')] if _f]
            for role in roles:
                cid = CACHE_CID.addUnique(role)
                sqldata.add((pid, movieid, cid, note, order))
        else:
            sqldata.add((pid, movieid, None, note, order))
        if count % 10000 == 0:
            print('SCANNING %s:' % rolename, end=' ')
            print(_(name))
        count += 1
    sqldata.flush()
    CACHE_PID.flush()
    CACHE_PID.personGender.clear()
    CACHE_CID.flush()
    print('CLOSING %s...' % rolename)


def castLists():
    """Read files listed in the 'role' column of the 'roletypes' table."""
    rt = [(x.id, x.role) for x in RoleType.select()]
    for roleid, rolename in rt:
        if rolename == 'guest':
            continue
        fname = rolename
        fname = fname.replace(' ', '-')
        if fname == 'actress':
            fname = 'actresses.list.gz'
        elif fname == 'miscellaneous-crew':
            fname = 'miscellaneous.list.gz'
        else:
            fname = fname + 's.list.gz'
        print('DOING', fname)
        try:
            f = SourceFile(fname, start=CAST_START, stop=CAST_STOP)
        except IOError:
            if rolename == 'actress':
                CACHE_CID.flush()
                if not CSV_DIR:
                    CACHE_CID.clear()
            continue
        doCast(f, roleid, rolename)
        f.close()
        if rolename == 'actress':
            CACHE_CID.flush()
            if not CSV_DIR:
                CACHE_CID.clear()
        t('castLists(%s)' % rolename)


def doAkaNames():
    """People's akas."""
    pid = None
    count = 0
    try:
        fp = SourceFile('aka-names.list.gz', start=AKAN_START)
    except IOError:
        return
    sqldata = SQLData(table=AkaName, cols=['personID', 'name', 'imdbIndex',
                                           'namePcodeCf', 'namePcodeNf', 'surnamePcode',
                                           'md5sum'])
    for line in fp:
        if line and line[0] != ' ':
            if line[0] == '\n':
                continue
            pid = CACHE_PID.addUnique(line.strip())
        else:
            line = line.strip()
            if line[:5] == '(aka ':
                line = line[5:]
            if line[-1:] == ')':
                line = line[:-1]
            try:
                name_dict = analyze_name(line)
            except IMDbParserError:
                if line:
                    print('WARNING doAkaNames wrong name:', _(line))
                continue
            name = name_dict.get('name')
            namePcodeCf, namePcodeNf, surnamePcode = name_soundexes(name)
            sqldata.add((pid, name, name_dict.get('imdbIndex'),
                        namePcodeCf, namePcodeNf, surnamePcode,
                        md5(line.encode('latin1')).hexdigest()))
            if count % 10000 == 0:
                print('SCANNING akanames:', _(line))
            count += 1
    sqldata.flush()
    fp.close()


class AkasMoviesCache(MoviesCache):

    """A MoviesCache-like class used to populate the AkaTitle table."""
    className = 'AkasMoviesCache'
    counter = counter()

    def __init__(self, *args, **kdws):
        MoviesCache.__init__(self, *args, **kdws)
        self.flushEvery = 50000
        self._mapsIDsToTitles = True
        self.notes = {}
        self.ids = {}
        self._table_name = tableName(AkaTitle)
        self._id_for_custom_q = 'AKAMOVIES'
        self.sqlstr, self.converter = createSQLstr(AkaTitle, ('id', 'movieID',
                   