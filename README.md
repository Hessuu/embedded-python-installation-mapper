# embedded-python-installation-mapper

## Terminology
| Term    | Meaning |
| -------- | ------- |
| Host | The developer's or user's machine like a desktop computer or a laptop where the mapper is started from. |
| Target | The device under development or evaluation, like an embedded device. This is the system whose Python installation is being mapped. |
| File object | A file or a directory. |
| Package | A collection of related file objects. For example, a package from Yocto, or all files in a directory. |
| Python module | Anything that is either: <br> (1) Executable with the Python interpreter <br> (2) Importable from another Python module. <br><br> Python modules can be file objects on the file system or a built-in module that is part of the interpreter. Files can be in Python's native formats .py and .pyc, but also "foreign" formats like .so and .rst |
| Python file | A Python module that explicitly manifests as a file on the file system (i.e. not a built-in). |
| Theoretical size | The size of a file object's contents. Might not correspond to size taken on disk. |
| Real size | The size that a file object takes up on disk. Tends to be a multiple of the file system's block size. This also means that there is a minimum size for a file object, like 4 KB. |
