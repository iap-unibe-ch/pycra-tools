import h5py
import xarray as xr
import numpy as np
from pathlib import Path

from pycra.fields import labels

def grid2dict_h5(gridfilepath: Path):
    # This is the new file format for Ticra Tools 24.1 grids
    griddict = {}

    h5grid = h5py.File(gridfilepath)
    # Checking if the h5 file is the correct format
    if h5grid["info"].attrs["version"] != 2:
        raise Exception(f'TICRA h5 file version {h5grid["info"]["version"]} incompatible with Pycra. Version 2 expected')


    nset = np.size(h5grid["data"], 1)

    beamc = []
    for i in range(int(nset)):
        # beam_centres seem to return as int32 array from the h5 files
        beamc.append([s for s in h5grid["object"].attrs["beam_centres"][:]])

    # Extract names of parameters from the /parameterlist
    param_l = [param.decode('utf-8') for param in h5grid["parameterlist"][()]]
    freqs_Hz = h5grid["parameters"]["frequency"][:]
    ycoords = h5grid["parameters"][param_l[2]][:]
    xcoords = h5grid["parameters"][param_l[3]][:]
    ny = len(ycoords)
    nx = len(xcoords)
    ylims = tuple([ycoords[0],ycoords[-1]])
    xlims = tuple([xcoords[0],xcoords[-1]])
    # Below are properties which exist in .grd but are not specified the same way in .h5
    # ktype no longer exists in h5
    ktype = 1
    # klimit no longer exists in h5, instead field class is specified
    if h5grid["object"].attrs["truncation"].decode('utf-8') == "rectangular":
        klimit = 0
    elif h5grid["object"].attrs["truncation"].decode('utf-8') == "elliptical":
        klimit = 1
    # below no longer exists in h5
    # sources = "not tracked"
    # freq_name = "not tracked"

    ncomp = h5grid["data"].shape[4]
    igrid = h5grid["object"].attrs["igrid"]
    icomp = h5grid["object"].attrs["icomp"]

    data = np.full(shape=(ny, nx, ncomp, len(freqs_Hz)), fill_value=complex(np.nan, np.nan), dtype=complex)
    # We need to rearrange the multidimensional array. Its NF, NB, NY, NX, NCOMP
    # but we want NY,NX,NCOMP,NF. We drop NB because no one knows what it is.
    data = np.transpose(h5grid["data"][:, 0, :, :, :], (1, 2, 3, 0))

    griddict = {
        'file_name': str(gridfilepath.resolve()),
        'freqs_Hz': freqs_Hz,
        'ktype': ktype,
        'nset': nset, 
        'icomp': icomp,
        'ncomp': ncomp, 
        'igrid': igrid,
        'beamc': beamc,
        'xlims': xlims,
        'ylims': ylims,
        'nx': nx,
        'ny': ny,
        'klimit': klimit,
        'data': data,
        'xcoords': xcoords,
        'ycoords': ycoords
    }
            
    return griddict

def gather_information(griddict: dict, tordict: dict = {}, userinfo: dict = {}) -> dict:
    """
    Combine data from h5file + torfile/userinfo: dictionary with labels etc.
    """
    
    if tordict:
        # Do something
        return
    elif userinfo:
        # Do something else
        return

    # Collecting info from h5 file itself
    h5grid = h5py.File(griddict["file_name"])
    class_name = h5grid["object"].attrs["class"].decode('utf-8')
    # We want homogenous field names
    field_name = h5grid["object"].attrs["field_type"].decode('utf-8')
    field_name = field_name.lower()
    field_name = field_name.replace(" ", "_")

    field_region_distance_m = h5grid["object"].attrs["field_distance"]
    field_region = h5grid["object"].attrs["field_region"].decode('utf-8')
    polarisation = h5grid["object"].attrs["polarisation"].decode('utf-8').strip('-')
    freqs_Hz = h5grid["parameters"]["frequency"][:]

    # given all the properties: define labels from user manual
    coordinate_system = labels.grid_type[class_name][griddict['igrid']] # e.g. {'name': 'uv', 'coords': ('u', 'v'), 'units': ('m', 'm'), 'tex': ('u', 'v')}
    polarisation = labels.grid_polarisation[class_name][griddict['icomp']][0] # e.g. linear
    field_components_mathnames = labels.grid_polarisation[class_name][griddict['icomp']][1] # e.g. ['E_{co}', 'E_{cx}', 'E_r']
    field_components_mathnames = field_components_mathnames[0:griddict['ncomp']] # e.g. ['E_{co}', 'E_{cx}']
    
    # replace fieldnames
    # surface_grid: e.g. E_{i,\,co} --> H_{r,\,co}
    # all other grids: e.g. E_{co} --> H_{co}
    if class_name == 'surface_grid': 
        if field_name == 'incident_h_field':
            field_components_mathnames = [el.replace(r'E', r'H') for el in field_components_mathnames]
        elif field_name == 'reflected_e_field':
            field_components_mathnames = [el.replace(r'E_{i',r'E_{r') for el in field_components_mathnames]
        elif field_name == 'reflected_h_field':
            field_components_mathnames = [el.replace(r'E_{i',r'E_{r') for el in field_components_mathnames]
            field_components_mathnames = [el.replace(r'E', r'H') for el in field_components_mathnames]
        elif field_name == 'currents':
            field_components_mathnames = [el.replace(r'E_{i,\,', r'J_{') for el in field_components_mathnames]
        else: # field_name == 'incident_e_field'
            pass
    elif field_name == 'h_field': 
            field_components_mathnames = [el.replace(r'E', r'H') for el in field_components_mathnames]
    else: # field_name == 'e_field'
        pass
    
    # determine units of the field components
    field_components_unitsystem, field_components_mathunits = labels.units_of_components(polarisation, field_region)

    # DEBUG CODE REMOVE LATER
    coordinate_system_name = "bla"



    
    # gather all the information
    inputinfodict = {
        'class_name': class_name, # torfile/user (required): e.g. spherical_cut (surface_cut)
        'field_name': field_name, # torfile/user (required): e.g. e_field (incident_e_field)
        'coordinate_system_name': coordinate_system_name, # torfile/user (optional)
        'field_region_distance_m': field_region_distance_m, # torfile/user (optional)
        'freqs_Hz': freqs_Hz} # torfile/user (optional)
    outputinfodict = {
        'coordinate_system': coordinate_system, # icut + class_name --> e.g. spherical_cut: polar, conical -->  {'name': 'polar', 'coords': ('phi', 'theta'), 'units': ('deg', 'deg'), 'tex': ('\\phi', '\\theta')}
        'polarisation': polarisation, # icomp + class_name --> e.g. spherical_cut: linear, total power, ...
        'field_region': field_region, # ncomp / torfile --> near_field / far_field
        'field_components_mathnames': field_components_mathnames, # ncomp + class_name + field_name --> e.g. spherical_cut: ['E_{co}', 'E_{cx}', 'E_r']
        'field_components_unitsystem': field_components_unitsystem, # icomp + class_name (polarisation & field_region) --> e.g. spherical
        'field_components_mathunits': field_components_mathunits} # icomp + class_name (polarisation & field_region)
    infodict = {**inputinfodict,**outputinfodict}

    return infodict
