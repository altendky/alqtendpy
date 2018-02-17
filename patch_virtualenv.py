import argparse
import os
import pathlib
import shutil
import sys


if 'win32' in sys.platform:
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination')
    args = parser.parse_args()

    source = pathlib.Path(os.environ['PYTHON']) / 'python3.dll'
    # str() required for python 3.5  :[
    shutil.copy(str(source), args.destination)
