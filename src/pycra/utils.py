from .labels import CYLINDRICAL_ATTRIBUTES, SPHERICAL_ATTRIBUTES, PLANAR_OR_SURFACE_ATTRIBUTES
import xarray as xr

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


def save(grid_or_cut: xr.DataArray, file_name: str = None) -> None:
    if file_name is None:
        file_name = grid_or_cut.data.name
    grid_or_cut.data.to_netcdf(f"{file_name}.nc")
