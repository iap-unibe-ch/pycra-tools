import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pycra_tools import readcut, readgrid, torfile

def cutplot_magnitudes(da):
    
    nr_components = len(da.comp.values)
    fig, ax = plt.subplots(1, nr_components, figsize=(4*nr_components+2, 5))
    for ii,_ in enumerate(da.comp.values):
        ax[ii].set_xlabel(f"${da.Y.attrs['texname']}$ ({da.Y.attrs['units']})" if da.Y.attrs['units'] else da.Y.attrs['texname'])
        ax[ii].set_ylabel(f"${da.comp.attrs['names_math'][ii]}$ ({da.comp.attrs['units_math'][ii]})")
        for jj,xval in enumerate(da.X.values):
            ax[ii].plot(da.Y.values, np.abs(da.values)[:,jj,ii], label=f"{xval} {da.X.units}")
        ax[ii].legend()
        ax[ii].grid(True, which='major', axis='both')
    
    return fig, ax

def gridplot_magnitudes(da):
    
    nr_components = len(da.comp.values)
    fig, ax = plt.subplots(1, nr_components, figsize=(4*nr_components+2, 5))
    for ii,_ in enumerate(da.comp.values):
        ax[ii].set_xlabel(f"{da.X.attrs['texname']} ({da.X.attrs['units']})" if da.X.attrs['units'] else da.X.attrs['texname'])
        ax[ii].set_ylabel(f"{da.Y.attrs['texname']} ({da.Y.attrs['units']})" if da.Y.attrs['units'] else da.Y.attrs['texname'])
        img = ax[ii].imshow(np.abs(da.values)[:,:,ii], 
                        extent=[np.min(da.X.values), np.max(da.X.values), 
                                np.min(da.Y.values), np.max(da.Y.values)], 
                        vmin=None, vmax=None, cmap=mpl.colormaps['viridis'])
        divider = make_axes_locatable(ax[ii])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(img, cax=cax)
        cax.set_ylabel(f"${da.comp.attrs['names_math'][ii]}$ ({da.comp.attrs['units_math'][ii]})")
            
    return fig, ax

# print(readgrid.__doc__) # show function docstring
# print(readgrid.__doc__) # show function docstring
# print(torfile.__doc__) # show function docstring

# define filepaths
directory_example_simulation = '/home/phjschmid/phdphysics/simulation/projects/pycra_tools/fields_example'
torfilepath = os.path.join(directory_example_simulation, 'Job_01', 'Job_01.tor')
cutfilepath = os.path.join(directory_example_simulation, 'Job_01', 'spherical_cut_far_E.cut')
grdfilepath_efield = os.path.join(directory_example_simulation, 'Job_01', 'spherical_grid_uv_near_E.grd')
grdfilepath_hfield = os.path.join(directory_example_simulation, 'Job_01', 'spherical_grid_uv_near_H.grd')

# read files
# Ticra Tools manual 24.1.0: pp. 349--350, 3275 (units)
tordict = torfile.tor2dict(torfilepath)
da_cut_efield = readcut(cutfilepath=cutfilepath, tordict=tordict)
da_grid_efield = readgrid(gridfilepath=grdfilepath_efield, tordict=tordict)
dh_grid_hfield = readgrid(gridfilepath=grdfilepath_hfield, tordict=tordict)

print(da_cut_efield)
print('\n')
print(da_cut_efield.X)
print('\n')
print(da_cut_efield.Y)
print('\n')
print(da_cut_efield.comp)
print('\n')
print(da_cut_efield.attrs)
print('\n')
print(da_cut_efield.freq)

print(da_grid_efield)
print('\n')
print(da_grid_efield.X)
print('\n')
print(da_grid_efield.Y)
print('\n')
print(da_grid_efield.comp)
print('\n')
print(da_grid_efield.attrs)
print('\n')
print(da_grid_efield.freq)

fig, ax = cutplot_magnitudes(da_cut_efield.sel(freq=da_cut_efield.freq.values[0]))
plt.tight_layout()
plt.show()

fig, ax = gridplot_magnitudes(da_grid_efield.sel(freq=da_grid_efield.freq.values[0]))
plt.tight_layout()
plt.show()

raise

# da_grd_hfield = readgrid(gridfilepath=grdfilepath_efield, tordict=tordict)
# print(da_grd_hfield)


fig, ax = plot_magnitudes(da, freq, #vmin=-40, vmax=0, 
                          normalize_with_maxvalue=False,
                          #contourlevels = [-50,-40,-30,-20,-10], 
                          colors=None)

# 1. Read one file (.tor file available)

# # 1. Reading multiple files from same project (same .tor file): better read .tor file only once
# tordict = torfile.tor2dict(torfilepath_example01_job01)
# da_cut_example01_job01 = readcut(cutfilepath=cutfilepath_example01_job01, tordict=tordict)
# da_cut_example01_job01 = readcut(cutfilepath=cutfilepath_example01_job02, tordict=tordict)
# da_grd_example01_job01 = readgrid(gridfilepath=grdfilepath_example01_job02, tordict=tordict)

# 3. Read file with info from the user (no .tor file available)