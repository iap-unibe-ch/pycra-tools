# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.contour as contour
from typing import List
from pathlib import Path

SPHERICAL_ATTRIBUTES = [
    {
        1: "linear E_theta and E_phi",
        2: "rhc and lhc",
        3: "Ludwigs co and cx",
        4: "major and minor axes",
        5: "xpd E_theta/E_phi and E_phi/E_theta",
        6: "xpd rhc/lhc and lhc/rhc",
        7: "xpd co/cx and cx/co",
        8: "xpd major/minor and minor/major",
        9: "total power and sqrt rhc/lhc",
        51: "RCS: theta_vv and theta_vh",
        52: "RCS: theta_hh and theta_hv",
        53: "RCS: theta_vv, theta_vh, theta_hh, theta_hv and theta_t",
    },
    {
        2: "two field comp",
        3: "three field comp",
        5: "rcs for both polarisations"
    },
    {
        1: "uv-grid",
        4: "elevation over azimuth",
        5: "elevation and azimuth",
        6: "azimuth over elevation",
        7: "theta phi grid",
        9: "azimuth over elevation,edx",
        10: "elevation over azimuth,edx"
    }
]

PLANAR_OR_SURFACE_ATTRIBUTES = [
    {
        1: "linear E_theta and E_phi",
        2: "rhc and lhc",
        3: "Linear along x and y direction",
        4: "major and minor axes",
        5: "xpd E_rho/E_theta and E_theta/E_rho",
        6: "xpd rhc/lhc and lhc/rhc",
        7: "xpd Ex/Ey and Ey/Ex",
        8: "xpd major/minor and minor/major",
        9: "total power and sqrt rhc/lhc",
        11: "Real part of x,y,z poynting vector"
    },
    {
        3: "three field comp",
    },
    {
        2: "rho, theta grid",
        3: "x, y grid"
    }
]

CYLINDRICAL_ATTRIBUTES = [
    {
        2: "rhc and lhc",
        3: "Linear E_theta and E_z",
        4: "major and minor axes",
        6: "rhc/lhc and lhc/rhc",
        7: "E_z/E_theta and E_theta/E_z",
        8: "major/minor and minor/major",
        9: "total power and sqrt rhc/lhc",
    },
    {
        3: "three field comp",
    },
    {
        8: "Theta, z grid"
    }
]

AXIS_LABELS = {
    1: ["u", "v"],
    2: ["Rho", "Theta"],
    3: ["X", "Y"],
    4: ["Azimuth (deg)", "Elevation (deg)"],
    5: ["Azimuth (deg)", "Elevation (deg)"],
    6: ["Azimuth (deg)", "Elevation (deg)"],
    7: ["Phi (deg)", "Theta (deg)"],
    8: ["Theta", "z"],
    9: ["Azimuth (deg)", "Elevation (deg)"],
    10: ["Azimuth (deg)", "Elevation (deg)"]
}


class GridFile:
    def __init__(self, file_names: List[str]) -> None:
        dat_list = []
        for file_name in file_names:
            path = Path(file_name)
            if not path.is_file():
                raise Exception("File not found:" + file_name)

            extension = path.suffix
            match extension:
                case ".grd":
                    dat_list.append(self._read_grid(file_name))
                case ".nc":
                    dat_list.append(xr.open_dataarray(file_name))

        self.data = xr.concat(dat_list, dim="freq", combine_attrs="override")
        for attr in ["filename", "source_field", "freq_name"]:
            at_list = []
            for ds in dat_list:
                if isinstance(ds.attrs[attr], list):
                    at_list.extend(ds.attrs[attr])
                else:
                    at_list.append(ds.attrs[attr])
            self.data.attrs[attr] = at_list

    def _read_grid(self, file_name: str, data_name: str = None) -> xr.DataArray:  # MISSING: 3 component processing
        if data_name is None:
            data_name = file_name.split('.')[0]
        with open(file_name, 'r') as file_grid:
            header = []
            line = file_grid.readline()
            while line[0:4] != "++++":
                header.append(line)
                line = file_grid.readline()

            frequencies = [float(n) for n in header[-1].split()]
            sources = [x.strip()[19:] for x in header[2:-3]]

            ktype = file_grid.readline()
            nset, icomp, ncomp, igrid = [int(s) for s in file_grid.readline().split()]

            # Determining grid type
            if igrid in CYLINDRICAL_ATTRIBUTES[2].keys():
                attributes = CYLINDRICAL_ATTRIBUTES
                grid_type = "cylindrical"
            elif ncomp == 2:
                attributes = SPHERICAL_ATTRIBUTES
                grid_type = "spherical"
            elif ncomp == 3:
                if igrid in PLANAR_OR_SURFACE_ATTRIBUTES[0].keys():
                    attributes = PLANAR_OR_SURFACE_ATTRIBUTES
                    grid_type = "planar or surface"
                elif igrid in SPHERICAL_ATTRIBUTES[0].keys():
                    attributes = SPHERICAL_ATTRIBUTES
                    grid_type = "spherical"
                else:
                    raise Exception(f"Combination of ICOMP, NCOMP, IGRID values invalid/unaccounted for")
            else:
                raise Exception(f"Combination of ICOMP, NCOMP, IGRID values invalid/unaccounted for")

            beamc = []
            for i in range(int(nset)):
                beamc.append([float(s) for s in file_grid.readline().split()])

            list_da = []
            for index, frequency in enumerate(frequencies):
                limits = file_grid.readline().split()
                x_limits = [float(s) for s in limits[0:3:2]]
                y_limits = [float(s) for s in limits[1:4:2]]

                nx, ny, klimit = [int(s) for s in file_grid.readline().split()]

                stpx = (x_limits[1] - x_limits[0]) / (nx - 1)
                stpy = (y_limits[1] - y_limits[0]) / (ny - 1)

                matrix = np.full(shape=(ny, nx, 4), fill_value=np.nan)

                if klimit == 1:
                    for y in range(ny):
                        Is, In = [int(s) for s in file_grid.readline().split()]
                        Is -= 1
                        for x in range(In):
                            line = file_grid.readline().split()
                            matrix[y, Is + x, 0] = float(line[0])
                            matrix[y, Is + x, 1] = float(line[1])
                            matrix[y, Is + x, 2] = float(line[2])
                            matrix[y, Is + x, 3] = float(line[3])
                else:
                    Is = 1
                    Ie = nx
                    for y in range(ny):
                        for x in range(nx):
                            line = file_grid.readline().split()
                            matrix[y, x, 0] = float(line[0])
                            matrix[y, x, 1] = float(line[1])
                            matrix[y, x, 2] = float(line[2])
                            matrix[y, x, 3] = float(line[3])
                matrix4d = np.expand_dims(matrix, 3)
                da = xr.DataArray(
                    data=matrix4d,
                    dims=["ycor", "xcor", "comp", "freq"],
                    name=data_name,
                    coords=dict(
                        xcor=(["xcor"], np.linspace(x_limits[0], x_limits[1], nx)),
                        ycor=(["ycor"], np.linspace(y_limits[0], y_limits[1], ny)),
                        comp=(["comp"], ["E_re", "E_i", "H_re", "H_i"]),
                        freq=(["freq"], [frequency]),
                    ),
                    attrs=dict(
                        filename=file_name,
                        grid_type=grid_type,
                        nset=[nset, "number of field sets or beams"],
                        icomp=[icomp, attributes[0][icomp]],
                        ncomp=[ncomp, attributes[1][ncomp]],
                        igrid=[igrid, attributes[2][igrid]],
                        source_field=sources,
                        freq_name=header[-3].strip()[16:],
                    ),
                )
                list_da.append(da)
        da = xr.concat(list_da, dim="freq")
        return da

    def power(self, grid_array: xr.DataArray = None) -> List:  # MISSING: 3 component processing
        # This is a "shortcut" way of computing the power without having to convert to complex values first
        if grid_array is None:
            grid_array = self.data
        power_grid = grid_array ** 2
        power_grid = power_grid.sum(dim="comp")
        power_grid.name = "power"
        max_db = []
        for frequency in power_grid.freq.values:
            s = power_grid\
                .sel(freq=frequency)\
                .where(power_grid.sel(freq=frequency) == power_grid.sel(freq=frequency).max(dim=["xcor", "ycor"])
                       , drop=True).squeeze()
            max_db.append(10 * np.log10(s))
        xr.merge([self.data, power_grid])
        return max_db

    def co_cross(self, grid_array: xr.DataArray = None) -> None:  # MISSING: 3 component processing
        if grid_array is None:
            grid_array = self.data
        max_v = self.power(grid_array)
        complex_E = grid_array.isel(comp=0) + grid_array.isel(comp=1) * 1j
        complex_H = grid_array.isel(comp=2) + grid_array.isel(comp=3) * 1j
        for it in max_v:
            x_coordinate_values = it.coords['xcor'].values
            y_coordinate_values = it.coords['ycor'].values
            x_max_val = complex_E.sel(xcor=x_coordinate_values, ycor=y_coordinate_values,
                                    freq=it.coords['freq'].values)
            y_max_val = complex_H.sel(xcor=x_coordinate_values, ycor=y_coordinate_values,
                                    freq=it.coords['freq'].values)
            r = np.arctan2(1, np.real(y_max_val / x_max_val))
            v_co = complex_E * np.sin(r) + complex_H * np.cos(r)
            v_cross = complex_E * np.cos(r) - complex_H * np.sin(r)
            # #normalise main beam phase to 0 deg wtf does this do
            pr = v_co.isel(np.abs(v_co).argmax(
                dim=['ycor', 'xcor']))  # fun fact np.max only looks at real part. MATLAB max looks at abs. value
            pr = np.abs(pr) / pr
            v_co = v_co * pr
            v_cross = v_cross * pr
            # add x y z to this function at some point later
            co_dB = 20 * np.log10(np.abs(v_co / v_co.isel(np.abs(v_co).argmax(dim=['ycor', 'xcor']))))
            cross_dB = 20 * np.log10(np.abs(v_cross / v_co.isel(np.abs(v_co).argmax(dim=['ycor', 'xcor']))))

        v_co.name = "co_polar"
        v_cross.name = "x_polar"
        co_dB.name = "co_dB"
        cross_dB.name = "x_dB"
        self.data = xr.merge([self.data, v_co, v_cross, co_dB, cross_dB])

    def plotcont(self, grid_array: xr.DataArray) -> tuple[plt.Figure, plt.Axes, contour.ContourSet]:
        fig, ax = plt.subplots()
        con = grid_array.plot.contour(colors='k', levels=[-30, -20, -10, -6, -3, -0.1], linestyles='solid')
        ax.set_xlabel(AXIS_LABELS[int(self.data.igrid[0])][0])
        ax.set_ylabel(AXIS_LABELS[int(self.data.igrid[0])][1])
        ax.set_title(str(grid_array.freq.item()) + "GHz")
        return fig, ax, con

    def save(self, file_name: str = None) -> None:
        if file_name is None:
            file_name = self.data.name
        self.data.to_netcdf(f"{file_name}.nc")

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

            # Determining cut type
            if icut in CYLINDRICAL_ATTRIBUTES[2].keys():
                attributes = CYLINDRICAL_ATTRIBUTES
                cut_type = "cylindrical"
            elif ncomp == 2:
                attributes = SPHERICAL_ATTRIBUTES
                cut_type = "spherical"
            elif ncomp == 3:
                if icut in PLANAR_OR_SURFACE_ATTRIBUTES[0].keys():
                    attributes = PLANAR_OR_SURFACE_ATTRIBUTES
                    cut_type = "planar or surface"
                elif icut in SPHERICAL_ATTRIBUTES[0].keys():
                    attributes = SPHERICAL_ATTRIBUTES
                    cut_type = "spherical"
                else:
                    raise Exception(f"Combination of ICOMP, NCOMP, ICUT values invalid/unaccounted for")
            else:
                raise Exception(f"Combination of ICOMP, NCOMP, ICUT values invalid/unaccounted for")

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

            matrix = np.full(shape=(no_of_cuts, v_num, 4, no_of_frequencies), fill_value=np.nan)
            for frequency in range(no_of_frequencies):
                for cut in range(no_of_cuts):
                    cut_start = cut * frequency * (v_num + 2)
                    line = lines[1 + cut_start].split()
                    v_ini, v_inc, v_num, c, icomp, icut, ncomp = [float(s) if '.' in s else int(s) for s in line]
                    for index in range(v_num):
                        line = lines[cut_start + index + 2].split()
                        matrix[cut, index, 0, frequency] = float(line[0])
                        matrix[cut, index, 1, frequency] = float(line[1])
                        matrix[cut, index, 2, frequency] = float(line[2])
                        matrix[cut, index, 3, frequency] = float(line[3])

            # matrix = np.expand_dims(matrix, 3)
            da = xr.DataArray(
                data=matrix,
                dims=["cut_rot", "angle", "comp", "freq"],
                name=data_name,
                coords=dict(
                    cut_rot=(["cut_rot"], cut_orientation),
                    angle=(["angle"], np.linspace(v_ini, (v_num - 1) * v_inc, v_num)),
                    comp=(["comp"], ["E_re", "E_i", "H_re", "H_i"]),
                    freq=(["freq"], np.arange(0, no_of_frequencies))
                ),
                attrs=dict(
                    filename=file_name,
                    grid_type=cut_type,
                    # nset=[nset, "number of field sets or beams"],
                    icomp=[icomp, attributes[0][icomp]],
                    ncomp=[ncomp, attributes[1][ncomp]],
                    icut=[icut, attributes[2][icut]],
                    # freq_name=header[-3].strip()[16:],
                ),
            )
        return da
