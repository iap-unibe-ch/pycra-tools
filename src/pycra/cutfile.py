import xarray as xr
import numpy as np
from typing import List
from pathlib import Path
from xarray import DataArray, Dataset
import matplotlib.pyplot as plt

from .labels import COMP_LABELS
from .utils import check_grid_or_cut_type

CUT_AXIS_LABELS = {
    # grid type: Name, Name, unit, unit, Longname, Longname
    "spherical": ["Theta", "Phi", "deg", "deg", "$\\theta$", "$\phi$"],
    "planar or surface": ["Rho", "Theta", "distance", "deg", "$\\rho$", "$\\theta$"],
    "cylindrical": ["Z", "Phi", "distance", "deg", "Z", "$\\phi$"]
}


def cutfile(file_names: List[str], data_name: str) -> DataArray:
    if data_name is None:
        data_name = file_names[0].split('.')[0]
    dat_list = []
    for file_name in file_names:
        path = Path(file_name)
        if not path.is_file():
            raise Exception("File not found:" + file_name)

        extension = path.suffix
        match extension:
            case ".cut":
                dat_list.append(readcut(file_name, data_name))
            case ".nc":
                dat_list.append(xr.open_dataarray(file_name))

    if len(dat_list) > 1:
        cut_data = xr.combine_by_coords(dat_list, combine_attrs="drop_conflicts")
    else:
        cut_data = dat_list[0]
    return cut_data


def readcut(file_name: str, data_name: str = None) -> xr.DataArray:  # FIX ICUT DICTIONARY
    if data_name is None:
        data_name = file_name.split('.')[0]
    with open(file_name, 'r') as file_cut:
        lines = file_cut.readlines()
        line = lines[1].split()
        _, _, v_num, _, icomp, icut, ncomp = [float(s) if '.' in s else int(s) for s in line]

        attributes, cut_type = check_grid_or_cut_type(icomp, ncomp, icut, "cut")

        no_of_cuts = len(lines) // (v_num + 2)
        cut_orientation = []
        for cut in range(no_of_cuts):
            cut_start = cut * (v_num + 2)
            line = lines[1 + cut_start].split()
            _, _, _, c, _, _, _, = [float(s) if '.' in s else int(s) for s in line]
            cut_orientation.append(c)
        # The cut file format does not tell us how many frequencies there are in the file, so we need to improvise
        duplicate_free = set(cut_orientation)
        no_of_frequencies = len(cut_orientation) // len(duplicate_free)
        if no_of_frequencies != 1:
            cut_orientation = list(set(cut_orientation))
            no_of_cuts = no_of_cuts // no_of_frequencies

        matrix = np.full(shape=(no_of_cuts, v_num, ncomp, no_of_frequencies), fill_value=np.nan, dtype=complex)
        for frequency in range(no_of_frequencies):
            for cut in range(no_of_cuts):
                cut_start = cut * frequency * (v_num + 2)
                line = lines[1 + cut_start].split()
                v_ini, v_inc, v_num, c, icomp, icut, ncomp = [float(s) if '.' in s else int(s) for s in line]
                for index in range(v_num):
                    line = lines[cut_start + index + 2].split()
                    for i in range(0, len(line), 2):
                        matrix[cut, index, i // 2] = complex(float(line[i]), float(line[i + 1]))

        xname, rot_name, xunit, rot_unit, xlname, rot_lname = CUT_AXIS_LABELS[cut_type][:]
        da = xr.DataArray(
            data=matrix,
            dims=[rot_name, xname, "comp", "freq"],
            name=data_name,
            coords=[
                (rot_name, cut_orientation, {"units": rot_unit, "long_name": rot_lname}),
                (xname, np.linspace(v_ini, (v_num - 1) * v_inc, v_num), {"units": xunit, "long_name": xlname}),
                ("comp", [COMP_LABELS[icomp][0], COMP_LABELS[icomp][1]], {"long_name": "Field component"}),
                ("freq", np.arange(0, no_of_frequencies))
            ],
            attrs=dict(
                filename=file_name,
                cut_type=cut_type,
                n_of_f=[no_of_frequencies, "number of frequencies"],
                icomp=[icomp, attributes[0][icomp]],
                ncomp=[ncomp, attributes[1][ncomp]],
                icut=[icut, attributes[2][icut]],
                # freq_name=header[-3].strip()[16:],
            ),
        )
    return da


def decibel(cut_array: xr.DataArray) -> Dataset:
    db_array = 20*np.log10(np.abs(cut_array))
    db_array.name = "db"
    db_array.attrs["units"] = "dB"
    db_array.attrs["long_name"] = "Directivity"
    db_array_normalised = 20*np.log10(np.abs(cut_array)/np.abs(cut_array.sel(comp='Co')).max(cut_array.dims[1]))
    db_array_normalised.name = "db0"
    db_array_normalised.attrs["units"] = "dB"
    db_array_normalised.attrs["long_name"] = "Normalised directivity"
    db_merged = xr.merge([db_array, db_array_normalised])
    return db_merged


def plotcut(cut_array: xr.DataArray):
    # versioning comment5
    return