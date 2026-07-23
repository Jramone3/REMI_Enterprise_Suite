s happening.

from distutils import cmd
import distutils.command.sdist as sdist

# import last to prevent caching
from distutils import {imported_module}

for mod in (cmd, sdist):
    assert mod.{imported_module} == {imported_module}, (
        f"\n{{mod.dir_util}}\n!=\n{{{imported_module}}}"
    )

print("success")
Ú
tmpdir_cwd)