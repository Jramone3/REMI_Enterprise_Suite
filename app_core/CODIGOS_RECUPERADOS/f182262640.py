#!/usr/bin/env python3
# Copyright 2012 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""A tool that generates FS API calls to generate a filesystem, and packages the files
to work with that.

This is called by emcc. You can also call it yourself.

You can split your files into "asset bundles", and create each bundle separately
with this tool. Then just include the generated js for each and they will load
the data and prepare it accordingly. This allows you to share assets and reduce
data downloads.

 * If you run this yourself, separately/standalone from emcc, then the main program
   compiled by emcc must be built with filesystem support. You can do that with
   -sFORCE_FILESYSTEM (if you forget that, an unoptimized build or one with
   ASSERTIONS enabled will show an error suggesting you use that flag).

Usage:

  file_packager TARGET [--preload A [B..]] [--embed C [D..]] [--exclude E [F..]]] [--js-output=OUTPUT.js] [--no-force] [--use-preload-cache] [--indexedDB-name=EM_PRELOAD_CACHE] [--separate-metadata] [--lz4] [--use-preload-plugins] [--no-node]

  --preload  ,
  --embed    See emcc --help for more details on those options.

  --exclude E [F..] Specifies filename pattern matches to use for excluding given files from being added to the package.
                    See https://docs.python.org/2/library/fnmatch.html for syntax.

  --from-emcc Indicate that `file_packager` was called from `emcc` and will be further processed by it, so some code generation can be skipped here

  --js-output=FILE Writes output in FILE, if not specified, standard output is used.

  --obj-output=FILE create an object file from embedded files, for direct linking into a wasm binary.

  --depfile=FILE Writes a dependency list containing the list of directories and files walked, compatible with Make, Ninja, CMake, etc.

  --wasm64 When used with `--obj-output` create a wasm64 object file

  --export-name=EXPORT_NAME Use custom export name (default is `Module`)

  --no-force Don't create output if no valid input file is specified.

  --use-preload-cache Stores package in IndexedDB so that subsequent loads don't need to do XHR. Checks package version.

  --indexedDB-name Use specified IndexedDB database name (Default: 'EM_PRELOAD_CACHE')

  --separate-metadata Stores package metadata separately. Only applicable when preloading and js-output file is specified.

  --lz4 Uses LZ4. This compresses the data using LZ4 when this utility is run, then the client decompresses chunks on the fly, avoiding storing
        the entire decompressed data in memory at once. See LZ4 in src/settings.js, you must build the main program with that flag.

  --use-preload-plugins Tells the file packager to run preload plugins on the files as they are loaded. This performs tasks like decoding images
                        and audio using the browser's codecs.

  --no-node Whether to support Node.js. By default we do, which emits some extra code.

  --quiet Suppress reminder about using `FORCE_FILESYSTEM`

Notes:

  * The file packager generates unix-style file paths. So if you are on windows and a file is accessed at
    subdir\file, in JS it will be subdir/file. For simplicity we treat the web platform as a *NIX.
"""

import base64
import ctypes
import fnmatch
import hashlib
import json
import os
import posixpath
import random
import shutil
import sys
from subprocess import PIPE
from textwrap import dedent
from typing import List

__scriptdir__ = os.path.dirname(os.path.abspath(__file__))
__rootdir__ = os.path.dirname(__scriptdir__)
sys.path.insert(0, __rootdir__)

from tools import shared, utils, js_manipulation


DEBUG = os.environ.get('EMCC_DEBUG')

IMAGE_SUFFIXES = ('.jpg', '.png', '.bmp')
AUDIO_SUFFIXES = ('.ogg', '.wav', '.mp3')
AUDIO_MIMETYPES = {'ogg': 'audio/ogg', 'wav': 'audio/wav', 'mp3': 'audio/mpeg'}

DDS_HEADER_SIZE = 128

# Set to 1 to randomize file order and add some padding,
# to work around silly av false positives
AV_WORKAROUND = 0

excluded_patterns: List[str] = []
new_data_files = []
walked = []


class Options:
  def __init__(self):
    self.export_name = 'Module'
    self.has_preloaded = False
    self.has_embedded = False
    self.jsoutput = None
    self.obj_output = None
    self.depfile = None
    self.from_emcc = False
    self.quiet = False
    self.force = True
    # If set to True, IndexedDB (IDBFS in library_idbfs.js) is used to locally
    # cache VFS XHR so that subsequent page loads can read the data from the
    # offline cache instead.
    self.use_preload_cache = False
    self.indexeddb_name = 'EM_PRELOAD_CACHE'
    # If set to True, the package metadata is stored separately from js-output
    # file which makes js-output file immutable to the package content changes.
    # If set to False, the package metadata is stored inside the js-output file
    # which makes js-output file to mutate on each invocation of this packager tool.
    self.separate_metadata = False
    self.lz4 = False
    self.use_preload_plugins = False
    self.support_node = True
    self.wasm64 = False


class DataFile:
  def __init__(self, srcpath, dstpath, mode, explicit_dst_path):
    self.srcpath = srcpath
    self.dstpath = dstpath
    self.mode = mode
    self.explicit_dst_path = explicit_dst_path


options = Options()


def err(*args):
  print(*args, file=sys.stderr)


def base64_encode(b):
  b64 = base64.b64encode(b)
  return b64.decode('ascii')


def has_hidden_attribute(filepath):
  """Win32 code to test whether the given file has the hidden property set."""

  if sys.platform != 'win32':
    return False

  try:
    attrs = ctypes.windll.kernel32.GetFileAttributesW(
        u'%s' % filepath)
    assert attrs != -1
    result = bool(attrs & 2)
  except Exception:
    result = False
  return result


def should_ignore(fullname):
  """The packager should never preload/embed files if the file
  is hidden (Win32) or it matches any pattern specified in --exclude"""
  if has_hidden_attribute(fullname):
    return True

  for p in excluded_patterns:
    if fnmatch.fnmatch(fullname, p):
      return True
  return False


def add(mode, rootpathsrc, rootpathdst):
  """Expand directories into individual files

  rootpathsrc: The path name of the root directory on the local FS we are
               adding to emscripten virtual FS.
  rootpathdst: The name we want to make the source path available on the
               emscripten virtual FS.
  """
  walked.append(rootpathsrc)
  for dirpath, dirnames, filenames in os.walk(rootpathsrc):
    new_dirnames = []
    for name in dirnames:
      fullname = os.path.join(dirpath, name)
      if not should_ignore(fullname):
        walked.append(fullname)
        new_dirnames.append(name)
      elif DEBUG:
        err('Skipping directory "%s" from inclusion in the emscripten '
            'virtual file system.' % fullname)
    for name in filenames:
      fullname = os.path.join(dirpath, name)
      if not should_ignore(fullname):
        walked.append(fullname)
        # Convert source filename relative to root directory of target FS.
        dstpath = os.path.join(rootpathdst,
                               os.path.relpath(fullname, rootpathsrc))
        new_data_files.append(DataFile(srcpath=fullname, dstpath=dstpath,
                                       mode=mode, explicit_dst_path=True))
      elif DEBUG:
        err('Skipping file "%s" from inclusion in the emscripten '
            'virtual file system.' % fullname)
    dirnames.clear()
    dirnames.extend(new_dirnames)


def to_asm_string(string):
  """Convert a python string to string suitable for including in an
  assembly file using the `.asciz` directive.

  The result will be an UTF-8 encoded string in the data section.
  """
  # See MCAsmStreamer::PrintQuotedString in llvm/lib/MC/MCAsmStreamer.cpp
  # And isPrint in llvm/include/llvm/ADT/StringExtras.h

  def is_print(c):
    return c >= 0x20 and c <= 0x7E

  def escape(c):
    if is_print(c):
      return chr(c)
    escape_chars = {
      '\b': '\\b',
      '\f': '\\f',
      '\n': '\\n',
      '\r': '\\r',
      '\t': '\\t',
    }
    if c in escape_chars:
      return escape_chars[c]
    # Enscode all other chars are three octal digits(!)
    return '\\%s%s%s' % (oct(c >> 6), oct(c >> 3), oct(c >> 0))

  return ''.join(escape(c) for c in string.encode('utf-8'))


def to_c_symbol(filename, used):
  """Convert a filename (python string) to a legal C symbols, avoiding collisions."""
  def escape(c):
     if c.isalnum():
       return c
     else:
       return '_'
  c_symbol = ''.join(escape(c) for c in filename)
  # Handle collisions
  if c_symbol in used:
    counter = 2
    while c_symbol + str(counter) in used:
      counter = counter + 1
    c_symbol = c_symbol + str(counter)
  used.add(c_symbol)
  return c_symbol


def generate_object_file(data_files):
  embed_files = [f for f in data_files if f.mode == 'embed']
  assert embed_files

  asm_file = shared.replace_suffix(options.obj_output, '.s')

  used = set()
  for f in embed_files:
    f.c_symbol_name = '__em_file_data_%s' % to_c_symbol(f.dstpath, used)

  with open(asm_file, 'w') as out:
    out.write('# Emscripten embedded file data, generated by tools/file_packager.py\n')

    for f in embed_files:
      if DEBUG:
        err('embedding %s at %s' % (f.srcpath, f.dstpath))

      size = os.path.getsize(f.srcpath)
      dstpath = to_asm_string(f.dstpath)
      srcpath = utils.normalize_path(f.srcpath)
      out.write(dedent(f'''
      .section .rodata.{f.c_symbol_name},"",@

      # The name of file
      {f.c_symbol_name}_name:
      .asciz "{dstpath}"
      .size {f.c_symbol_name}_name, {len(dstpath)+1}

      # The size of the file followed by the content itself
      {f.c_symbol_name}:
      .incbin "{srcpath}"
      .size {f.c_symbol_name}, {size}
      '''))

    if options.wasm64:
      align = 3
      ptr_type = 'i64'
      bits = 64
    else:
      align = 2
      ptr_type = 'i32'
      bits = 32
    out.write(dedent(f'''
      .functype _emscripten_fs_load_embedded_files ({ptr_type}) -> ()
      .section .text,"",@
      init_file_data:
        .functype init_file_data () -> ()
        global.get __emscripten_embedded_file_data@GOT
        call _emscripten_fs_load_embedded_files
        end_function

      # Run init_file_data on startup.
      # See system/lib/README.md for ordering of system constructors.
      .section .init_array.49,"",@
      .p2align {align}
      .int{bits} init_file_data

      # A list of triples of:
      # (file_name_ptr, file_data_size, file_data_ptr)
      # The list in null terminate with a single 0
      .globl __emscripten_embedded_file_data
      .export_name __emscripten_embedded_file_data, __emscripten_embedded_file_data
      .section .rodata.__emscripten_embedded_file_data,"",@
      __emscripten_embedded_file_data:
      .p2align {align}
      '''))

    for f in embed_files:
      # The `.dc.a` directive gives us a pointer (address) sized entry.
      # See https://sourceware.org/binutils/docs/as/Dc.html
      out.write(dedent(f'''\
        .p2align %s
        .dc.a {f.c_symbol_name}_name
        .p2align %s
        .int32 {os.path.getsize(f.srcpath)}
        .p2align %s
        .dc.a {f.c_symbol_name}
        ''' % (align, align, align)))

    ptr_size = 4
    elem_size = (2 * ptr_size) + 4
    total_size = len(embed_files) * elem_size + 4
    out.write(dedent(f'''\
      .dc.a 0
      .size __emscripten_embedded_file_data, {total_size}
      '''))
  cmd = [shared.EMCC, '-c', asm_file, '-o', options.obj_output]
  if options.wasm64:
    target = 'wasm64-unknown-emscripten'
    cmd.append('-Wno-experimental')
  else:
    target = 'wasm32-unknown-emscripten'
  cmd.append('--target=' + target)
  shared.check_call(cmd)


def main():
  if len(sys.argv) == 1:
    err('''Usage: file_packager TARGET [--preload A [B..]] [--embed C [D..]] [--exclude E [F..]]] [--js-output=OUTPUT.js] [--no-force] [--use-preload-cache] [--indexedDB-name=EM_PRELOAD_CACHE] [--separate-metadata] [--lz4] [--use-preload-plugins]
  See the source for more details.''')
    return 1

  data_target = sys.argv[1]
  data_files = []
  plugins = []
  leading = ''

  for arg in sys.argv[2:]:
    if arg == '--preload':
      leading = 'preload'
    elif arg == '--embed':
      leading = 'embed'
    elif arg == '--exclude':
      leading = 'exclude'
    elif arg == '--no-force':
      options.force = False
      leading = ''
    elif arg == '--use-preload-cache':
      options.use_preload_cache = True
      leading = ''
    elif arg.startswith('--indexedDB-name'):
      options.indexeddb_name = arg.split('=', 1)[1] if '=' in arg else None
      leading = ''
    elif arg == '--no-heap-copy':
      err('ignoring legacy flag --no-heap-copy (that is the only mode supported now)')
      leading = ''
    elif arg == '--separate-metadata':
      options.separate_metadata = True
      leading = ''
    elif arg == '--lz4':
      options.lz4 = True
      leading = ''
    elif arg == '--use-preload-plugins':
      options.use_preload_plugins = True
      leading = ''
    elif arg == '--no-node':
      options.support_node = False
      leading = ''
    elif arg.startswith('--js-output'):
      options.jsoutput = arg.split('=', 1)[1] if '=' in arg else None
      leading = ''
    elif arg.startswith('--obj-output'):
      options.obj_output = arg.split('=', 1)[1] if '=' in arg else None
      leading = ''
    elif arg.startswith('--depfile'):
      options.depfile = arg.split('=', 1)[1] if '=' in arg else None
      leading = ''
    elif arg == '--wasm64':
      options.wasm64 = True
    elif arg.startswith('--export-name'):
      if '=' in arg:
        options.export_name = arg.split('=', 1)[1]
      leading = ''
    elif arg == '--from-emcc':
      options.from_emcc = True
      leading = ''
    elif arg == '--quiet':
      options.quiet = True
    elif arg.startswith('--plugin'):
      plugin = utils.read_file(arg.split('=', 1)[1])
      eval(plugin) # should append itself to plugins
      leading = ''
    elif leading == 'preload' or leading == 'embed':
      mode = leading
      # position of @ if we're doing 'src@dst'. '__' is used to keep the index
      # same with the original if they escaped with '@@'.
      at_position = arg.replace('@@', '__').find('@')
      # '@@' in input string means there is an actual @ character, a single '@'
      # means the 'src@dst' notation.
      uses_at_notation = (at_position != -1)

      if uses_at_notation:
        srcpath = arg[0:at_position].replace('@@', '@') # split around the @
        dstpath = arg[at_position + 1:].replace('@@', '@')
      else:
        # Use source path as destination path.
        srcpath = dstpath = arg.replace('@@', '@')
      if os.path.isfile(srcpath) or os.path.isdir(srcpath):
        data_files.append(DataFile(srcpath=srcpath, dstpath=dstpath, mode=mode,
                                   explicit_dst_path=uses_at_notation))
      else:
        err('error: ' + arg + ' does not exist')
        return 1
    elif leading == 'exclude':
      excluded_patterns.append(arg)
    else:
      err('Unknown parameter:', arg)
      return 1

  options.has_preloaded = any(f.mode == 'preload' for f in data_files)
  options.has_embedded = any(f.mode == 'embed' for f in data_files)

  if options.separate_metadata:
    if not options.has_preloaded or not options.jsoutput:
      err('cannot separate-metadata without both --preloaded files '
          'and a specified --js-output')
      return 1

  if not options.from_emcc and not options.quiet:
    err('Remember to build the main file with `-sFORCE_FILESYSTEM` '
        'so that it includes support for loading this file package')

  if options.jsoutput and os.path.abspath(options.jsoutput) == os.path.abspath(data_target):
    err('error: TARGET should not be the same value of --js-output')
    return 1

  walked.append(__file__)
  for file_ in data_files:
    if not should_ignore(file_.srcpath):
      if os.path.isdir(file_.srcpath):
        add(file_.mode, file_.srcpath, file_.dstpath)
      else:
        walked.append(file_.srcpath)
        new_data_files.append(file_)
  data_files = [file_ for file_ in new_data_files
                if not os.path.isdir(file_.srcpath)]
  if len(data_files) == 0:
    err('Nothing to do!')
    sys.exit(1)

  # Absolutize paths, and check that they make sense
  # os.getcwd() always returns the hard path with any symbolic links resolved,
  # even if we cd'd into a symbolic link.
  curr_abspath = os.path.abspath(os.getcwd())

  for file_ in data_files:
    if not file_.explicit_dst_path:
      # This file was not defined with src@dst, so we inferred the destination
      # from the source. In that case, we require that the destination be
      # within the current working directory.
      path = file_.dstpath
      # Use os.path.realpath to resolve any symbolic links to hard paths,
      # to match the structure in curr_abspath.
      abspath = os.path.realpath(os.path.abspath(path))
      if DEBUG:
        err(path, abspath, curr_abspath)
      if not abspath.startswith(curr_abspath):
        err('Error: Embedding "%s" which is not contained within the current directory '
            '"%s".  This is invalid since the current directory becomes the '
            'root that the generated code will see.  To include files outside of the current '
            'working directoty you can use the `--preload-file srcpath@dstpath` syntax to '
            'explicitly specify the target location.' % (path, curr_abspath))
        sys.exit(1)
      file_.dstpath = abspath[len(curr_abspath) + 1:]
      if os.path.isabs(path):
        err('Warning: Embedding an absolute file/directory name "%s" to the '
            'virtual filesystem. The file will be made available in the '
            'relative path "%s". You can use the `--preload-file srcpath@dstpath` '
            'syntax to explicitly specify the target location the absolute source '
            'path should be directed to.' % (path, file_.dstpath))

  for file_ in data_files:
    # name in the filesystem, native and emulated
    file_.dstpath = utils.normalize_path(file_.dstpath)
    # If user has submitted a directory name as the destination but omitted
    # the destination filename, use the filename from source file
    if file_.dstpath.endswith('/'):
      file_.dstpath = file_.dstpath + os.path.basename(file_.srcpath)
    # make destination path always relative to the root
    file_.dstpath = posixpath.normpath(os.path.join('/', file_.dstpath))
    if DEBUG:
      err('Packaging file "%s" to VFS in path "%s".' % (file_.srcpath,  file_.dstpath))

  # Remove duplicates (can occur naively, for example preload dir/, preload dir/subdir/)
  seen = set()

  def was_seen(name):
    if name in seen:
      return True
    seen.add(name)
    return False

  # The files are sorted by the dstpath to make the order of files reproducible
  # across file systems / operating systems (os.walk does not produce the same
  # file order on different file systems / operating systems)
  data_files = sorted(data_files, key=lambda file_: file_.dstpath)
  data_files = [file_ for file_ in data_files if not was_seen(file_.dstpath)]

  if AV_WORKAROUND:
    random.shuffle(data_files)

  # Apply plugins
  for file_ in data_files:
    for plugin in plugins:
      plugin(file_)

  metadata = {'files': []}

  if options.obj_output:
    if not options.has_embedded:
      err('--obj-output is only applicable when embedding files')
      return 1
    generate_object_file(data_files)
    if not options.has_preloaded:
      return 0

  ret = generate_js(data_target, data_files, metadata)

  if options.force or len(data_files):
    if options.jsoutput is None:
      print(ret)
    else:
      # Overwrite the old jsoutput file (if exists) only when its content
      # differs from the current generated one, otherwise leave the file
      # untouched preserving its old timestamp
      if os.path.isfile(options.jsoutput):
        old = utils.read_file(options.jsoutput)
        if old != ret:
          utils.write_file(options.jsoutput, ret)
      else:
        utils.write_file(options.jsoutput, ret)
      if options.separate_metadata:
        utils.write_file(options.jsoutput + '.metadata', json.dumps(metadata, separators=(',', ':')))

  if options.depfile:
    with open(options.depfile, 'w') as f:
      for target in [data_target, options.jsoutput]:
        if target:
          f.write(escape_for_makefile(target))
          f.write(' \\\n')
      f.write(': \\\n')
      for dependency in walked:
        f.write(escape_for_makefile(dependency))
        f.write(' \\\n')

  return 0


def escape_for_makefile(fpath):
  # Escapes for CMake's "pathname" grammar as described here:
  #   https://cmake.org/cmake/help/latest/command/add_custom_command.html#grammar-token-depfile-pathname
  # Which is congruent with how Ninja and GNU Make expect characters escaped.
  fpath = utils.normalize_path(fpath)
  return fpath.replace('$', '$$').replace('#', '\\#').replace(' ', '\\ ')


def generate_js(data_target, data_files, metadata):
  # emcc will add this to the output itself, so it is only needed for
  # standalone calls
  if options.from_emcc:
    ret = ''
  else:
    ret = '''
  var Module = typeof %(EXPORT_NAME)s !== 'undefined' ? %(EXPORT_NAME)s : {};\n''' % {"EXPORT_NAME": options.export_name}

  ret += '''
  if (!Module.expectedDataFileDownloads) {
    Module.expectedDataFileDownloads = 0;
  }

  Module.expectedDataFileDownloads++;
  (function() {
    // Do not attempt to redownload the virtual filesystem data when in a pthread or a Wasm Worker context.
    if (Module['ENVIRONMENT_IS_PTHREAD'] || Module['$ww']) return;
    var loadPackage = function(metadata) {\n'''

  code = '''
      function assert(check, msg) {
        if (!check) throw msg + new Error().stack;
      }\n'''

  # Set up folders
  partial_dirs = []
  for file_ in data_files:
    dirname = os.path.dirname(file_.dstpath)
    dirname = dirname.lstrip('/') # absolute paths start with '/', remove that
    if dirname != '':
      parts = dirname.split('/')
      for i in range(len(parts)):
        partial = '/'.join(parts[:i + 1])
        if partial not in partial_dirs:
          code += ('''Module['FS_createPath'](%s, %s, true, true);\n'''
                   % (json.dumps('/' + '/'.join(parts[:i])), json.dumps(parts[i])))
          partial_dirs.append(partial)

  if options.has_preloaded:
    # Bundle all datafiles into one archive. Avoids doing lots of simultaneous
    # XHRs which has overhead.
    start = 0
    with open(data_target, 'wb') as data:
      for file_ in data_files:
        file_.data_start = start
        curr = utils.read_binary(file_.srcpath)
        file_.data_end = start + len(curr)
        if AV_WORKAROUND:
            curr += '\x00'
        start += len(curr)
        data.write(curr)

    if start > 256 * 1024 * 1024:
      err('warning: file packager is creating an asset bundle of %d MB. '
          'this is very large, and browsers might have trouble loading it. '
          'see https://hacks.mozilla.org/2015/02/synchronous-execution-and-filesystem-access-in-emscripten/'
          % (start / (1024 * 1024)))

    create_preloaded = '''
          Module['FS_createPreloadedFile'](this.name, null, byteArray, true, true, function() {
            Module['removeRunDependency'](`fp ${that.name}`);
          }, function() {
            err(`Preloading file ${that.name} failed`);
          }, false, true); // canOwn this data in the filesystem, it is a slide into the heap that will never change\n'''
    create_data = '''// canOwn this data in the filesystem, it is a slide into the heap that will never change
          Module['FS_createDataFile'](this.name, null, byteArray, true, true, true);
          Module['removeRunDependency'](`fp ${that.name}`);'''

    if not options.lz4:
      # Data requests - for getting a block of data out of the big archive - have
      # a similar API to XHRs
      code += '''
      /** @constructor */
      function DataRequest(start, end, audio) {
        this.start = start;
        this.end = end;
        this.audio = audio;
      }
      DataRequest.prototype = {
        requests: {},
        open: function(mode, name) {
          this.name = name;
          this.requests[name] = this;
          Module['addRunDependency'](`fp ${this.name}`);
        },
        send: function() {},
        onload: function() {
          var byteArray = this.byteArray.subarray(this.start, this.end);
          this.finish(byteArray);
        },
        finish: function(byteArray) {
          var that = this;
          %s
          this.requests[this.name] = null;
        }
      };

      var files = metadata['files'];
      for (var i = 0; i < files.length; ++i) {
        new DataRequest(files[i]['start'], files[i]['end'], files[i]['audio'] || 0).open('GET', files[i]['filename']);
      }\n''' % (create_preloaded if options.use_preload_plugins else create_data)

  if options.has_embedded and not options.obj_output:
    err('--obj-output is recommended when using --embed.  This outputs an object file for linking directly into your application is more effecient than JS encoding')

  for counter, file_ in enumerate(data_files):
    filename = file_.dstpath
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    if file_.mode == 'embed':
      if not options.obj_output:
        # Embed (only needed when not generating object file output)
        data = base64_encode(utils.read_binary(file_.srcpath))
        code += "      var fileData%d = '%s';\n" % (counter, data)
        # canOwn this data in the filesystem (i.e. there is no need to create a copy in the FS layer).
        code += ("      Module['FS_createDataFile']('%s', '%s', atob(fileData%d), true, true, true);\n"
                 % (dirname, basename, counter))
    elif file_.mode == 'preload':
      # Preload
      metadata_el = {
        'filename': file_.dstpath,
        'start': file_.data_start,
        'end': file_.data_end,
      }
      if filename[-4:] in AUDIO_SUFFIXES:
        metadata_el['audio'] = 1

      metadata['files'].append(metadata_el)
    else:
      assert 0

  if options.has_preloaded:
    if not options.lz4:
      # Get the big archive and split it up
      use_data = '''// Reuse the bytearray from the XHR as the source for file reads.
          DataRequest.prototype.byteArray = byteArray;
          var files = metadata['files'];
          for (var i = 0; i < files.length; ++i) {
            DataRequest.prototype.requests[files[i].filename].onload();
          }'''
      use_data += ("          Module['removeRunDependency']('datafile_%s');\n"
                   % js_manipulation.escape_for_js_string(data_target))

    else:
      # LZ4FS usage
      temp = data_target + '.orig'
      shutil.move(data_target, temp)
      meta = shared.run_js_tool(utils.path_from_root('tools/lz4-compress.mjs'),
                                [temp, data_target], stdout=PIPE)
      os.unlink(temp)
      use_data = '''var compressedData = %s;
            compressedData['data'] = byteArray;
            assert(typeof Module['LZ4'] === 'object', 'LZ4 not present - was your app build with -sLZ4?');
            Module['LZ4'].loadPackage({ 'metadata': metadata, 'compressedData': compressedData }, %s);
            Module['removeRunDependency']('datafile_%s');''' % (meta, "true" if options.use_preload_plugins else "false", js_manipulation.escape_for_js_string(data_target))

    package_name = data_target
    remote_package_size = os.path.getsize(package_name)
    remote_package_name = os.path.basename(package_name)
    ret += '''
      var PACKAGE_PATH = '';
      if (typeof window === 'object') {
        PACKAGE_PATH = window['encodeURIComponent'](window.location.pathname.toString().substring(0, window.location.pathname.toString().lastIndexOf('/')) + '/');
      } else if (typeof process === 'undefined' && typeof location !== 'undefined') {
        // web worker
        PACKAGE_PATH = encodeURIComponent(location.pathname.toString().substring(0, location.pathname.toString().lastIndexOf('/')) + '/');
      }
      var PACKAGE_NAME = '%s';
      var REMOTE_PACKAGE_BASE = '%s';
      if (typeof Module['locateFilePackage'] === 'function' && !Module['locateFile']) {
        Module['locateFile'] = Module['locateFilePackage'];
        err('warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)');
      }
      var REMOTE_PACKAGE_NAME = Module['locateFile'] ? Module['locateFile'](REMOTE_PACKAGE_BASE, '') : REMOTE_PACKAGE_BASE;\n''' % (js_manipulation.escape_for_js_string(data_target), js_manipulation.escape_for_js_string(remote_package_name))
    metadata['remote_package_size'] = remote_package_size
    ret += '''var REMOTE_PACKAGE_SIZE = metadata['remote_package_size'];\n'''

    if options.use_preload_cache:
      # Set the id to a hash of the preloaded data, so that caches survive over multiple builds
      # if the data has not changed.
      data = utils.read_binary(data_target)
      package_uuid = 'sha256-' + hashlib.sha256(data).hexdigest()
      metadata['package_uuid'] = str(package_uuid)

      code += r'''
        var PACKAGE_UUID = metadata['package_uuid'];
        var indexedDB;
        if (typeof window === 'object') {
          indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
        } else if (typeof location !== 'undefined') {
          // worker
          indexedDB = self.indexedDB;
        } else {
          throw 'using IndexedDB to cache data can only be done on a web page or in a web worker';
        }
        var IDB_RO = "readonly";
        var IDB_RW = "readwrite";
        var DB_NAME = "''' + options.indexeddb_name + '''";
        var DB_VERSION = 1;
        var METADATA_STORE_NAME = 'METADATA';
        var PACKAGE_STORE_NAME = 'PACKAGES';
        function openDatabase(callback, errback) {
          try {
            var openRequest = indexedDB.open(DB_NAME, DB_VERSION);
          } catch (e) {
            return errback(e);
          }
          openRequest.onupgradeneeded = function(event) {
            var db = /** @type {IDBDatabase} */ (event.target.result);

            if (db.objectStoreNames.contains(PACKAGE_STORE_NAME)) {
              db.deleteObjectStore(PACKAGE_STORE_NAME);
            }
            var packages = db.createObjectStore(PACKAGE_STORE_NAME);

            if (db.objectStoreNames.contains(METADATA_STORE_NAME)) {
              db.deleteObjectStore(METADATA_STORE_NAME);
            }
            var metadata = db.createObjectStore(METADATA_STORE_NAME);
          };
          openRequest.onsuccess = function(event) {
            var db = /** @type {IDBDatabase} */ (event.target.result);
            callback(db);
          };
          openRequest.onerror = function(error) {
            errback(error);
          };
        };

        // This is needed as chromium has a limit on per-entry files in IndexedDB
        // https://cs.chromium.org/chromium/src/content/renderer/indexed_db/webidbdatabase_impl.cc?type=cs&sq=package:chromium&g=0&l=177
        // https://cs.chromium.org/chromium/src/out/Debug/gen/third_party/blink/public/mojom/indexeddb/indexeddb.mojom.h?type=cs&sq=package:chromium&g=0&l=60
        // We set the chunk size to 64MB to stay well-below the limit
        var CHUNK_SIZE = 64 * 1024 * 1024;

        function cacheRemotePackage(
          db,
          packageName,
          packageData,
          packageMeta,
          callback,
          errback
        ) {
          var transactionPackages = db.transaction([PACKAGE_STORE_NAME], IDB_RW);
          var packages = transactionPackages.objectStore(PACKAGE_STORE_NAME);
          var chunkSliceStart = 0;
          var nextChunkSliceStart = 0;
          var chunkCount = Math.ceil(packageData.byteLength / CHUNK_SIZE);
          var finishedChunks = 0;
          for (var chunkId = 0; chunkId < chunkCount; chunkId++) {
            nextChunkSliceStart += CHUNK_SIZE;
            var putPackageRequest = packages.put(
              packageData.slice(chunkSliceStart, nextChunkSliceStart),
              `package/${packageName}/${chunkId}`
            );
            chunkSliceStart = nextChunkSliceStart;
            putPackageRequest.onsuccess = function(event) {
              finishedChunks++;
              if (finishedChunks == chunkCount) {
                var transaction_metadata = db.transaction(
                  [METADATA_STORE_NAME],
                  IDB_RW
                );
                var metadata = transaction_metadata.objectStore(METADATA_STORE_NAME);
                var putMetadataRequest = metadata.put(
                  {
                    'uuid': packageMeta.uuid,
                    'chunkCount': chunkCount
                  },
                  `metadata/${packageName}`
                );
                putMetadataRequest.onsuccess = function(event) {
                  callback(packageData);
                };
                putMetadataRequest.onerror = function(error) {
                  errback(error);
                };
              }
            };
            putPackageRequest.onerror = function(error) {
              errback(error);
            };
          }
        }

        /* Check if there's a cached package, and if so whether it's the latest available */
        function checkCachedPackage(db, packageName, callback, errback) {
          var transaction = db.transaction([METADATA_STORE_NAME], IDB_RO);
          var metadata = transaction.objectStore(METADATA_STORE_NAME);
          var getRequest = metadata.get(`metadata/${packageName}`);
          getRequest.onsuccess = function(event) {
            var result = event.target.result;
            if (!result) {
              return callback(false, null);
            } else {
              return callback(PACKAGE_UUID === result['uuid'], result);
            }
          };
          getRequest.onerror = function(error) {
            errback(error);
          };
        }

        function fetchCachedPackage(db, packageName, metadata, callback, errback) {
          var transaction = db.transaction([PACKAGE_STORE_NAME], IDB_RO);
          var packages = transaction.objectStore(PACKAGE_STORE_NAME);

          var chunksDone = 0;
          var totalSize = 0;
          var chunkCount = metadata['chunkCount'];
          var chunks = new Array(chunkCount);

          for (var chunkId = 0; chunkId < chunkCount; chunkId++) {
            var getRequest = packages.get(`package/${packageName}/${chunkId}`);
            getRequest.onsuccess = function(event) {
              if (!event.target.result) {
                errback(new Error(`CachedPackageNotFound for: ${packageName}`));
                return;
              }
              // If there's only 1 chunk, there's nothing to concatenate it with so we can just return it now
              if (chunkCount == 1) {
                callback(event.target.result);
              } else {
                chunksDone++;
                totalSize += event.target.result.byteLength;
                chunks.push(event.target.result);
                if (chunksDone == chunkCount) {
                  if (chunksDone == 1) {
                    callback(event.target.result);
                  } else {
                    var tempTyped = new Uint8Array(totalSize);
                    var byteOffset = 0;
                    for (var chunkId in chunks) {
                      var buffer = chunks[chunkId];
                      tempTyped.set(new Uint8Array(buffer), byteOffset);
                      byteOffset += buffer.byteLength;
                      buffer = undefined;
                    }
                    chunks = undefined;
                    callback(tempTyped.buffer);
                    tempTyped = undefined;
                  }
                }
              }
            };
            getRequest.onerror = function(error) {
              errback(error);
            };
          }
        }\n'''

    # add Node.js support code, if necessary
    node_support_code = ''
    if options.support_node:
      node_support_code = '''
        if (typeof process === 'object' && typeof process.versions === 'object' && typeof process.versions.node === 'string') {
          require('fs').readFile(packageName, function(err, contents) {
            if (err) {
              errback(err);
            } else {
              callback(contents.buffer);
            }
          });
          return;
        }'''.strip()
    ret += '''
      function fetchRemotePackage(packageName, packageSize, callback, errback) {
        %(node_support_code)s
        var xhr = new XMLHttpRequest();
        xhr.open('GET', packageName, true);
        xhr.responseType = 'arraybuffer';
        xhr.onprogress = function(event) {
          var url = packageName;
          var size = packageSize;
          if (event.total) size = event.total;
          if (event.loaded) {
            if (!xhr.addedTotal) {
              xhr.addedTotal = true;
              if (!Module.dataFileDownloads) Module.dataFileDownloads = {};
              Module.dataFileDownloads[url] = {
                loaded: event.loaded,
                total: size
              };
            } else {
              Module.dataFileDownloads[url].loaded = event.loaded;
            }
            var total = 0;
            var loaded = 0;
            var num = 0;
            for (var download in Module.dataFileDownloads) {
            var data = Module.dataFileDownloads[download];
              total += data.total;
              loaded += data.loaded;
              num++;
            }
            total = Math.ceil(total * Module.expectedDataFileDownloads/num);
            if (Module['setStatus']) Module['setStatus'](`Downloading data... (${loaded}/${total})`);
          } else if (!Module.dataFileDownloads) {
            if (Module['setStatus']) Module['setStatus']('Downloading data...');
          }
        };
        xhr.onerror = function(event) {
          throw new Error("NetworkError for: " + packageName);
        }
        xhr.onload = function(event) {
          if (xhr.status == 200 || xhr.status == 304 || xhr.status == 206 || (xhr.status == 0 && xhr.response)) { // file URLs can return 0
            var packageData = xhr.response;
            callback(packageData);
          } else {
            throw new Error(xhr.statusText + " : " + xhr.responseURL);
          }
        };
        xhr.send(null);
      };

      function handleError(error) {
        console.error('package error:', error);
      };\n''' % {'node_support_code': node_support_code}

    code += '''
      function processPackageData(arrayBuffer) {
        assert(arrayBuffer, 'Loading data file failed.');
        assert(arrayBuffer.constructor.name === ArrayBuffer.name, 'bad input to processPackageData');
        var byteArray = new Uint8Array(arrayBuffer);
        var curr;
        %s
      };
      Module['addRunDependency']('datafile_%s');\n''' % (use_data, js_manipulation.escape_for_js_string(data_target))
    # use basename because from the browser's point of view,
    # we need to find the datafile in the same dir as the html file

    code += '''
      if (!Module.preloadResults) Module.preloadResults = {};\n'''

    if options.use_preload_cache:
      code += '''
        function preloadFallback(error) {
          console.error(error);
          console.error('falling back to default preload behavior');
          fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE, processPackageData, handleError);
        };

        openDatabase(
          function(db) {
            checkCachedPackage(db, PACKAGE_PATH + PACKAGE_NAME,
              function(useCached, metadata) {
                Module.preloadResults[PACKAGE_NAME] = {fromCache: useCached};
                if (useCached) {
                  fetchCachedPackage(db, PACKAGE_PATH + PACKAGE_NAME, metadata, processPackageData, preloadFallback);
                } else {
                  fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE,
                    function(packageData) {
                      cacheRemotePackage(db, PACKAGE_PATH + PACKAGE_NAME, packageData, {uuid:PACKAGE_UUID}, processPackageData,
                        function(error) {
                          console.error(error);
                          processPackageData(packageData);
                        });
                    }
                  , preloadFallback);
                }
              }
            , preloadFallback);
          }
        , preloadFallback);

        if (Module['setStatus']) Module['setStatus']('Downloading...');\n'''
    else:
      # Not using preload cache, so we might as well start the xhr ASAP,
      # potentially before JS parsing of the main codebase if it's after us.
      # Only tricky bit is the fetch is async, but also when runWithFS is called
      # is async, so we handle both orderings.
      ret += '''
      var fetchedCallback = null;
      var fetched = Module['getPreloadedPackage'] ? Module['getPreloadedPackage'](REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE) : null;

      if (!fetched) fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE, function(data) {
        if (fetchedCallback) {
          fetchedCallback(data);
          fetchedCallback = null;
        } else {
          fetched = data;
        }
      }, handleError);\n'''

      code += '''
      Module.preloadResults[PACKAGE_NAME] = {fromCache: false};
      if (fetched) {
        processPackageData(fetched);
        fetched = null;
      } else {
        fetchedCallback = processPackageData;
      }\n'''

  ret += '''
    function runWithFS() {\n'''
  ret += code
  ret += '''
    }
    if (Module['calledRun']) {
      runWithFS();
    } else {
      if (!Module['preRun']) Module['preRun'] = [];
      Module["preRun"].push(runWithFS); // FS is not initialized yet, wait for it
    }\n'''

  if options.separate_metadata:
      _metadata_template = '''
    Module['removeRunDependency']('%(metadata_file)s');
  }

  function runMetaWithFS() {
    Module['addRunDependency']('%(metadata_file)s');
    var REMOTE_METADATA_NAME = Module['locateFile'] ? Module['locateFile']('%(metadata_file)s', '') : '%(metadata_file)s';
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
     if (xhr.readyState === 4 && xhr.status === 200) {
       loadPackage(JSON.parse(xhr.responseText));
     }
    }
    xhr.open('GET', REMOTE_METADATA_NAME, true);
    xhr.overrideMimeType('application/json');
    xhr.send(null);
  }

  if (Module['calledRun']) {
    runMetaWithFS();
  } else {
    if (!Module['preRun']) Module['preRun'] = [];
    Module["preRun"].push(runMetaWithFS);
  }\n''' % {'metadata_file': os.path.basename(options.jsoutput + '.metadata')}

  else:
      _metadata_template = '''
    }
    loadPackage(%s);\n''' % json.dumps(metadata)

  ret += '''%s
  })();\n''' % _metadata_template

  return ret


if __name__ == '__main__':
  sys.exit(main())

# SIG # Begin Windows Authenticode signature block
# MIIoQQYJKoZIhvcNAQcCoIIoMjCCKC4CAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCA3kB7w47Wd9S5a
# Tz0RGhzsCXJK5Ytgv7IVjwwzHfqKfqCCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGgwwghoIAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEIG7JFa5gL5X2/Wa7A6Yoed9aKe1URnXesl0C6Y0LNwAMMEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEAnaRBevkwQMzz2qf6TnqghDQVw1tA
# 4BYCg37TKl5+vlAwr3q0m0FALqGjilHTFSAwVw009AyooXKzz/ihSipg6lvYCFxJ
# Rk8XLB+O0UiIdDvw1Qu9tSJGps/Q/l3GitbipxfCNCN2kHWog/fn/974/+i+FP8E
# V1Z8My8th2XKeupN7wfjFyaeXBUwh8muM8Jmecmcq+WhXqsQmkJMNvzxb/bqY1KI
# caG55do88Rov8rnfpgoXBCtalxgDfOU3ynu41rdd9SU593H2KJ6MyPq/kGq59NgJ
# N2IExDnS7c4CKzBKhfgK7B0sVELG0MyCkyxClGnSvisJQQGikkkyLjvxj6GCF5Yw
# gheSBgorBgEEAYI3AwMBMYIXgjCCF34GCSqGSIb3DQEHAqCCF28wghdrAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCC3SulaHp9cn5E3RTl+G305Gjz9
# 6JWhIEDC3DB4Ee25VQIGaPB/5/P8GBMyMDI1MTAxNjE2MTcyNC40NzVaMASAAgH0
# oIHRpIHOMIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUw
# IwYDVQQLExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5u
# U2hpZWxkIFRTUyBFU046MzcwMy0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29m
# dCBUaW1lLVN0YW1wIFNlcnZpY2WgghHsMIIHIDCCBQigAwIBAgITMwAAAgpHshTZ
# 7rKzDwABAAACCjANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDAeFw0yNTAxMzAxOTQyNTdaFw0yNjA0MjIxOTQyNTdaMIHLMQswCQYD
# VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
# MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3Nv
# ZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046
# MzcwMy0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
# cnZpY2UwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCy7NzwEpb7BpwA
# k9LJ00Xq30TcTjcwNZ80TxAtAbhSaJ2kwnJA1Au/Do9/fEBjAHv6Mmtt3fmPDeIJ
# nQ7VBeIq8RcfjcjrbPIg3wA5v5MQflPNSBNOvcXRP+fZnAy0ELDzfnJHnCkZNsQU
# Z7GF7LxULTKOYY2YJw4TrmcHohkY6DjCZyxhqmGQwwdbjoPWRbYu/ozFem/yfJPy
# jVBql1068bcVh58A8c5CD6TWN/L3u+Ny+7O8+Dver6qBT44Ey7pfPZMZ1Hi7yvCL
# v5LGzSB6o2OD5GIZy7z4kh8UYHdzjn9Wx+QZ2233SJQKtZhpI7uHf3oMTg0zanQf
# z7mgudefmGBrQEg1ox3n+3Tizh0D9zVmNQP9sFjsPQtNGZ9ID9H8A+kFInx4mrSx
# A2SyGMOQcxlGM30ktIKM3iqCuFEU9CHVMpN94/1fl4T6PonJ+/oWJqFlatYuMKv2
# Z8uiprnFcAxCpOsDIVBO9K1vHeAMiQQUlcE9CD536I1YLnmO2qHagPPmXhdOGrHU
# nCUtop21elukHh75q/5zH+OnNekp5udpjQNZCviYAZdHsLnkU0NfUAr6r1UqDcSq
# 1yf5RiwimB8SjsdmHll4gPjmqVi0/rmnM1oAEQm3PyWcTQQibYLiuKN7Y4io5bJT
# Vwm+vRRbpJ5UL/D33C//7qnHbeoWBQIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFAKv
# F0EEj4AyPfY8W/qrsAvftZwkMB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1
# GelyMF8GA1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
# a2lvcHMvY3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEp
# LmNybDBsBggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWlj
# cm9zb2Z0LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUy
# MFBDQSUyMDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYI
# KwYBBQUHAwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQCwk3PW
# 0CyjOaqXCMOusTde7ep2CwP/xV1J3o9KAiKSdq8a2UR5RCHYhnJseemweMUH2kNe
# fpnAh2Bn8H2opDztDJkj8OYRd/KQysE12NwaY3KOwAW8Rg8OdXv5fUZIsOWgprkC
# QM0VoFHdXYExkJN3EzBbUCUw3yb4gAFPK56T+6cPpI8MJLJCQXHNMgti2QZhX9Kk
# fRAffFYMFcpsbI+oziC5Brrk3361cJFHhgEJR0J42nqZTGSgUpDGHSZARGqNcAV5
# h+OQDLeF2p3URx/P6McUg1nJ2gMPYBsD+bwd9B0c/XIZ9Mt3ujlELPpkijjCdSZx
# hzu2M3SZWJr57uY+FC+LspvIOH1Opofanh3JGDosNcAEu9yUMWKsEBMngD6VWQSQ
# YZ6X9F80zCoeZwTq0i9AujnYzzx5W2fEgZejRu6K1GCASmztNlYJlACjqafWRofT
# qkJhV/J2v97X3ruDvfpuOuQoUtVAwXrDsG2NOBuvVso5KdW54hBSsz/4+ORB4qLn
# q4/GNtajUHorKRKHGOgFo8DKaXG+UNANwhGNxHbILSa59PxExMgCjBRP3828yGKs
# quSEzzLNWnz5af9ZmeH4809fwIttI41JkuiY9X6hmMmLYv8OY34vvOK+zyxkS+9B
# ULVAP6gt+yaHaBlrln8Gi4/dBr2y6Srr/56g0DCCB3EwggVZoAMCAQICEzMAAAAV
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
# BRDBcQZqELQdVTNYs6FwZvKhggNPMIICNwIBATCB+aGB0aSBzjCByzELMAkGA1UE
# BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAc
# BgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjElMCMGA1UECxMcTWljcm9zb2Z0
# IEFtZXJpY2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOjM3
# MDMtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2
# aWNloiMKAQEwBwYFKw4DAhoDFQDRAMVJlA6bKq93Vnu3UkJgm5HlYaCBgzCBgKR+
# MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMT
# HU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA
# 7Jr+WzAiGA8yMDI1MTAxNjA1MTcxNVoYDzIwMjUxMDE3MDUxNzE1WjB2MDwGCisG
# AQQBhFkKBAExLjAsMAoCBQDsmv5bAgEAMAkCAQACASUCAf8wBwIBAAICEhgwCgIF
# AOycT9sCAQAwNgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAKMAgCAQAC
# AwehIKEKMAgCAQACAwGGoDANBgkqhkiG9w0BAQsFAAOCAQEAN2hW3EMbFFb6CbNn
# YvqlnFlI2zq3mj6RzJzccCrwn6IyLISaiIRp0+lmbDFaheCxfLY0AG3E4vKMBoaA
# 41bYWdMwvvgf6BiGS7iYYgyJZ9xedLQMfHh9aH2n4xXyYGLrYh0d3AG72iYw5Q6M
# tOj/VTmKU3fUkHpAs9SUQz8t+SRfmLPPnDaVPXfdlOqa8hj0TbjvMDi7vlyg6b1g
# ZCBOsDY/stmd674ER1t8BJ0CbEvSwcfvuRb7LCocVUzLoz+n33DLtEpKzlgZkzRt
# 2srudcYFQwNjC7tZVsRlqTwjj8O9c/PioTOcWclQP7NmgOQCJMDynAWS46XaTTYK
# lazf8DGCBA0wggQJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNo
# aW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29y
# cG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEw
# AhMzAAACCkeyFNnusrMPAAEAAAIKMA0GCWCGSAFlAwQCAQUAoIIBSjAaBgkqhkiG
# 9w0BCQMxDQYLKoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIMht7/dSnvQVOTFs
# 3M3+0pdmiY6hMmG5dQt3bRNu3AGAMIH6BgsqhkiG9w0BCRACLzGB6jCB5zCB5DCB
# vQQgTZrL/LR6kr9fdnTcpNyWioTy70hdG107sx7HSHD35JowgZgwgYCkfjB8MQsw
# CQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9u
# ZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNy
# b3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAgpHshTZ7rKzDwABAAACCjAi
# BCCwGwEpPLVYXcixd6yKdFlssTQA717vtINoUBgUZXmUdDANBgkqhkiG9w0BAQsF
# AASCAgCEiCJB1c2hic1pEA71tuzcwRJwcSQ8723mJqQcwnbrLMOscibbfF5T90fJ
# Jx7p1jz9Ny4OFfBmMp1XN9IQ6ZFRsR6T5g1h06Ntjji+QVi0tLpBgSAhs8XChVS2
# Do8W5GgKlgLf8rRjC9azq0VqTUV+CaLiokN1FT/ev/c1qEhObYtrusizy0y0fMsV
# B4ILC/VBvwL9LruO3KVc7OKJIZyGu9AgNfIobA7s8n4sVqDRiDVrs/ZdtjgvXix8
# i2BTT16mtcApMmvnF30HiQsVcQifhKuKvtNBNIlmHq0rfJk4mfYjm+F1aabCYDOi
# odLdS/3dgoMTP/eO0HDa8ptFo05oJc+Dq1NiMsRlQpF0Xh7wy69JU60R4Z3AAid7
# NDDVJiFgQr+jeDQQ+HK2xvb9F7zz5/QzZXJF+kJ6sgLtrV8sgN1h1sQp18Ckf5+D
# SEwjO58WojxFgbykIzLmnzUc+HD3uGmQkPVSkwMwcfU1aSUnB7YrtvtH38auNAoV
# Vx/Fe1bKVJfEltWSPP6DF9zKfg4hbC/HZYwBXGiVbWk/O2RGymsoifZco2DfqF7d
# ShMaK1L8RPgTkIf8uK/OVuAncHYHJAJut3ejNFy6oXWWaFHytynAl8sGjOBx72ov
# gfz5FBuHRIFRfpC+87ZA04T/6RohzPfAM5obc+KV5XiX4zYQFw==
# SIG # End Windows Authenticode signature block