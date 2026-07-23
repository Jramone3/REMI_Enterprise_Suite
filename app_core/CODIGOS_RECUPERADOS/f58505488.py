#!/usr/bin/env python3

# compressor.py
from subprocess import Popen, PIPE

def compress(value):
    """Compresses a byte array with the xz binary"""

    process = Popen(["xz", "--compress", "--force"], stdin=PIPE, stdout=PIPE)
    return process.communicate(value)[0]

def decompress(value):
    """Decompresses a byte array with the xz binary"""

    process = Popen(["xz", "--decompress", "--stdout", "--force"],
                    stdin=PIPE, stdout=PIPE)
    return process.communicate(value)[0]

def compress_file(path):
    """Compress the file at 'path' with the xz binary"""

    process = Popen(["xz", "--compress", "--force", "--stdout", path], stdout=PIPE)
    return process.communicate()[0]

# compressor.py

import os
import sys
from optparse import OptionParser
from sys import argv
import base64
import json
from io import BytesIO

from os.path import basename
from errno import EPIPE
import lzma

def load():
    ppds_compressed = base64.b64decode(ppds_compressed_b64)
    ppds_decompressed = decompress(ppds_compressed)
    ppds = json.loads(ppds_decompressed.decode(encoding='ASCII'))
    return ppds

def ls():
    binary_name = basename(argv[0])
    ppds = load()
    for key, value in ppds.items():
        if key == 'ARCHIVE': continue
        for ppd in value[2]:
            try:
                print(ppd.replace('"', '"' + binary_name + ':', 1))
            except IOError as e:
                # Errors like broken pipes (program which takes the standard
                # output terminates before this program terminates) should not
                # generate a traceback.
                if e.errno == EPIPE: exit(0)
                raise

def cat(ppd):
    # Ignore driver's name, take only PPD's
    ppd = ppd.split(":")[-1]
    # Remove also the index
    ppd = "0/" + ppd[ppd.find("/")+1:]

    # Object for streaming decompression
    decompressor = lzma.LZMADecompressor()
    # size for one decompression i.e. ~20MB
    size = 20000000

    ppds = load()
    ppds['ARCHIVE'] = base64.b64decode(ppds['ARCHIVE'].encode('ASCII'))
    ppdtext=bytearray()

    if ppd in ppds:
        start = ppds[ppd][0]
        length = ppds[ppd][1]

        text = BytesIO(decompressor.decompress(ppds['ARCHIVE'],size))
        for i in range(int(start/size)):
            text = BytesIO(decompressor.decompress(ppds['ARCHIVE'],size))
        text.seek(start%size)

        if((size-(start%size)) < length):
            ppdtext.extend(text.read())
            length = length - (size-(start%size))
            text = BytesIO(decompressor.decompress(ppds['ARCHIVE'],size))
            while(size < length):
                ppdtext.extend(text.read())
                length = length - size
                text = BytesIO(decompressor.decompress(ppds['ARCHIVE'],size))
            ppdtext.extend(text.read(length))
        else:
            ppdtext.extend(text.read(length))
        
        return ppdtext

def main():
    usage = "usage: %prog list\n" \
            "       %prog cat URI"
    version = "%prog 1.1.0\n" \
              "Copyright (c) 2013 Vitor Baptista.\n" \
              "This is free software; see the source for copying conditions.\n" \
              "There is NO warranty; not even for MERCHANTABILITY or\n" \
              "FITNESS FOR A PARTICULAR PURPOSE."
    parser = OptionParser(usage=usage,
                          version=version)
    (options, args) = parser.parse_args()

    if len(args) == 0 or len(args) > 2:
        parser.error("incorrect number of arguments")

    if args[0].lower() == 'list':
        ls()
    elif args[0].lower() == 'cat':
        if not len(args) == 2:
            parser.error("incorrect number of arguments")
        ppd = cat(args[1])
        if not ppd:
            parser.error("Printer '%s' does not have default driver!" % args[1])
        try:
            # avoid any assumption of encoding or system locale; just print the
            # bytes of the PPD as they are
            if sys.version_info.major < 3:
                sys.stdout.write(ppd)
            else:
                sys.stdout.buffer.write(ppd)
        except IOError as e:
            # Errors like broken pipes (program which takes the standard output
            # terminates before this program terminates) should not generate a
            # traceback.
            if e.errno == EPIPE: exit(0)
            raise
    else:
        parser.error("argument " + args[0] + " invalid")

# PPDs Archive
ppds_compressed_b64 = b"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"

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # We don't want a KeyboardInterrupt throwing a
        # traceback into stdout.
        pass
