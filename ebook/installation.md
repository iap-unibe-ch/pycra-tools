# Installation instructions

We suggest to use [pip](https://pip.pypa.io/en/stable/) package installer and the [venv](https://docs.python.org/3/library/venv.html) module for installing the package in a lightweight virtual environment.
Using Python's built-in virtual environments is preferable to separate the dependencies for different projects and from the python system install. This avoids compatibility problems and conflicts between modules and packages, which might cause instability and bugs when we use python.

## 1. Create and activate virtual environment
A comprehensive tutorial about Python virtual environments is e.g. [RealPython -- Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer/). 
The following instructions just outline the idea. The user is kindly asked to consult professional instructions.

```{warning}
The authors disclaim all responsibility. The responsibility lies entirely with the user.
```

### Linux
For example, create an extra directory (say "/opt/venv"), inside of which we create the desired environment (say "pycraenv").
```sh
mkdir /opt/venv
```
```sh
python3 -m venv /opt/venv/pycraenv
```
```sh
source /opt/venv/pycraenv/bin/activate
```

### Windows (PowerShell)
For example, create an extra directory (say "C:\Tools\python\venv"), inside of which we create the desired environment (say "pycraenv").
```sh
New-Item -Path 'C:\Tools\python\venv' -ItemType Directory
```
```sh
python -m venv C:\Tools\python\venv\pycraenv
```
```sh
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
```sh
C:\Tools\python\venv\pycraenv\Scripts\Activate.ps1
```

## 2. Make sure pip is up to date
```sh
pip install --upgrade pip
```

## 3. Install pycra-tools package
```sh
pip install pycra-tools
```
