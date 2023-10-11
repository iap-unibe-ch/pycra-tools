# pycra

[![License](https://img.shields.io/pypi/l/graspy.svg?color=green)](https://github.com/Spect4tor/graspy/raw/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)

Package to process Ticra Tools .grd and .cut files based on xarray. You should familiarise yourself with xarray to be 
able to use this package effectively.

## Installation instructions

1. Activate your virtual environment
```sh
# Linux
source path-to-venv/bin/activate
# Windows
path-to-venv\Scripts\activate
```
2. Make sure pip is up to date 
```sh
pip install --upgrade pip
```
3. Install the pycra package
```sh
pip install git+https://git.iap.unibe.ch/albers/pycra.git
```


## Usage example
For cutfiles:
```py
from pycra.cutfile import *
import os

os.chdir("/path/to/your/data")
# Import can handle multiple files, so if you're importing a single file still put it in a list
mycut = cut(["filename.cut"])
# Converting the complex data into dB data
mycut = decibel(mycut)
# Plotting the db data variable from "mycut"
plotcut(mycut.db)
```

For gridfiles:
```py
from pycra.gridfile import *
import os

os.chdir("/path/to/your/data")
# Import can handle multiple files, so if you're importing a single file still put it in a list
mygrid = grid(["filename.cut"])
# Converting the complex data into dB data
mygrid = co_cross(mygrid)
# Plotting the db data variable from "mygrid"
plotcont(mygrid.db)
```
