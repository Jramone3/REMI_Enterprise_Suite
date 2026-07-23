import io
import ntpath
import operator
import os
import posixpath
import sys
import warnings
from glob import _StringGlobber
from itertools import chain
from _collections_abc import Sequence

try:
    import pwd
except ImportError:
    pwd = None
try:
    import grp
except ImportError:
    grp = None

from ._abc import UnsupportedOperation, PurePathBase, PathBase


__all__ = [
    "PurePath", "PurePosixPath", "PureWindowsPath",
    "Path", "PosixPath", "WindowsPath",
    ]


class _PathParents(Sequence):
    """This object provides sequence-like access to the logical ancestors
    of a path.  Don't try to construct it yourself."""
    __slots__ = ('_path', '_drv', '_root', '_tail')

    def __init__(self, path):
        self._path = path
        self._drv = path.drive
        self._root = path.root
        self._tail = path._tail

    def __len__(self):
        return len(self._tail)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return tuple(self[i] for i in range(*idx.indices(len(self))))

        if idx >= len(self) or idx < -len(self):
            raise IndexError(idx)
        if idx < 0:
            idx += len(self)
        return self._path._from_parsed_parts(self._drv, self._root,
                                             self._tail[:-idx - 1])

    def __repr__(self):
        return "<{}.parents>".format(type(self._path).__name__)


class PurePath(PurePathBase):
    """Base class for manipulating paths without I/O.

    PurePath represents a filesystem path and offers operations which
    don't imply any actual filesystem I/O.  Depending on your system,
    instantiating a PurePath will return either a PurePosixPath or a
    PureWindowsPath object.  You can also instantiate either of these classes
    directly, regardless of your system.
    """

    __slots__ = (
        # The `_raw_paths` slot stores unnormalized string paths. This is set
        # in the `__init__()` method.
        '_raw_paths',

        # The `_drv`, `_root` and `_tail_cached` slots store parsed and
        # normalized parts of the path. They are set when any of the `drive`,
        # `root` or `_tail` properties are accessed for the first time. The
        # three-part division corresponds to the result of
        # `os.path.splitroot()`, except that the tail is further split on path
        # separators (i.e. it is a list of strings), and that the root and
        # tail are normalized.
        '_drv', '_root', '_tail_cached',

        # The `_str` slot stores the string representation of the path,
        # computed from the drive, root and tail when `__str__()` is called
        # for the first time. It's used to implement `_str_normcase`
        '_str',

        # The `_str_normcase_cached` slot stores the string path with
        # normalized case. It is set when the `_str_normcase` property is
        # accessed for the first time. It's used to implement `__eq__()`
        # `__hash__()`, and `_parts_normcase`
        '_str_normcase_cached',

        # The `_parts_normcase_cached` slot stores the case-normalized
        # string path after splitting on path separators. It's set when the
        # `_parts_normcase` property is accessed for the first time. It's used
        # to implement comparison methods like `__lt__()`.
        '_parts_normcase_cached',

        # The `_hash` slot stores the hash of the case-normalized string
        # path. It's set when `__hash__()` is called for the first time.
        '_hash',
    )
    parser = os.path
    _globber = _StringGlobber

    def __new__(cls, *args, **kwargs):
        """Construct a PurePath from one or several strings and or existing
        PurePath objects.  The strings and path objects are combined so as
        to yield a canonicalized path, which is incorporated into the
        new PurePath object.
        """
        if cls is PurePath:
            cls = PureWindowsPath if os.name == 'nt' else PurePosixPath
        return object.__new__(cls)

    def __init__(self, *args):
        paths = []
        for arg in args:
            if isinstance(arg, PurePath):
                if arg.parser is not self.parser:
                    # GH-103631: Convert separators for backwards compatibility.
                    paths.append(arg.as_posix())
                else:
                    paths.extend(arg._raw_paths)
            else:
                try:
                    path = os.fspath(arg)
                except TypeError:
                    path = arg
                if not isinstance(path, str):
                    raise TypeError(
                        "argument should be a str or an os.PathLike "
                        "object where __fspath__ returns a str, "
                        f"not {type(path).__name__!r}")
                paths.append(path)
        # Avoid calling super().__init__, as an optimisation
        self._raw_paths = paths

    def joinpath(self, *pathsegments):
        """Combine this path with one or several arguments, and return a
        new path representing either a subpath (if all arguments are relative
        paths) or a totally different path (if one of the arguments is
        anchored).
        """
        return self.with_segments(self, *pathsegments)

    def __truediv__(self, key):
        try:
            return self.with_segments(self, key)
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, key):
        try:
            return self.with_segments(key, self)
        except TypeError:
            return NotImplemented

    def __reduce__(self):
        return self.__class__, tuple(self._raw_paths)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.as_posix())

    def __fspath__(self):
        return str(self)

    def __bytes__(self):
        """Return the bytes representation of the path.  This is only
        recommended to use under Unix."""
        return os.fsencode(self)

    @property
    def _str_normcase(self):
        # String with normalized case, for hashing and equality checks
        try:
            return self._str_normcase_cached
        except AttributeError:
            if self.parser is posixpath:
                self._str_normcase_cached = str(self)
            else:
                self._str_normcase_cached = str(self).lower()
            return self._str_normcase_cached

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self._str_normcase)
            return self._hash

    def __eq__(self, other):
        if not isinstance(other, PurePath):
            return NotImplemented
        return self._str_normcase == other._str_normcase and self.parser is other.parser

    @property
    def _parts_normcase(self):
        # Cached parts with normalized case, for comparisons.
        try:
            return self._parts_normcase_cached
        except AttributeError:
            self._parts_normcase_cached = self._str_normcase.split(self.parser.sep)
            return self._parts_normcase_cached

    def __lt__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase < other._parts_normcase

    def __le__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase <= other._parts_normcase

    def __gt__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase > other._parts_normcase

    def __ge__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase >= other._parts_normcase

    def __str__(self):
        """Return the string representation of the path, suitable for
        passing to system calls."""
        try:
            return self._str
        except AttributeError:
            self._str = self._format_parsed_parts(self.drive, self