import re
import pint
#import h5py
import xarray as xr
import numpy as np
from pathlib import Path

from . import labels
from .. import torfile

def grid2dict_h5(gridfilepath: Path):
    
    griddict = {}
    
    # with h5py.File(gridfilepath, "r") as f:
    #     # Print all root level object names (aka keys) 
    #     # these can be group or dataset names 
    #     print("Keys: %s" % f.keys())
    #     # get first object name/key; may or may NOT be a group
    #     a_group_key = list(f.keys())[0]
    #     # get the object type for a_group_key: usually group or dataset
    #     print(type(f[a_group_key])) 
    #     # If a_group_key is a dataset name, 
    #     # this gets the dataset values and returns as a list
    #     data = list(f[a_group_key])
    #     # preferred methods to get dataset values:
    #     ds_obj = f[a_group_key]      # returns as a h5py dataset object
    #     ds_arr = f[a_group_key][()]  # returns as a numpy array

    # f = h5py.File(gridfilepath, 'r')
    # print(f.keys())

    # print('\n')

    # keys = list(f['/object'].attrs.keys())
    # print(keys)
    # for key in keys:
    #     temp = f['/object'].attrs[key]
    #     print('%s: %s' % (key, temp))
    
    # print('\n')

    # print(f['/parameterlist'][()])

    # print('\n')

    # keys = list(f['/parameters'].keys())
    # print(keys)
    # for key in keys:
    #     temp = f['/parameters'][key][()]
    #     print('%s: %s' % (key, temp))

    # # allocate data
    # data = f['/data'][()]
    # icomp = f['/object'].attrs['icomp']
    # icomp = f['/object'].attrs['igrid']
    # freqs = f['/parameters']['frequency']
    # freqs_unit = f['/parameters']['frequency'].attrs['unit'].decode()
    # print(freqs_unit)
    # print(icomp)

    # f.close()

    # raise
    
    return griddict