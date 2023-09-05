import xarray as xr
import numpy as np
from typing import List
from pathlib import Path
from .labels import COMP_LABELS
from .typecheck import check_grid_or_cut_type

CUT_AXIS_LABELS = {
    # grid type: Name, Name, unit, unit, Longname, Longname
    "spherical": ["Theta", "Phi", "deg", "deg", "$\\theta$", "$\phi$"],
    "planar or surface": ["Rho", "Theta", "distance", "deg", "$\\rho$", "$\\theta$"],
    "cylindrical": ["Z", "Phi", "distance", "deg", "Z", "$\\phi$"]
}

class CutFile:
    def __init__(self, file_names: List[str]) -> None:
        dat_list = []
        for file_name in file_names:
            path = Path(file_name)
            if not path.is_file():
                raise Exception("File not found:" + file_name)

            extension = path.suffix
            match extension:
                case ".cut":
                    dat_list.append(self._read_cut(file_name))
                case ".nc":
                    dat_list.append(xr.open_dataarray(file_name))

        self.data = xr.concat(dat_list, dim="freq", combine_attrs="override")
        for attr in ["filename"]:
            at_list = []
            for ds in dat_list:
                if isinstance(ds.attrs[attr], list):
                    at_list.extend(ds.attrs[attr])
                else:
                    at_list.append(ds.attrs[attr])
            self.data.attrs[attr] = at_list

    def _read_cut(self, file_name: str, data_name: str = None) -> xr.DataArray:  # FIX ICUT DICTIONARY
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

            xname, yname, xunit, yunit, xlname, ylname = CUT_AXIS_LABELS[cut_type][:]
            da = xr.DataArray(
                data=matrix,
                dims=[yname, xname, "comp", "freq"],
                name=data_name,
                coords=[
                    (xname, cut_orientation, {"units": xunit, "long_name": xlname}),
                    (yname, np.linspace(v_ini, (v_num - 1) * v_inc, v_num), {"units": yunit, "long_name": ylname}),
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
