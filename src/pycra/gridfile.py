import xarray as xr
import numpy as np
import matplotlib.contour as contour
from typing import List
from pathlib import Path
from .labels import COMP_LABELS
from .utils import check_grid_or_cut_type

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


def gridfile(file_names: List[str], data_name: str) -> xr.DataArray:
    if data_name is None:
        data_name = file_names[0].split('.')[0]
    dat_list = []
    for file_name in file_names:
        path = Path(file_name)
        if not path.is_file():
            raise Exception("File not found:" + file_name)

        extension = path.suffix
        match extension:
            case ".grd":
                dat_list.append(readgrd(file_name, data_name))
            case ".nc":
                dat_list.append(xr.open_dataarray(file_name))

    if len(dat_list) > 1:
        grid_data = xr.combine_by_coords(dat_list, combine_attrs="drop_conflicts")
    else:
        grid_data = dat_list[0]
    # for attr in ["filename", "source_field", "freq_name"]:
    #     at_list = []
    #     for ds in dat_list:
    #         if isinstance(ds.attrs[attr], list):
    #             at_list.extend(ds.attrs[attr])
    #         else:
    #             at_list.append(ds.attrs[attr])
    #     self.data.attrs[attr] = at_list
    #     self.data.attrs[attr] = at_list
    return grid_data


def readgrd(file_name: str, data_name: str = None) -> xr.DataArray:  # MISSING: 3 component processing
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


def power(grid_array: xr.DataArray) -> xr.DataArray:
    power_grid = abs(grid_array)**2
    power_grid = power_grid.sum(dim="comp")
    power_grid.coords['comp'] = "power"
    # xy_dims = list(grid_array.dims)[0:2]
    # max_db = []
    # for frequency in power_grid.freq.values:
    #     s = power_grid \
    #         .sel(freq=frequency) \
    #         .where(power_grid.sel(freq=frequency) == power_grid.sel(freq=frequency).max(dim=xy_dims)
    #                , drop=True).squeeze()
    #     max_db.append(10 * np.log10(s))
    # Maybe should convert powergrid to dB?
    return power_grid


def co_cross(grid_array: xr.DataArray) -> xr.DataArray:  # MISSING: 3 component processing
    dim_x, dim_y = grid_array.dims[0:2]
    power = np.abs(grid_array) ** 2
    power = power.sum(dim="comp")
    max_val = power.argmax([dim_x, dim_y])
    complex_E = grid_array.isel(comp=0)
    complex_H = grid_array.isel(comp=1)
    x_max_val = complex_E.isel(max_val)
    y_max_val = complex_H.isel(max_val)
    r = np.arctan2(1, np.real(y_max_val / x_max_val))
    v_co = complex_E * np.sin(r) + complex_H * np.cos(r)
    v_cross = complex_E * np.cos(r) - complex_H * np.sin(r)
    # normalise main beam phase to 0 deg wtf does this do
    pol_rot = v_co.isel(np.abs(v_co).argmax(dim=[dim_x, dim_y]))
    # fun fact np.max only looks at real part. MATLAB max looks at abs. value
    pol_rot = np.abs(pol_rot) / pol_rot
    v_co = v_co * pol_rot
    v_cross = v_cross * pol_rot
    co_dB = 20 * np.log10(np.abs(v_co / v_co.isel(np.abs(v_co).argmax(dim=[dim_x, dim_y]))))
    cross_dB = 20 * np.log10(np.abs(v_cross / v_co.isel(np.abs(v_co).argmax(dim=[dim_x, dim_y]))))

    co_dB.coords['pols'] = "co_dB"
    co_dB.name = f'{grid_array.name}_dB'
    cross_dB.coords['pols'] = "x_dB"
    dB_concat = xr.concat([co_dB, cross_dB], dim='pols')
    # grid_processed = xr.merge([grid_array, dB_merge])
    return dB_concat


def plotcont(grid_array: xr.DataArray) -> contour.ContourSet:
    con_handles = []
    for i in grid_array.coords['freq'].values:
        plot_grid = grid_array.sel(freq=i)
        con = plot_grid.plot.contourf(levels=[-70, -60, -50, -40, -30, -20, -10, -6, -3, -0.001])
        con_handles.append(con)
    return con_handles
