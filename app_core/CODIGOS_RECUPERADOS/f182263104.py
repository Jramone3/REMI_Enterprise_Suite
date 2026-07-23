# Copyright 2014 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""WebIDL binder

https://emscripten.org/docs/porting/connecting_cpp_and_javascript/WebIDL-Binder.html
"""

import argparse
import os
import sys
from typing import List

__scriptdir__ = os.path.dirname(os.path.abspath(__file__))
__rootdir__ = os.path.dirname(__scriptdir__)
sys.path.insert(0, __rootdir__)

from tools import utils

sys.path.append(utils.path_from_root('third_party'))
sys.path.append(utils.path_from_root('third_party/ply'))

import WebIDL

# CHECKS='FAST' will skip most argument type checks in the wrapper methods for
#                  performance (~3x faster than default).
# CHECKS='ALL' will do extensive argument type checking (~5x slower than default).
#                 This will catch invalid numbers, invalid pointers, invalid strings, etc.
# Anything else defaults to legacy mode for backward compatibility.
CHECKS = os.environ.get('IDL_CHECKS', 'DEFAULT')
# DEBUG=1 will print debug info in render_function
DEBUG = os.environ.get('IDL_VERBOSE') == '1'


def dbg(*args):
  if DEBUG:
    print(*args, file=sys.stderr)


dbg(f'Debug print ON, CHECKS=${CHECKS}')

# We need to avoid some closure errors on the constructors we define here.
CONSTRUCTOR_CLOSURE_SUPPRESSIONS = '/** @suppress {undefinedVars, duplicate} @this{Object} */'


class Dummy:
  def __init__(self, type):
    self.type = type

  def __repr__(self):
    return f'<Dummy type:{self.type}>'

  def getExtendedAttribute(self, _name):
    return None


parser = argparse.ArgumentParser()
parser.add_argument('--wasm64', action='store_true', default=False,
                    help='Build for wasm64')
parser.add_argument('infile')
parser.add_argument('outfile')
options = parser.parse_args()

input_file = options.infile
output_base = options.outfile
cpp_output = output_base + '.cpp'
js_output = output_base + '.js'

utils.delete_file(cpp_output)
utils.delete_file(js_output)

p = WebIDL.Parser()
p.parse('''
interface VoidPtr {
};
''' + utils.read_file(input_file))
data = p.finish()

interfaces = {}
implements = {}
enums = {}

for thing in data:
  if isinstance(thing, WebIDL.IDLInterface):
    interfaces[thing.identifier.name] = thing
  elif isinstance(thing, WebIDL.IDLImplementsStatement):
    implements.setdefault(thing.implementor.identifier.name, []).append(thing.implementee.identifier.name)
  elif isinstance(thing, WebIDL.IDLEnum):
    enums[thing.identifier.name] = thing

# print interfaces
# print implements

pre_c = ['''
#include <emscripten.h>
#include <stdlib.h>

EM_JS_DEPS(webidl_binder, "$intArrayFromString,$UTF8ToString,$alignMemory");
''']

mid_c = ['''
extern "C" {

// Define custom allocator functions that we can force export using
// EMSCRIPTEN_KEEPALIVE.  This avoids all webidl users having to add
// malloc/free to -sEXPORTED_FUNCTIONS.
EMSCRIPTEN_KEEPALIVE void webidl_free(void* p) { free(p); }
EMSCRIPTEN_KEEPALIVE void* webidl_malloc(size_t len) { return malloc(len); }

''']


def build_constructor(name):
  implementing_name = implements[name][0] if implements.get(name) else 'WrapperObject'
  return [r'''{name}.prototype = Object.create({implementing}.prototype);
{name}.prototype.constructor = {name};
{name}.prototype.__class__ = {name};
{name}.__cache__ = {{}};
Module['{name}'] = {name};
'''.format(name=name, implementing=implementing_name)]


mid_js = ['''
// Bindings utilities

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function WrapperObject() {
}
''']

mid_js += build_constructor('WrapperObject')

mid_js += ['''
/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant)
    @param {*=} __class__ */
function getCache(__class__) {
  return (__class__ || WrapperObject).__cache__;
}
Module['getCache'] = getCache;

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant)
    @param {*=} __class__ */
function wrapPointer(ptr, __class__) {
  var cache = getCache(__class__);
  var ret = cache[ptr];
  if (ret) return ret;
  ret = Object.create((__class__ || WrapperObject).prototype);
  ret.ptr = ptr;
  return cache[ptr] = ret;
}
Module['wrapPointer'] = wrapPointer;

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function castObject(obj, __class__) {
  return wrapPointer(obj.ptr, __class__);
}
Module['castObject'] = castObject;

Module['NULL'] = wrapPointer(0);

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function destroy(obj) {
  if (!obj['__destroy__']) throw 'Error: Cannot destroy object. (Did you create it yourself?)';
  obj['__destroy__']();
  // Remove from cache, so the object can be GC'd and refs added onto it released
  delete getCache(obj.__class__)[obj.ptr];
}
Module['destroy'] = destroy;

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function compare(obj1, obj2) {
  return obj1.ptr === obj2.ptr;
}
Module['compare'] = compare;

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function getPointer(obj) {
  return obj.ptr;
}
Module['getPointer'] = getPointer;

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function getClass(obj) {
  return obj.__class__;
}
Module['getClass'] = getClass;

// Converts big (string or array) values into a C-style storage, in temporary space

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
var ensureCache = {
  buffer: 0,  // the main buffer of temporary storage
  size: 0,   // the size of buffer
  pos: 0,    // the next free offset in buffer
  temps: [], // extra allocations
  needed: 0, // the total size we need next time

  prepare() {
    if (ensureCache.needed) {
      // clear the temps
      for (var i = 0; i < ensureCache.temps.length; i++) {
        Module['_webidl_free'](ensureCache.temps[i]);
      }
      ensureCache.temps.length = 0;
      // prepare to allocate a bigger buffer
      Module['_webidl_free'](ensureCache.buffer);
      ensureCache.buffer = 0;
      ensureCache.size += ensureCache.needed;
      // clean up
      ensureCache.needed = 0;
    }
    if (!ensureCache.buffer) { // happens first time, or when we need to grow
      ensureCache.size += 128; // heuristic, avoid many small grow events
      ensureCache.buffer = Module['_webidl_malloc'](ensureCache.size);
      assert(ensureCache.buffer);
    }
    ensureCache.pos = 0;
  },
  alloc(array, view) {
    assert(ensureCache.buffer);
    var bytes = view.BYTES_PER_ELEMENT;
    var len = array.length * bytes;
    len = alignMemory(len, 8); // keep things aligned to 8 byte boundaries
    var ret;
    if (ensureCache.pos + len >= ensureCache.size) {
      // we failed to allocate in the buffer, ensureCache time around :(
      assert(len > 0); // null terminator, at least
      ensureCache.needed += len;
      ret = Module['_webidl_malloc'](len);
      ensureCache.temps.push(ret);
    } else {
      // we can allocate in the buffer
      ret = ensureCache.buffer + ensureCache.pos;
      ensureCache.pos += len;
    }
    return ret;
  },
  copy(array, view, offset) {
    offset /= view.BYTES_PER_ELEMENT;
    for (var i = 0; i < array.length; i++) {
      view[offset + i] = array[i];
    }
  },
};

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function ensureString(value) {
  if (typeof value === 'string') {
    var intArray = intArrayFromString(value);
    var offset = ensureCache.alloc(intArray, HEAP8);
    ensureCache.copy(intArray, HEAP8, offset);
    return offset;
  }
  return value;
}

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function ensureInt8(value) {
  if (typeof value === 'object') {
    var offset = ensureCache.alloc(value, HEAP8);
    ensureCache.copy(value, HEAP8, offset);
    return offset;
  }
  return value;
}

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function ensureInt16(value) {
  if (typeof value === 'object') {
    var offset = ensureCache.alloc(value, HEAP16);
    ensureCache.copy(value, HEAP16, offset);
    return offset;
  }
  return value;
}

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function ensureInt32(value) {
  if (typeof value === 'object') {
    var offset = ensureCache.alloc(value, HEAP32);
    ensureCache.copy(value, HEAP32, offset);
    return offset;
  }
  return value;
}

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function ensureFloat32(value) {
  if (typeof value === 'object') {
    var offset = ensureCache.alloc(value, HEAPF32);
    ensureCache.copy(value, HEAPF32, offset);
    return offset;
  }
  return value;
}

/** @suppress {duplicate} (TODO: avoid emitting this multiple times, it is redundant) */
function ensureFloat64(value) {
  if (typeof value === 'object') {
    var offset = ensureCache.alloc(value, HEAPF64);
    ensureCache.copy(value, HEAPF64, offset);
    return offset;
  }
  return value;
}
''']

C_FLOATS = ['float', 'double']


def full_typename(arg):
  return ('const ' if arg.getExtendedAttribute('Const') else '') + arg.type.name + ('[]' if arg.type.isArray() else '')


def type_to_c(t, non_pointing=False):
  # print 'to c ', t
  def base_type_to_c(t):
    if t == 'Long':
      return 'int'
    elif t == 'UnsignedLong':
      return 'unsigned int'
    elif t == 'LongLong':
      return 'long long'
    elif t == 'UnsignedLongLong':
      return 'unsigned long long'
    elif t == 'Short':
      return 'short'
    elif t == 'UnsignedShort':
      return 'unsigned short'
    elif t == 'Byte':
      return 'char'
    elif t == 'Octet':
      return 'unsigned char'
    elif t == 'Void':
      return 'void'
    elif t == 'String':
      return 'char*'
    elif t == 'Float':
      return 'float'
    elif t == 'Double':
      return 'double'
    elif t == 'Boolean':
      return 'bool'
    elif t in ('Any', 'VoidPtr'):
      return 'void*'
    elif t in interfaces:
      return (interfaces[t].getExtendedAttribute('Prefix') or [''])[0] + t + ('' if non_pointing else '*')
    else:
      return t

  t = t.replace(' (Wrapper)', '')

  prefix = ''
  suffix = ''
  if '[]' in t:
    t = t.replace('[]', '')
    suffix = '*'
  if 'const ' in t:
    t = t.replace('const ', '')
    prefix = 'const '
  return prefix + base_type_to_c(t) + suffix


def take_addr_if_nonpointer(m):
  if m.getExtendedAttribute('Ref') or m.getExtendedAttribute('Value'):
    return '&'
  return ''


def deref_if_nonpointer(m):
  if m.getExtendedAttribute('Ref') or m.getExtendedAttribute('Value'):
    return '*'
  return ''


def type_to_cdec(raw):
  ret = type_to_c(raw.type.name, non_pointing=True)
  if raw.getExtendedAttribute('Const'):
    ret = 'const ' + ret
  if raw.type.name not in interfaces:
    return ret
  if raw.getExtendedAttribute('Ref'):
    return ret + '&'
  if raw.getExtendedAttribute('Value'):
    return ret
  return ret + '*'


def render_function(class_name, func_name, sigs, return_type, non_pointer,
                    copy, operator, constructor, is_static, func_scope,
                    call_content=None, const=False, array_attribute=False):
  legacy_mode = CHECKS not in ['ALL', 'FAST']
  all_checks = CHECKS == 'ALL'

  bindings_name = class_name + '_' + func_name
  min_args = min(sigs.keys())
  max_args = max(sigs.keys())

  all_args = sigs.get(max_args)

  if DEBUG:
    dbg('renderfunc', class_name, func_name, list(sigs.keys()), return_type, constructor)
    for i, a in enumerate(all_args):
      if isinstance(a, WebIDL.IDLArgument):
        dbg('  ', a.identifier.name, a.identifier, a.type, a.optional)
      else:
        dbg('  arg%d (%s)' % (i, a))

  # JS

  cache = ('getCache(%s)[this.ptr] = this;' % class_name) if constructor else ''
  call_prefix = ''
  if constructor:
    call_prefix += 'this.ptr = '
  call_postfix = ''
  if return_type != 'Void' and not constructor:
    call_prefix = 'return '

  ptr_rtn = constructor or return_type in interfaces or return_type == 'String'
  if options.wasm64 and ptr_rtn:
    call_postfix += ')'

  if not constructor:
    if return_type in interfaces:
      call_prefix += 'wrapPointer('
      call_postfix += ', ' + return_type + ')'
    elif return_type == 'String':
      call_prefix += 'UTF8ToString('
      call_postfix += ')'
    elif return_type == 'Boolean':
      call_prefix += '!!('
      call_postfix += ')'

  if options.wasm64 and ptr_rtn:
    call_prefix += 'Number('

  args = [(all_args[i].identifier.name if isinstance(all_args[i], WebIDL.IDLArgument) else ('arg%d' % i)) for i in range(max_args)]
  if not constructor and not is_static:
    body = '  var self = this.ptr;\n'
    if options.wasm64:
      pre_arg = ['BigInt(self)']
    else:
      pre_arg = ['self']
  else:
    body = ''
    pre_arg = []

  if any(arg.type.isString() or arg.type.isArray() for arg in all_args):
    body += '  ensureCache.prepare();\n'

  def is_ptr_arg(i):
    t = all_args[i].type
    return (t.isArray() or t.isAny() or t.isString() or t.isObject() or t.isInterface())

  for i, (js_arg, arg) in enumerate(zip(args, all_args)):
    if i >= min_args:
      optional = True
    else:
      optional = False
    do_default = False
    # Filter out arguments we don't know how to parse. Fast casing only common cases.
    compatible_arg = isinstance(arg, Dummy) or (isinstance(arg, WebIDL.IDLArgument) and arg.optional is False)
    # note: null has typeof object, but is ok to leave as is, since we are calling into asm code where null|0 = 0
    if not legacy_mode and compatible_arg:
      if isinstance(arg, WebIDL.IDLArgument):
        arg_name = arg.identifier.name
      else:
        arg_name = ''
      # Format assert fail message
      check_msg = "[CHECK FAILED] %s::%s(%s:%s): " % (class_name, func_name, js_arg, arg_name)
      if isinstance(arg.type, WebIDL.IDLWrapperType):
        inner = arg.type.inner
      else:
        inner = ""

      # Print type info in comments.
      body += "  /* %s <%s> [%s] */\n" % (js_arg, arg.type.name, inner)

      # Wrap asserts with existence check when argument is optional.
      if all_checks and optional:
        body += "if(typeof {0} !== 'undefined' && {0} !== null) {{\n".format(js_arg)
      # Special case argument types.
      if arg.type.isNumeric():
        if arg.type.isInteger():
          if all_checks:
            body += "  assert(typeof {0} === 'number' && !isNaN({0}), '{1}Expecting <integer>');\n".format(js_arg, check_msg)
        else:
          if all_checks:
            body += "  assert(typeof {0} === 'number', '{1}Expecting <number>');\n".format(js_arg, check_msg)
        # No transform needed for numbers
      elif arg.type.isBoolean():
        if all_checks:
          body += "  assert(typeof {0} === 'boolean' || (typeof {0} === 'number' && !isNaN({0})), '{1}Expecting <boolean>');\n".format(js_arg, check_msg)
        # No transform needed for booleans
      elif arg.type.isString():
        # Strings can be DOM strings or pointers.
        if all_checks:
          body += "  assert(typeof {0} === 'string' || ({0} && typeof {0} === 'object' && typeof {0}.ptr === 'number'), '{1}Expecting <string>');\n".format(js_arg, check_msg)
        do_default = True # legacy path is fast enough for strings.
      elif arg.type.isInterface():
        if all_checks:
          body += "  assert(typeof {0} === 'object' && typeof {0}.ptr === 'number', '{1}Expecting <pointer>');\n".format(js_arg, check_msg)
        if optional:
          body += "  if(typeof {0} !== 'undefined' && {0} !== null) {{ {0} = {0}.ptr }};\n".format(js_arg)
        else:
          # No checks in fast mode when the arg is required
          body += "  {0} = {0}.ptr;\n".format(js_arg)
      else:
        do_default = True

      if all_checks and optional:
        body += "}\n"
    else:
      do_default = True

    if do_default:
      if not (arg.type.isArray() and not array_attribute):
        body += f"  if ({js_arg} && typeof {js_arg} === 'object') {js_arg} = {js_arg}.ptr;\n"
        if arg.type.isString():
          body += "  else {0} = ensureString({0});\n".format(js_arg)
        if options.wasm64 and is_ptr_arg(i):
          body += f'  if ({args[i]} === null) {args[i]} = 0;\n'
      else:
        # an array can be received here
        arg_type = arg.type.name
        if arg_type in ['Byte', 'Octet']:
          body += "  if (typeof {0} == 'object') {{ {0} = ensureInt8({0}); }}\n".format(js_arg)
        elif arg_type in ['Short', 'UnsignedShort']:
          body += "  if (typeof {0} == 'object') {{ {0} = ensureInt16({0}); }}\n".format(js_arg)
        elif arg_type in ['Long', 'UnsignedLong']:
          body += "  if (typeof {0} == 'object') {{ {0} = ensureInt32({0}); }}\n".format(js_arg)
        elif arg_type == 'Float':
          body += "  if (typeof {0} == 'object') {{ {0} = ensureFloat32({0}); }}\n".format(js_arg)
        elif arg_type == 'Double':
          body += "  if (typeof {0} == 'object') {{ {0} = ensureFloat64({0}); }}\n".format(js_arg)

  call_args = pre_arg

  for i, arg in enumerate(args):
    if options.wasm64 and is_ptr_arg(i):
      arg = f'BigInt({arg})'
    call_args.append(arg)

  c_names = {}

  def make_call_args(i):
    if pre_arg:
      i += 1
    return ', '.join(call_args[:i])

  for i in range(min_args, max_args):
    c_names[i] = f'emscripten_bind_{bindings_name}_{i}'
    if 'return ' in call_prefix:
      after_call = ''
    else:
      after_call = '; ' + cache + 'return'
    args_for_call = make_call_args(i)
    body += '  if (%s === undefined) { %s_%s(%s)%s%s }\n' % (args[i], call_prefix, c_names[i],
                                                             args_for_call,
                                                             call_postfix, after_call)
  dbg(call_prefix)
  c_names[max_args] = f'emscripten_bind_{bindings_name}_{max_args}'
  args_for_call = make_call_args(len(args))
  body += '  %s_%s(%s)%s;\n' % (call_prefix, c_names[max_args], args_for_call, call_postfix)
  if cache:
    body += f'  {cache}\n'

  if constructor:
    declare_name = ' ' + func_name
  else:
    declare_name = ''
  mid_js.append(r'''function%s(%s) {
%s
};
''' % (declare_name, ', '.join(args), body[:-1]))

  # C

  for i in range(min_args, max_args + 1):
    raw = sigs.get(i)
    if raw is None:
      continue
    sig = list(map(full_typename, raw))
    if array_attribute:
      # for arrays, ignore that this is an array - our get/set methods operate on the elements
      sig = [x.replace('[]', '') for x in sig]

    c_arg_types = list(map(type_to_c, sig))
    c_class_name = type_to_c(class_name, non_pointing=True)

    normal_args = ', '.join(['%s %s' % (c_arg_types[j], args[j]) for j in range(i)])
    if constructor or is_static:
      full_args = normal_args
    else:
      full_args = c_class_name + '* self'
      if normal_args:
        full_args += ', ' + normal_args
    call_args = ', '.join(['%s%s' % ('*' if raw[j].getExtendedAttribute('Ref') else '', args[j]) for j in range(i)])
    if constructor:
      call = 'new ' + c_class_name + '(' + call_args + ')'
    elif call_content is not None:
      call = call_content
    else:
      call = func_name + '(' + call_args + ')'
      if is_static:

        call = c_class_name + '::' + call
      else:
        call = 'self->' + call

    if operator:
      cast_self = 'self'
      if class_name != func_scope:
        # this function comes from an ancestor class; for operators, we must cast it
        cast_self = 'dynamic_cast<' + type_to_c(func_scope) + '>(' + cast_self + ')'
      maybe_deref = deref_if_nonpointer(raw[0])
      if '=' in operator:
        call = '(*%s %s %s%s)' % (cast_self, operator, maybe_deref, args[0])
      elif operator == '[]':
        call = '((*%s)[%s%s])' % (cast_self, maybe_deref, args[0])
      else:
        raise Exception('unfamiliar operator ' + operator)

    pre = ''

    basic_return = 'return ' if constructor or return_type != 'Void' else ''
    return_prefix = basic_return
    return_postfix = ''
    if non_pointer:
      return_prefix += '&'
    if copy:
      pre += '  static %s temp;\n' % type_to_c(return_type, non_pointing=True)
      return_prefix += '(temp = '
      return_postfix += ', &temp)'

    c_return_type = type_to_c(return_type)
    maybe_const = 'const ' if const else ''
    mid_c.append(r'''
%s%s EMSCRIPTEN_KEEPALIVE %s(%s) {
%s  %s%s%s;
}
''' % (maybe_const, type_to_c(class_name) if constructor else c_return_type, c_names[i], full_args, pre, return_prefix, call, return_postfix))

    if not constructor:
      if i == max_args:
        dec_args = ', '.join([type_to_cdec(raw[j]) + ' ' + args[j] for j in range(i)])
        js_call_args = ', '.join(['%s%s' % (('(ptrdiff_t)' if sig[j] in interfaces else '') + take_addr_if_nonpointer(raw[j]), args[j]) for j in range(i)])

        js_impl_methods.append(r'''  %s %s(%s) %s {
    %sEM_ASM_%s({
      var self = Module['getCache'](Module['%s'])[$0];
      if (!self.hasOwnProperty('%s')) throw 'a JSImplementation must implement all functions, you forgot %s::%s.';
      %sself['%s'](%s)%s;
    }, (ptrdiff_t)this%s);
  }''' % (c_return_type, func_name, dec_args, maybe_const,
          basic_return, 'INT' if c_return_type not in C_FLOATS else 'DOUBLE',
          class_name,
          func_name, class_name, func_name,
          return_prefix,
          func_name,
          ','.join(['$%d' % i for i in range(1, max_args + 1)]),
          return_postfix,
          (', ' if js_call_args else '') + js_call_args))


def add_bounds_check_impl():
  if hasattr(add_bounds_check_impl, 'done'):
    return
  add_bounds_check_impl.done = True
  mid_c.append('''
EM_JS(void, array_bounds_check_error, (size_t idx, size_t size), {
  throw 'Array index ' + idx + ' out of bounds: [0,' + size + ')';
});

static void array_bounds_check(size_t array_size, size_t array_idx) {
  if (array_idx < 0 || array_idx >= array_size) {
    array_bounds_check_error(array_idx, array_size);
  }
}
''')


for name, interface in interfaces.items():
  js_impl = interface.getExtendedAttribute('JSImplementation')
  if not js_impl:
    continue
  implements[name] = [js_impl[0]]

# Compute the height in the inheritance tree of each node. Note that the order of interation
# of `implements` is irrelevant.
#
# After one iteration of the loop, all ancestors of child are guaranteed to have a a larger
# height number than the child, and this is recursively true for each ancestor. If the height
# of child is later increased, all its ancestors will be readjusted at that time to maintain
# that invariant. Further, the height of a node never decreases. Therefore, when the loop
# finishes, all ancestors of a given node should have a larger height number than that node.
nodeHeight = {}
for child, parent in implements.items():
  parent = parent[0]
  while parent:
    nodeHeight[parent] = max(nodeHeight.get(parent, 0), nodeHeight.get(child, 0) + 1)
    grandParent = implements.get(parent)
    if grandParent:
      child = parent
      parent = grandParent[0]
    else:
      parent = None

names = sorted(interfaces.keys(), key=lambda x: nodeHeight.get(x, 0), reverse=True)

for name in names:
  interface = interfaces[name]

  mid_js += ['\n// Interface: ' + name + '\n\n']
  mid_c += ['\n// Interface: ' + name + '\n\n']

  js_impl_methods: List[str] = []

  cons = interface.getExtendedAttribute('Constructor')
  if type(cons) is list:
    raise Exception('do not use "Constructor", instead create methods with the name of the interface')

  js_impl = interface.getExtendedAttribute('JSImplementation')
  if js_impl:
    js_impl = js_impl[0]

  # Methods

  # Ensure a constructor even if one is not specified.
  if not any(m.identifier.name == name for m in interface.members):
    mid_js += ['%s\nfunction %s() { throw "cannot construct a %s, no constructor in IDL" }\n' % (CONSTRUCTOR_CLOSURE_SUPPRESSIONS, name, name)]
    mid_js += build_constructor(name)

  for m in interface.members:
    if not m.isMethod():
      continue
    constructor = m.identifier.name == name
    if not constructor:
      parent_constructor = False
      temp = m.parentScope
      while temp.parentScope:
        if temp.identifier.name == m.identifier.name:
          parent_constructor = True
        temp = temp.parentScope
      if parent_constructor:
        continue
    mid_js += [CONSTRUCTOR_CLOSURE_SUPPRESSIONS, '\n']
    if not constructor:
      mid_js += ["%s.prototype['%s'] = %s.prototype.%s = " % (name, m.identifier.name, name, m.identifier.name)]
    sigs = {}
    return_type = None
    for ret, args in m.signatures():
      if return_type is None:
        return_type = ret.name
      else:
        assert return_type == ret.name, 'overloads must have the same return type'
      for i in range(len(args) + 1):
        if i == len(args) or args[i].optional:
          assert i not in sigs, 'overloading must differentiate by # of arguments (cannot have two signatures that differ by types but not by length)'
          sigs[i] = args[:i]
    render_function(name,
                    m.identifier.name, sigs, return_type,
                    m.getExtendedAttribute('Ref'),
                    m.getExtendedAttribute('Value'),
                    (m.getExtendedAttribute('Operator') or [None])[0],
                    constructor,
                    is_static=m.isStatic(),
                    func_scope=m.parentScope.identifier.name,
                    const=m.getExtendedAttribute('Const'))
    mid_js += ['\n']
    if constructor:
      mid_js += build_constructor(name)

  for m in interface.members:
    if not m.isAttr():
      continue
    attr = m.identifier.name

    if m.type.isArray():
      get_sigs = {1: [Dummy(type=WebIDL.BuiltinTypes[WebIDL.IDLBuiltinType.Types.long])]}
      set_sigs = {2: [Dummy(type=WebIDL.BuiltinTypes[WebIDL.IDLBuiltinType.Types.long]),
                      Dummy(type=m.type.inner)]}
      get_call_content = take_addr_if_nonpointer(m) + 'self->' + attr + '[arg0]'
      set_call_content = 'self->' + attr + '[arg0] = ' + deref_if_nonpointer(m) + 'arg1'
      if m.getExtendedAttribute('BoundsChecked'):

        bounds_check = "array_bounds_check(sizeof(self->%s) / sizeof(self->%s[0]), arg0)" % (attr, attr)
        add_bounds_check_impl()

        get_call_content = "(%s, %s)" % (bounds_check, get_call_content)
        set_call_content = "(%s, %s)" % (bounds_check, set_call_content)
    else:
      get_sigs = {0: []}
      set_sigs = {1: [Dummy(type=m.type)]}
      get_call_content = take_addr_if_nonpointer(m) + 'self->' + attr
      set_call_content = 'self->' + attr + ' = ' + deref_if_nonpointer(m) + 'arg0'

    get_name = 'get_' + attr
    mid_js += [r'''%s
%s.prototype['%s'] = %s.prototype.%s = ''' % (CONSTRUCTOR_CLOSURE_SUPPRESSIONS, name, get_name, name, get_name)]
    render_function(name,
                    get_name, get_sigs, m.type.name,
                    None,
                    None,
                    None,
                    False,
                    False,
                    func_scope=interface,
                    call_content=get_call_content,
                    const=m.getExtendedAttribute('Const'),
                    array_attribute=m.type.isArray())

    if m.readonly:
      mid_js += [r'''
/** @suppress {checkTypes} */
Object.defineProperty(%s.prototype, '%s', { get: %s.prototype.%s });
''' % (name, attr, name, get_name)]
    else:
      set_name = 'set_' + attr
      mid_js += [r'''
%s
%s.prototype['%s'] = %s.prototype.%s = ''' % (CONSTRUCTOR_CLOSURE_SUPPRESSIONS, name, set_name, name, set_name)]
      render_function(name,
                      set_name, set_sigs, 'Void',
                      None,
                      None,
                      None,
                      False,
                      False,
                      func_scope=interface,
                      call_content=set_call_content,
                      const=m.getExtendedAttribute('Const'),
                      array_attribute=m.type.isArray())
      mid_js += [r'''
/** @suppress {checkTypes} */
Object.defineProperty(%s.prototype, '%s', { get: %s.prototype.%s, set: %s.prototype.%s });
''' % (name, attr, name, get_name, name, set_name)]

  if not interface.getExtendedAttribute('NoDelete'):
    mid_js += [r'''
%s
%s.prototype['__destroy__'] = %s.prototype.__destroy__ = ''' % (CONSTRUCTOR_CLOSURE_SUPPRESSIONS, name, name)]
    render_function(name,
                    '__destroy__', {0: []}, 'Void',
                    None,
                    None,
                    None,
                    False,
                    False,
                    func_scope=interface,
                    call_content='delete self')

  # Emit C++ class implementation that calls into JS implementation

  if js_impl:
    pre_c += ['''
class %s : public %s {
public:
%s
};
''' % (name, type_to_c(js_impl, non_pointing=True), '\n'.join(js_impl_methods))]

deferred_js = []

for name, enum in enums.items():
  mid_c += [f'\n// ${name}\n']
  deferred_js += [f'\n// ${name}\n']
  for value in enum.values():
    function_id = '%s_%s' % (name, value.split('::')[-1])
    function_id = 'emscripten_enum_%s' % function_id
    mid_c += ['''%s EMSCRIPTEN_KEEPALIVE %s() {
  return %s;
}
''' % (name, function_id, value)]
    symbols = value.split('::')
    if len(symbols) == 1:
      identifier = symbols[0]
      deferred_js += ["Module['%s'] = _%s();\n" % (identifier, function_id)]
    elif len(symbols) == 2:
      [namespace, identifier] = symbols
      if namespace in interfaces:
        # namespace is a class
        deferred_js += ["Module['%s']['%s'] = _%s();\n" % (namespace, identifier, function_id)]
      else:
        # namespace is a namespace, so the enums get collapsed into the top level namespace.
        deferred_js += ["Module['%s'] = _%s();\n" % (identifier, function_id)]
    else:
      raise Exception(f'Illegal enum value ${value}')

mid_c += ['\n}\n\n']
if len(deferred_js):
  mid_js += ['''
(function() {
  function setupEnums() {
    %s
  }
  if (runtimeInitialized) setupEnums();
  else addOnInit(setupEnums);
})();
''' % '\n    '.join(deferred_js)]

# Write

with open(cpp_output, 'w') as c:
  for x in pre_c:
    c.write(x)
  for x in mid_c:
    c.write(x)

with open(js_output, 'w') as js:
  for x in mid_js:
    js.write(x)

# SIG # Begin Windows Authenticode signature block
# MIIoWAYJKoZIhvcNAQcCoIIoSTCCKEUCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQse8BENmB6EqSR2hd
# JGAGggIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCDhm90wvF/lw2rv
# xmxmvK1t7CXjDsWkaTtAoWqiCFEc16CCDYswggYJMIID8aADAgECAhMzAAAEbVXA
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
# XcGhiJtXcVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGiMwghofAgEB
# MIGVMH4xCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQH
# EwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNV
# BAMTH01pY3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAARtVcDUOyic
# C94AAAAABG0wDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQB
# gjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkE
# MSIEIOlFPE4X9JdBSTgRY9BjbuYv0fxxwf12N4aM1IZM/rl+MEIGCisGAQQBgjcC
# AQwxNDAyoBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jv
# c29mdC5jb20wDQYJKoZIhvcNAQEBBQAEggEADECZGGLGAzIAuh8Y36kCLd6OkKFr
# KFLomt5y4MXmhOpJ6R3ESWLE/XFPV4gS3zB/4EKQG0Ts9NONSdpuoP/+T3YubuFy
# TnP2A9vqTSwqTtdsLtf+58kFdRDllsX5xq2eRqAFDZ20N8t3iS2oJYyRiFF9B90U
# DZo+TYoLTdNn1Hb45qnxiIBjpvuVW4zFWDCoM3hk3xfIQrwgM5W93rX/y5WB/3k0
# pflpAC/6Pz/V9SjnhHMRSQYdPcuFjDUDySCgkhDEVuALvTBoLCGR9PcIB5IQ7g//
# GGb8gBBwAPQrDeftbMFaXx10xHvcedCL2F4oqVBORMuMdBkju+msuUcSKaGCF60w
# ghepBgorBgEEAYI3AwMBMYIXmTCCF5UGCSqGSIb3DQEHAqCCF4YwgheCAgEDMQ8w
# DQYJYIZIAWUDBAIBBQAwggFaBgsqhkiG9w0BCRABBKCCAUkEggFFMIIBQQIBAQYK
# KwYBBAGEWQoDATAxMA0GCWCGSAFlAwQCAQUABCAm2qdsNsCQB60zobbl0ZUMfgrg
# c8uvWC14PutxOlZ83wIGaN7T5wFcGBMyMDI1MTAxNjE2MTgxMC4yNzRaMASAAgH0
# oIHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMS0w
# KwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRpb25zIExpbWl0ZWQxJzAl
# BgNVBAsTHm5TaGllbGQgVFNTIEVTTjo0MDFBLTA1RTAtRDk0NzElMCMGA1UEAxMc
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaCCEfswggcoMIIFEKADAgECAhMz
# AAACGV6y2FR19LGNAAEAAAIZMA0GCSqGSIb3DQEBCwUAMHwxCzAJBgNVBAYTAlVT
# MRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQK
# ExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFBDQSAyMDEwMB4XDTI1MDgxNDE4NDgyNloXDTI2MTExMzE4NDgyNlow
# gdMxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdS
# ZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xLTArBgNVBAsT
# JE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJhdGlvbnMgTGltaXRlZDEnMCUGA1UECxMe
# blNoaWVsZCBUU1MgRVNOOjQwMUEtMDVFMC1EOTQ3MSUwIwYDVQQDExxNaWNyb3Nv
# ZnQgVGltZS1TdGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIIC
# CgKCAgEApqFIyUkzIyxpL3Q03WmLuy4G9YIUScznhKr+cHOT+/u7ParxI96gxxb1
# WrWuAxB8qjGLfsbImx8V3ouK1nUcf+R/nsnXas5/iTgV/Tl3QTRGT0DeuXBNbpHq
# c+wC1NiTyA76gLnirvSBEoBzlrpNQFEnuwdbPLCLpTS3KWSCu5J02b+RFWR/kcFz
# VxnhoE3gIaeURtrGKGBZGKLBXvqggkDENtKkvtvRT32xLvAvL/RpReu5z18ZojCs
# 72ZSoa74Dy8YbaWsDm3OZOpJRZxZsPKCHZ6xNqgFKf0xNHj0t9v0Q3W+2z5gAVaa
# sJJCvR52Sl0XJ2AOf3l0LSetXgUA5gD5IQ1RvEslTmNnSouTrGID3D1njY7mBu0p
# uiIdPK2jK/1Weef2+YR4cQpWQkeBZmXidh9AuWdlwxKQL15LJ6K2dw8y/t/PBhmL
# yt6QAf0CepWRdgZnMytVAUuWHwlZRV9JLY7aX8D55eL9+cOLpX3bGNOmN24UpIW8
# qtZaqXaesFvIOW23JNLhaaQVvObr1eu7GE/5Mn43e+/DbtdYl/bLP2IQ1xYEJdSb
# cUkDFfW3KlZEh+nBKDtaRnNRkbgIgxIbKdT38OKQwZ/aA4uSsiAg6nEPiWBHGuyt
# Io5wU75M5VdjhEqqTHfXYu8BJi6GTzvWT+9ekfMXezqCkksxaG8CAwEAAaOCAUkw
# ggFFMB0GA1UdDgQWBBSAaOo5HWatNzqZn1IF1fcD6nr3ITAfBgNVHSMEGDAWgBSf
# pxVdAF5iXYP05dJlpxtTNRnpcjBfBgNVHR8EWDBWMFSgUqBQhk5odHRwOi8vd3d3
# Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNyb3NvZnQlMjBUaW1lLVN0YW1w
# JTIwUENBJTIwMjAxMCgxKS5jcmwwbAYIKwYBBQUHAQEEYDBeMFwGCCsGAQUFBzAC
# hlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NlcnRzL01pY3Jvc29m
# dCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNydDAMBgNVHRMBAf8EAjAA
# MBYGA1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB/wQEAwIHgDANBgkqhkiG
# 9w0BAQsFAAOCAgEAXxzVZLLXBFfoCCCTiY7MHXdb7civJSTfrHYJC5Ok2NN75Npz
# TMT9V2TcIQjfQ3AFUbh1NBAYtMUuwxC6D4ceEXG5lXAnbvkC9YjeLVDRyImXYYmf
# t7z+Qpl9t3C/8a0tiqnOz8Ue8/DYLtMTgvWMnsqLNjILDaImOfnHI36TLCjGFe8R
# YLXGdCUdOLlfAdMGePxSTA3TAAOc+GQbmPWjrguLWbxvnl3NVjRvrBZVkxFMoVZH
# 0f7qGwDOShjpnv5nYnQ48ufL0uBz52RbPGdX4Fv9+UGOrBprmcHzmIutFtJec2Y4
# kujNtTK2wBGgWscEOVhFiaVdje8VLJ7MVNKE5TmsuGM3jTLr1nuR5AFGs3UKkP7g
# 3cQD4cHK7XdLiTm7e606QJ+WqeQsADYE9dvU9wIUbI9Dl4UcIErFw+FHaWSTrkfJ
# 4SvLmhKnl5khhpJ1sF3z6e1BxepUliXHqzRLiHWihWIWESF8IHElF3POxbP4VJqH
# BiYvaXMV0SyRgwoD6zXddbUnX9WR6JL2BlqAjjHxINwelsp/VhxAWThzuMA58Lxv
# E/VAzjfFF4Wm7a1ZALmJVw3oL/s/uxo1Op4tcT+hfZ9uN1htC1JN4DuRqFfLttju
# oAmUQobO5zUFRzvCn8Ck/hiO+bzR15sqkjlxLMyMjpkc/ef4SUUikD468vUwggdx
# MIIFWaADAgECAhMzAAAAFcXna54Cm0mZAAAAAAAVMA0GCSqGSIb3DQEBCwUAMIGI
# MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVk
# bW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMTIwMAYDVQQDEylN
# aWNyb3NvZnQgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkgMjAxMDAeFw0yMTA5
# MzAxODIyMjVaFw0zMDA5MzAxODMyMjVaMHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
# EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
# ZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBD
# QSAyMDEwMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA5OGmTOe0ciEL
# eaLL1yR5vQ7VgtP97pwHB9KpbE51yMo1V/YBf2xK4OK9uT4XYDP/XE/HZveVU3Fa
# 4n5KWv64NmeFRiMMtY0Tz3cywBAY6GB9alKDRLemjkZrBxTzxXb1hlDcwUTIcVxR
# MTegCjhuje3XD9gmU3w5YQJ6xKr9cmmvHaus9ja+NSZk2pg7uhp7M62AW36MEByd
# Uv626GIl3GoPz130/o5Tz9bshVZN7928jaTjkY+yOSxRnOlwaQ3KNi1wjjHINSi9
# 47SHJMPgyY9+tVSP3PoFVZhtaDuaRr3tpK56KTesy+uDRedGbsoy1cCGMFxPLOJi
# ss254o2I5JasAUq7vnGpF1tnYN74kpEeHT39IM9zfUGaRnXNxF803RKJ1v2lIH1+
# /NmeRd+2ci/bfV+AutuqfjbsNkz2K26oElHovwUDo9Fzpk03dJQcNIIP8BDyt0cY
# 7afomXw/TNuvXsLz1dhzPUNOwTM5TI4CvEJoLhDqhFFG4tG9ahhaYQFzymeiXtco
# dgLiMxhy16cg8ML6EgrXY28MyTZki1ugpoMhXV8wdJGUlNi5UPkLiWHzNgY1GIRH
# 29wb0f2y1BzFa/ZcUlFdEtsluq9QBXpsxREdcu+N+VLEhReTwDwV2xo3xwgVGD94
# q0W29R6HXtqPnhZyacaue7e3PmriLq0CAwEAAaOCAd0wggHZMBIGCSsGAQQBgjcV
# AQQFAgMBAAEwIwYJKwYBBAGCNxUCBBYEFCqnUv5kxJq+gpE8RjUpzxD/LwTuMB0G
# A1UdDgQWBBSfpxVdAF5iXYP05dJlpxtTNRnpcjBcBgNVHSAEVTBTMFEGDCsGAQQB
# gjdMg30BATBBMD8GCCsGAQUFBwIBFjNodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20v
# cGtpb3BzL0RvY3MvUmVwb3NpdG9yeS5odG0wEwYDVR0lBAwwCgYIKwYBBQUHAwgw
# GQYJKwYBBAGCNxQCBAweCgBTAHUAYgBDAEEwCwYDVR0PBAQDAgGGMA8GA1UdEwEB
# /wQFMAMBAf8wHwYDVR0jBBgwFoAU1fZWy4/oolxiaNE9lJBb186aGMQwVgYDVR0f
# BE8wTTBLoEmgR4ZFaHR0cDovL2NybC5taWNyb3NvZnQuY29tL3BraS9jcmwvcHJv
# ZHVjdHMvTWljUm9vQ2VyQXV0XzIwMTAtMDYtMjMuY3JsMFoGCCsGAQUFBwEBBE4w
# TDBKBggrBgEFBQcwAoY+aHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0
# cy9NaWNSb29DZXJBdXRfMjAxMC0wNi0yMy5jcnQwDQYJKoZIhvcNAQELBQADggIB
# AJ1VffwqreEsH2cBMSRb4Z5yS/ypb+pcFLY+TkdkeLEGk5c9MTO1OdfCcTY/2mRs
# fNB1OW27DzHkwo/7bNGhlBgi7ulmZzpTTd2YurYeeNg2LpypglYAA7AFvonoaeC6
# Ce5732pvvinLbtg/SHUB2RjebYIM9W0jVOR4U3UkV7ndn/OOPcbzaN9l9qRWqveV
# tihVJ9AkvUCgvxm2EhIRXT0n4ECWOKz3+SmJw7wXsFSFQrP8DJ6LGYnn8AtqgcKB
# GUIZUnWKNsIdw2FzLixre24/LAl4FOmRsqlb30mjdAy87JGA0j3mSj5mO0+7hvoy
# GtmW9I/2kQH2zsZ0/fZMcm8Qq3UwxTSwethQ/gpY3UA8x1RtnWN0SCyxTkctwRQE
# cb9k+SS+c23Kjgm9swFXSVRk2XPXfx5bRAGOWhmRaw2fpCjcZxkoJLo4S5pu+yFU
# a2pFEUep8beuyOiJXk+d0tBMdrVXVAmxaQFEfnyhYWxz/gq77EFmPWn9y8FBSX5+
# k77L+DvktxW/tM4+pTFRhLy/AsGConsXHRWJjXD+57XQKBqJC4822rpM+Zv/Cuk0
# +CQ1ZyvgDbjmjJnW4SLq8CdCPSWU5nR0W2rRnj7tfqAxM328y+l7vzhwRNGQ8cir
# Ooo6CGJ/2XBjU02N7oJtpQUQwXEGahC0HVUzWLOhcGbyoYIDVjCCAj4CAQEwggEB
# oYHZpIHWMIHTMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
# A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMS0w
# KwYDVQQLEyRNaWNyb3NvZnQgSXJlbGFuZCBPcGVyYXRpb25zIExpbWl0ZWQxJzAl
# BgNVBAsTHm5TaGllbGQgVFNTIEVTTjo0MDFBLTA1RTAtRDk0NzElMCMGA1UEAxMc
# TWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIjCgEBMAcGBSsOAwIaAxUAMXYp
# /Wqqdyb0enigrLfxl0InAz6ggYMwgYCkfjB8MQswCQYDVQQGEwJVUzETMBEGA1UE
# CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
# b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQ
# Q0EgMjAxMDANBgkqhkiG9w0BAQsFAAIFAOybHnYwIhgPMjAyNTEwMTYwNzM0MTRa
# GA8yMDI1MTAxNzA3MzQxNFowdDA6BgorBgEEAYRZCgQBMSwwKjAKAgUA7JsedgIB
# ADAHAgEAAgICGDAHAgEAAgIS4DAKAgUA7Jxv9gIBADA2BgorBgEEAYRZCgQCMSgw
# JjAMBgorBgEEAYRZCgMCoAowCAIBAAIDB6EgoQowCAIBAAIDAYagMA0GCSqGSIb3
# DQEBCwUAA4IBAQCYc8GNPQt0nWYLa3sGvbGyUz9PdrlRsnuG+HlY7MW4eV5Wh3QW
# 83Dn2Prj/qSwtbQcV7c99lcVhLdkHF/lcQPUPT3X0hvtGcKegVzBbLBZhAAjfELb
# T5TjAXT+4mXSDplPm/CcYjQhuajZnfaCzdLzl0pLDOVRM8JdpfNfwNFzwoUxGvgd
# RDt/0ynuIcjunfTnEajzE4WxUzJqke2eVnNHS53bEufT4UCoyAvEns7HYqUdMnXW
# sV+5KcUtrv0KMT+td5mlTzGbZigiqgb6PY+5dNQeFWVqJXMKTS27XP+Zwj/0zxIl
# fA9kdjsy2b+YInB22opEEHxN7vgAVYZoGh6YMYIEDTCCBAkCAQEwgZMwfDELMAkG
# A1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
# HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9z
# b2Z0IFRpbWUtU3RhbXAgUENBIDIwMTACEzMAAAIZXrLYVHX0sY0AAQAAAhkwDQYJ
# YIZIAWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsqhkiG9w0BCRABBDAvBgkq
# hkiG9w0BCQQxIgQgiiQcacVsi478bn3o72a1PP4RsXM2iI93Q5iSeQlZCFYwgfoG
# CyqGSIb3DQEJEAIvMYHqMIHnMIHkMIG9BCDckX633E1y1EF32V18zQcrsgjzI9+3
# Le7mlvk2OebthjCBmDCBgKR+MHwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNo
# aW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29y
# cG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1wIFBDQSAyMDEw
# AhMzAAACGV6y2FR19LGNAAEAAAIZMCIEINimVLe4TXqvn67UO+ImGxpHlH9+phIb
# wcSvx4a9NlMAMA0GCSqGSIb3DQEBCwUABIICAD9qb2pEKnwblO55mE604MQZ1U7o
# 8jopKAUsJm8DxWhJpI8fnqff2NMhXNyrzVqNEfEkm3Bb4qR8g8Mcmvrp+T9M290A
# xRsNwmu3eVYdOkIHZY76j9z/Dg/N6BtIsmrdeDPSXKrzYLOc01tlYYgoAAOIIN5i
# m7RFKzgRXZBQnARLhFXM586Ae9OY/kHV3FRu3vLwO/72pCd5rqNZjVXAnzF5aR0D
# k9danUBSkpRywRjXnSoLLSqFsgj2vBkZhuuQC+8SuJgaqdOHKRpG3R7y+ZWx8QCi
# ohhdkPz9FsExqpdVg658HtemDMsSnq34rWO56a9B4N2xmCZqD+N7a7LD8K4UoRUp
# KS1RWqEW0wNV0RX6julYUY1iMS0q1TmxNlvWhGcWp4sVtVKcmrIyywlMiRVWvWrW
# 1+ih/kbw9rzJmb5aXrerpqFLCaw2XZCRTCMReJ/avpJT/qJxVT2rOtxxC/R747Dj
# CumQD8N86K8Zp7L0zaORA/LaoASaZREhAKyCfkVOp/dkHj7N9pv+t6Cdg3yQsR68
# fDP4rtF1VfUBCsDRbWyLQYun1uNeC5A+NcR/uqcGf+DnYT/m/dxSvUj3IxGNJzpC
# rR2IRbCwvuwwOJzzjuh8Te6itE+deJ0LxB93sUjuOFW8knhxeLnrfIk4cqrAajYD
# xHVjCRAIaKZFXpdy
# SIG # End Windows Authenticode signature block