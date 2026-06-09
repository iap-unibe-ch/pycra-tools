# pycra-tools
	
[![License](https://img.shields.io/pypi/l/graspy.svg?color=green)](https://github.com/iap-unibe-ch/pycra/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)

Package to process Ticra Tools .grd and .cut files based on xarray. You should familiarise yourself with xarray to be 
able to use this package effectively.

## Installation instructions
### Create virtual environment 
We do not install the modules or packages directly to your "system install" of Python:<br>
Modules and packages may conflict with each other and with the version of Python you have installed on your system. 
If there is a compatibility problem, it can cause instability or bugs when you try to use Python.<br>
<br>Instead, it is preferable to use Python's built-in virtual environments:<br>
Each virtual environment can have its own Python version, separate packages and modules, and other variables. 
That lets you keep the dependencies for each project separate from each other and from your system installation. 
This ensures that compatibility problems won't affect the primary Python installation on your PC, 
and that it doesn't become a bloated mess of extra packages and modules.<br>
For instance, create an extra directory (say "venv"), inside of which we create the desired environment (say "pycraenv").

#### Linux
`
mkdir /opt/venv 
python3 -m venv /opt/venv/pycraenv
`
#### Windows (PowerShell)
`
New-Item -Path 'C:\Tools\python\venv' -ItemType Directory
python -m venv C:\Tools\python\venv\pycraenv
`
### Activate your virtual environment
#### Linux
`
source /opt/venv/pycraenv/bin/activate
`
#### Windows (PowerShell)
`
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
C:\Tools\python\venv\pycraenv\Scripts\Activate.ps1
`

### Install pycra-tools
Ensuring pip is up to date: 

`pip install --upgrade pip`

Install the package:	

`pip install pycra-tools`
