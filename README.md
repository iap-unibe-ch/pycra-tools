# pycra-tools

[![License](https://img.shields.io/pypi/l/graspy.svg?color=green)](https://github.com/iap-unibe-ch/pycra/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)

Package to process Ticra Tools .grd and .cut files based on xarray. You should familiarise yourself with xarray to be 
able to use this package effectively.

## Installation instructions

0. Create virtual environment 
### What is the idea?
We do not install the modules or packages directly to your "system install" of Python:<br>
Modules and packages may conflict with each other and with the version of Python you have installed on your system. 
If there is a compatibility problem, it can cause instability or bugs when you try to use Python.<br>
<br>Instead, it is preferable to use Python's built-in virtual environments:<br>
Each virtual environment can have its own Python version, separate packages and modules, and other variables. 
That lets you keep the dependencies for each project separate from each other and from your system installation. 
This ensures that compatibility problems won't affect the primary Python installation on your PC, 
and that it doesn't become a bloated mess of extra packages and modules.<br>
For instance, create an extra directory (say "venv"), inside of which we create the desired environment (say "pycraenv").
### Linux
mkdir /opt/venv <br>
python3 -m venv /opt/venv/pycraenv<br>
### Windows (PowerShell)
New-Item -Path 'C:\Tools\python\venv' -ItemType Directory<br>
python -m venv C:\Tools\python\venv\pycraenv

1. Activate your virtual environment
### Linux
source /opt/venv/pycraenv/bin/activate
### Windows (PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass<br>
C:\Tools\python\venv\pycraenv\Scripts\Activate.ps1

2. Make sure pip is up to date: 
`pip install --upgrade pip`

3. Install the package:
`pip install git+https://git.iap.unibe.ch/TICRA_Tools/pycra.git`


## Usage example

    from pycra import torfile
    from pycra.coupling import cutfile as cutfile_coupling
    from pycra.fields import cutfile as cutfile_fields
    from pycra.fields import gridfile as gridfile_fields
    
    directory_example_simulation = '/opt/venv/pycra/example'
    torfilename = os.path.join(directory_example_simulation, 'Job_01', 'Job1.tor')
    cutfilename_coupling = os.path.join(directory_example_simulation, 'Job_01', 'coupling_system.cut')
    cutfilename_field = os.path.join(directory_example_simulation, 'Job_01', 'single_cut.cut')
    gridfilename_field = os.path.join(directory_example_simulation, 'Job_01', 'single_grid.grd')

    tordict = torfile.tor2dict(torfilename)
    da_couplingcut = cutfile_coupling.readcut(cutfilepath=cutfilename_coupling, tordict=torfilename)
    da_fieldcut = cutfile_fields.readcut(gridfilename_field, tordict=tordict)
    da_fieldgrid = gridfile_fields.readgrid(gridfilename_field, tordict=tordict)

For cutfiles:
```py
from pycra.cutfile import *
import os

os.chdir("/path/to/your/data")
# Import can handle multiple files, so if you're importing a single file still put it in a list
mycut = cut(["filename.cut"])
# Converting the complex data into dB data and overwriting the old complex data with db data
mycut = decibel(mycut)
# Plotting the db data variable from "mycut". Since the db has too many dimensions we need to slice it.
# Here we choose only the co-polar component. 
plotcut(mycut.sel(comp="Co"))
```

For gridfiles:
```py
from pycra.gridfile import *
import os

os.chdir("/path/to/your/data")
# Import can handle multiple files, so if you're importing a single file still put it in a list
mygrid = grid(["filename.cut"])
# Converting the complex data into dB data and overwriting the old complex data with db data
mygrid = co_cross(mygrid)
# Plotting the db data variable from "mygrid". Since the db has too many dimensions we need to slice it.
# Here we choose only the co-polar component. 
plotgrid(mygrid.sel(comp="Co"))
```
