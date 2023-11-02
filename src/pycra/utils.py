from .labels import CYLINDRICAL_ATTRIBUTES, SPHERICAL_ATTRIBUTES, PLANAR_OR_SURFACE_ATTRIBUTES
import xarray as xr
import numpy as np


def check_grid_or_cut_type(icomp: int, ncomp: int, ival: int, ftype: str) -> [dict, str]:
    # Determining what type of cut or grid file is being processed
    if ival in CYLINDRICAL_ATTRIBUTES[2].keys():
        attributes = CYLINDRICAL_ATTRIBUTES
        grid_type = "cylindrical"
    elif ncomp == 2:
        attributes = SPHERICAL_ATTRIBUTES
        grid_type = "spherical"
    elif ncomp == 3:
        if ival in PLANAR_OR_SURFACE_ATTRIBUTES[0].keys():
            attributes = PLANAR_OR_SURFACE_ATTRIBUTES
            grid_type = "planar or surface"
        elif ival in SPHERICAL_ATTRIBUTES[0].keys():
            attributes = SPHERICAL_ATTRIBUTES
            grid_type = "spherical"
        else:
            raise Exception(f"Combination of ICOMP = {icomp}, NCOMP = {ncomp}, I{ftype.upper()}\
             values invalid/unaccounted for")
    else:
        raise Exception(f"Combination of ICOMP = {icomp}, NCOMP = {ncomp}, I{ftype.upper()}\
             values invalid/unaccounted for")
    return attributes, grid_type


def db_norm(array: xr.DataArray) -> xr.DataArray:
    if str(array.coords['comp'].values) == "power":
        db_array = 10 * np.log10(np.abs(array))
        print("power array detected")
    else:
        db_array = 20 * np.log10(np.abs(array))
    max_vals = []
    if np.size(db_array.freq) > 1:
        for i in db_array.freq:
            mval = db_array.sel(freq=i).max(dim=db_array.dims[0:2])
            db_array.loc[{'freq': i}] = db_array.sel(freq=i) - mval.max()
            # mval is also a DataArray, so we need extract the values which are a numpy array and convert them to a
            # list.
            max_vals.append(mval.values.tolist())
    else:
        max_vals = db_array.max(dim=db_array.dims[0:2])
        db_array = db_array - max_vals.max()
        max_vals = max_vals.values.tolist()
    db_array.name = f'{array.name}_dB'
    db_array.attrs["units"] = "dB"
    db_array.attrs["long_name"] = "Normalised directivity"
    db_array.attrs["peak_gain"] = max_vals
    db_array = db_array.assign_attrs(array.attrs)
    return db_array


def decibel(array: xr.DataArray) -> xr.DataArray:
    if str(array.coords['comp'].values) == "power":
        db_array = 10 * np.log10(np.abs(array))
        print("power array detected")
    else:
        db_array = 20 * np.log10(np.abs(array))
    max_vals = []
    if np.size(db_array.freq) > 1:
        for i in db_array.freq:
            mval = db_array.sel(freq=i).max(dim=db_array.dims[0:2])
            # mval is also a DataArray, so we need extract the values which are a numpy array and convert them to a
            # list.
            max_vals.append(mval.values.tolist())
    else:
        max_vals = db_array.max(dim=db_array.dims[0:2])
        max_vals = max_vals.values.tolist()
    db_array.name = f'{array.name}_dB'
    db_array.attrs["units"] = "dB"
    db_array.attrs["long_name"] = "Directivity"
    db_array.attrs["peak_gain"] = max_vals
    db_array = db_array.assign_attrs(array.attrs)
    return db_array


def save(grid_or_cut: xr.DataArray, file_name: str = None) -> None:
    if file_name is None:
        file_name = grid_or_cut.data.name
    grid_or_cut.data.to_netcdf(f"{file_name}.nc")
