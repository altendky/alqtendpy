import os
import pathlib
import shutil
import sys


if 'win32' in sys.platform:
    source = pathlib.Path(os.environ['PYTHON']) / 'python3.dll'
    destination = pathlib.Path(os.environ['VENV']) / 'Scripts'
    # str() required for python 3.5  :[
    shutil.copy(str(source), str(destination))
