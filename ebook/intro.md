# Welcome to pycra-tools

[![License](https://img.shields.io/pypi/l/graspy.svg?color=green)](https://github.com/iap-unibe-ch/pycra/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)

The purpose of this package is to process file outputs of from software products of [TICRA](https://www.ticra.com/), 
such as the *General Reflector Antenna Software Package* (GRASP). The name of the package derives from [TICRA Tools](https://www.ticra.com/software/ticratools/), 
TICRA\'s shared interface to multiple of its software products.

Pycra-tools currently supports the following data formats:
- GRASP field data in cuts: `.cut`
- GRASP field data in grids: `.grd` / `.h5`
- GRASP coupling data in cuts: `.cut`

Numerical data and some information is stored in these files, 
but parts of the relevant information is normally also stored in the project\'s TICRA object repository `.tor` file, or must be read from the `.tci` file (or provided by the user). 
Pycra-tools gathers the data and stores it in [Xarray](https://docs.xarray.dev/en/stable/) data structures, in the form of a labeled multi-dimensional array.

This documentation comprises the following contents:

```{tableofcontents}
```

```{note}
We kindly welcome suggestions for improvement, as well as implementations for other files (e.g. GRASP coupling date in grids).
```
