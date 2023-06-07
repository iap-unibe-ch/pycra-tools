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
        3: "Ludwig's co and cx",
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
    {  # This is for grid files
        1: "uv-grid",
        4: "elevation over azimuth",
        5: "elevation and azimuth",
        6: "azimuth over elevation",
        7: "theta phi grid",
        9: "azimuth over elevation,edx",
        10: "elevation over azimuth,edx"
    },
    {  # This is for cut files
        1: "radial C=phi V_=theta",
        2: "circular C=theta V_=phi"
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
    {  # This is for grid files
        2: "rho, theta grid",
        3: "x, y grid"
    },
    {  # This is for cut files
        1: "radial C=phi V_=rho",
        2: "circular C=rho V_=theta"
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
    {  # This is for grid files
        8: "Theta, z grid"
    },
    {  # This is for cut files
        1: "axial C=phi V_=z",
        2: "circular C=z V_=phi"
    }
]

GRID_AXIS_LABELS = {
    #   Name, Name, unit, unit, Longname, Longname
    1: ["u", "v", "", "", "U", "V"],
    2: ["Rho", "Theta", "deg", "deg", "$\\rho$", "$\\theta$"],
    3: ["X", "Y", "mm", "mm", "X-axis", "Y-axis"],
    4: ["Az", "El", "deg", "deg", "Azimuth", "Elevation"],
    5: ["Az", "El", "deg", "deg", "Azimuth", "Elevation"],
    6: ["Az", "El", "deg", "deg", "Azimuth", "Elevation"],
    7: ["Phi", "Theta", "deg", "deg", "$\\phi$", "$\\theta$"],
    8: ["Theta", "z", "deg", "mm", "$\\theta$", "Z-distance"],
    9: ["Az", "El", "deg", "deg", "Azimuth", "Elevation"],
    10: ["Az", "El", "deg", "deg", "Azimuth", "Elevation"],
}

COMP_LABELS = {
    1: ["$E_\\theta$", "$E_\phi$"],
    2: ["RHC", "LHC"],
    3: ["Co", "Cross"],
    4: ["Major", "Minor"],
    5: ["$\\frac{E_\\theta}{E_\phi}$", "$\\frac{E_\phi}{E_\\theta}$"],
    6: ["$\\frac{RHC}{LHC}$", "$\\frac{LHC}{RHC}$"],
    7: ["$\\frac{Co}{Cross}$", "$\\frac{Cross}{Co}$"],
    8: ["$\\frac{major}{minor}$", "$\\frac{minor}{major}$"],
    9: ["Total Power", "$\sqrt{\\frac{RHC}{LHC}$"],
    11: ["X Poynting", "Y Poynting", "Z Poynting"],
    51: ["$\sigma_{VV}$", "$\sigma_{VH}$"],
    52: ["$\sigma_{HH}$", "$\sigma_{HV}$"],
    53: ["$\sigma_{VV}$", "$\sigma_{VH}$", "$\sigma_{HH}$", "$\sigma_{HV}$", "$\sigma_{T}$"],
}

CUT_AXIS_LABELS = {
    # grid type: Name, Name, unit, unit, Longname, Longname
    "spherical": ["Theta", "Phi", "deg", "deg", "$\\theta$", "$\phi$"],
    "planar or surface": ["Rho", "Theta", "distance", "deg", "$\\rho$", "$\\theta$"],
    "cylindrical": ["Z", "Phi", "distance", "deg", "Z", "$\\phi$"]
}


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

            attributes, grid_type = check_grid_or_cut_type(icomp, ncomp, igrid, "grid")

            xname, yname, xunit, yunit, xlname, ylname = GRID_AXIS_LABELS[igrid][:]



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

                matrix = np.full(shape=(ny, nx, ncomp), fill_value=np.nan, dtype=complex)

                if klimit == 1:
                    for y in range(ny):
                        Is, In = [int(s) for s in file_grid.readline().split()]
                        Is -= 1
                        for x in range(In):
                            line = file_grid.readline().split()
                            for i in range(0, len(line), 2):
                                matrix[y, Is + x, i // 2] = complex(float(line[i]), float(line[i+1]))
                elif klimit == 0:
                    Is = 1
                    Ie = nx
                    for y in range(ny):
                        for x in range(nx):
                            line = file_grid.readline().split()
                            for i in range(0, len(line), 2):
                                matrix[y, x, i // 2] = complex(float(line[i]), float(line[i+1]))

                else:
                    raise Exception(f"Unknown KLIMIT = {klimit}")


                matrix4d = np.expand_dims(matrix, 3)
                da = xr.DataArray(
                    data=matrix4d,
                    dims=[yname, xname, "comp", "freq"],
                    name=data_name,
                    coords=[ #3D not yet accommodated here
                        (xname, np.linspace(x_limits[0], x_limits[1], nx), {"units": xunit, "long_name": xlname}),
                        (yname, np.linspace(y_limits[0], y_limits[1], ny), {"units": yunit, "long_name": ylname}),
                        ("comp", [COMP_LABELS[icomp][0], COMP_LABELS[icomp][1]], {"long_name": "Field component"}),
                        ("freq", [frequency], {"unit": "GHz"})
                    ],
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

    def power(self, grid_array: xr.DataArray = None) -> List:
        if grid_array is None:
            grid_array = self.data
        power_grid = abs(grid_array)**2
        power_grid = power_grid.sum(dim="comp")
        power_grid.name = "power"
        xy_dims = grid_array.dims[0:2]
        max_db = []
        for frequency in power_grid.freq.values:
            s = power_grid \
                .sel(freq=frequency) \
                .where(power_grid.sel(freq=frequency) == power_grid.sel(freq=frequency).max(dim=xy_dims)
                       , drop=True).squeeze()
            max_db.append(10 * np.log10(s))
        self.data = xr.merge([self.data, power_grid]) #this is not added in dB
        return max_db

    def co_cross(self, grid_array: xr.DataArray = None) -> None:  # MISSING: 3 component processing
        if grid_array is None:
            grid_array = self.data
        max_v = self.power(grid_array)
        complex_E = grid_array.isel(comp=0)
        complex_H = grid_array.isel(comp=1)
        dim_x, dim_y = grid_array.dims[0:2]
        for it in max_v:
            x_max_val = complex_E.sel(freq=it.coords['freq'].values)
            y_max_val = complex_H.sel(freq=it.coords['freq'].values)
            r = np.arctan2(1, np.real(y_max_val / x_max_val))
            v_co = complex_E * np.sin(r) + complex_H * np.cos(r)
            v_cross = complex_E * np.cos(r) - complex_H * np.sin(r)
            # normalise main beam phase to 0 deg wtf does this do
            pr = v_co.isel(np.abs(v_co).argmax(dim=[dim_x, dim_y]))
            # fun fact np.max only looks at real part. MATLAB max looks at abs. value
            pr = np.abs(pr) / pr
            v_co = v_co * pr
            v_cross = v_cross * pr
            co_dB = 20 * np.log10(np.abs(v_co / v_co.isel(np.abs(v_co).argmax(dim=[dim_x, dim_y]))))
            cross_dB = 20 * np.log10(np.abs(v_cross / v_co.isel(np.abs(v_co).argmax(dim=[dim_x, dim_y]))))

        v_co.name = "co_polar"
        v_cross.name = "x_polar"
        co_dB.name = "co_dB"
        cross_dB.name = "x_dB"
        self.data = xr.merge([self.data, v_co, v_cross, co_dB, cross_dB])

    def plotcont(self, grid_array: xr.DataArray) -> tuple[plt.Figure, plt.Axes, contour.ContourSet]:
        fig, ax = plt.subplots()
        #con = grid_array.plot.contour(colors='k', levels=[-30, -20, -10, -6, -3, -0.1], linestyles='solid')
        con = grid_array.plot.contourf(levels=[-30, -20, -10, -6, -3, -0.1])
        ax.set_xlabel(GRID_AXIS_LABELS[int(self.data.igrid[0])][0])
        ax.set_ylabel(GRID_AXIS_LABELS[int(self.data.igrid[0])][1])
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
