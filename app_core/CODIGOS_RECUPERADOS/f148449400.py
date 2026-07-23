led with one argument, an OSError instance.  It can
report the error to continue with the walk, or raise the exception
to abort the walk.  Note that the filename is available as the
filename attribute of the exception object.

By default, os.walk does not follow symbolic links to subdirectories on
systems that support them.  In order to get this functionality, set the
optional argument 'followlinks' to true.

Caution:  if you pass a relative pathname for top, don't change the
current working directory between resumptions of walk.  walk never
changes the current directory, and assumes that the client doesn't
either.

Example:

import os
from os.path import join, getsize
for root, dirs, files in os.walk('python/Lib/xml'):
    print(root, "consumes ")
    print(sum(getsize(join(root, name)) for name in files), end=" ")
    print("bytes in", len(files), "non-directory files")
    if '__pycache__' in dirs:
        dirs.remove('__pycache__')  # don't visit __pycache__ directories

z