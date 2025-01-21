#!/usr/bin/env python3
# -*- coding: utf-8 -*-

description = """
Description:

    Read parameter-scan-data for S22 calibration correction:
    water surface is closer to antenna than calibration plate
    --> Simulate coupling of calibration plate at position of water surface
    
"""

import os
import sys
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from pycra import torfile
from pycra.coupling import cutfile

sys.path.insert(1, '/home/phjschmid/phdphysics/code/tools/tools_python')
from mypytools.grasp import plot_gridfile
from mypytools.grasp.ffparams import compute_directivity, directivity_to_dB
from mypytools.mypyplot.utils import export_figure

def main():

    directory_data = './coupling_and_plate/Job_01'
    torfilename = os.path.join(directory_data, os.path.basename(directory_data) + '.tor')
    tordict = torfile.tor2dict(torfilename)
    
    #cutfilename = os.path.join(directory_data, 'coupling_system_horn0.cut')
    #da = cutfile.readcut(cutfilename, tordict=tordict)
    #print(da)
    
    cutfilename = os.path.join(directory_data, 'coupling_system_horn0_trivial.cut')
    da = cutfile.readcut(cutfilename, tordict=tordict)
    print(da)
        
    # cutfilename = os.path.join(directory_data, 'coupling_system_horn1.cut')
    # da = cutfile.readcut(cutfilename, tordict=tordict)
    # print(da)
    
    cutfilename = os.path.join(directory_data, 'coupling_system_horn2.cut')
    da = cutfile.readcut(cutfilename, tordict=tordict)
    print(da)
    
    print(da)
    
    return

if __name__ == '__main__':
    main()