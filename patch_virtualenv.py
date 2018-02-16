import os
import pathlib
import shutil
import sys


if 'win32' in sys.platform:
    source = pathlib.Path(os.environ['PYTHON']) / 'python3.dll'
    destination = pathlib.Path(os.environ['VENV']) / 'Scripts'
    shutil.copy(source, destination)
