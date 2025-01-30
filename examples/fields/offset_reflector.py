import os

from pycra import torfile
from pycra.fields import cutfile, gridfile

def main():
    """
    Near- and farfield simulations from offset reflector.
    
    Example:
    --------
    
    directory = './offset_reflector/Job_01'
    torfilepath = os.path.join(directory, 'Job_01.tor')
    gridfilepath = os.path.join(directory, 'spherical_grid_nearfield_uv_H.grd')
    da = gridfile.readgrid(gridfilepath, torfilepath=torfilepath)
    print(gridfile.readgrid.__doc__) # show function docstring
    
    -----------------------------------------------------
    | The dataframe "da" is composed of four parts:     |
    | - "da.name": filename incl. path of the file      |
    | - "da.data": data (4-dimensional array)           |
    | - "da.coords": coordinates that define the data   |
    | - "da.attrs": auxiliary information               |
    -----------------------------------------------------
    
    <xarray.DataArray (Y: 13, X: 11, comp: 3, freq: 1)> Size: 7kB
    array([[[[-6.69461264e-05+2.01470450e-05j],
            [-3.05007701e-06+1.85402436e-04j],
            [ 2.12885169e-05+6.53415092e-05j]],

            [[-2.13894380e-04+2.69500025e-04j],
            [ 1.68635992e-04+7.92198911e-05j],
            [ 3.95888274e-05-6.24646009e-05j]],

            [[-7.37250605e-05-2.75211796e-04j],
            [ 2.33454324e-04-5.07442722e-04j],
            [ 3.02900082e-05+1.70943289e-05j]],

            [[-5.31687278e-04-8.46406556e-05j],
            [ 2.19564966e-04+1.96485166e-04j],
            [ 1.83031378e-04+5.64914078e-05j]],

            [[ 1.16892340e-04+4.80066782e-04j],
            [-5.47063074e-04-1.19707296e-05j],
            [-1.33129009e-04-1.42517642e-04j]],

    ...

            [[-9.21630093e-05+1.12567646e-04j],
            [-5.62696687e-04+2.93190027e-04j],
            [ 1.41687714e-04-1.06508266e-04j]],

            [[-5.19779300e-05+3.54479456e-04j],
            [-2.58416629e-04-3.91071193e-04j],
            [ 3.61595198e-05+3.92024570e-05j]],

            [[-2.69447670e-04+3.17538489e-05j],
            [ 2.33480729e-04+4.46032960e-04j],
            [ 3.01249765e-05-1.01829686e-04j]],

            [[ 4.51522098e-04-9.78500379e-05j],
            [-2.77629041e-04-8.21287052e-05j],
            [-6.34109090e-05+6.43905102e-05j]],

            [[-1.32905570e-03-6.98870742e-04j],
            [-5.35695828e-04-4.99182512e-04j],
            [ 3.30376944e-04+2.53112809e-04j]]]])
    Coordinates:
    * Y        (Y) float64 104B 0.7071 0.5893 0.4714 ... -0.4714 -0.5893 -0.7071
    * X        (X) float64 88B -0.7071 -0.5657 -0.4243 ... 0.4243 0.5657 0.7071
    * comp     (comp) <U1 12B 'a' 'b' 'c'
    * freq     (freq) float64 8B 9.993e+09
    Attributes:
        filename:                 /home/phjschmid/phdphysics/code/projects/pycra/...
        class_name:               spherical_grid
        coordinate_system:        uv
        coordinate_system_name:   single_cut_coor
        field_region:             near
        field_region_distance_m:  1.0

    
    ------------
    | da.attrs |
    ------------
    
    {'filename': '/home/phjschmid/phdphysics/code/projects/pycra/examples/fields/offset_reflector/Job_01/spherical_grid_nearfield_uv_H.grd', 
     'class_name': 'spherical_grid', 'coordinate_system': 'uv', 'coordinate_system_name': 'single_cut_coor', 'field_region': 'near', 'field_region_distance_m': 1.0}
    
    "class_name" (da.attrs['class_name'])
    There are different classes of grids and cuts.
    - grids: spherical_grid, cylindrical_grid, planar_grid, surface_grid
    - cuts: spherical_cut, cylindrical_cut, planar_cut, surface_cut
    
    "coordinate_system" (da.attrs['coordinate_system'])
    There are different types of parametrizations for each class. Examples:
    - For the class "spherical_cut", there are the following types: "polar", "conical"
    - For the class "planar_grid", there are the following types: "rho_phi", "xy".
    - For the class "spherical_grid", there are the following types: "uv", "elevation_over_azimuth", "elevation_and_azimuth", "azimuth_over_elevation", "theta_phi", "azimuth_over_elevation_edx", "elevation_over_azimuth_edx"
    Remark: the cooresponding coordinates are specified under "da.X" and "da.Y" (see below)
    
    "coordinate_system_name" (da.attrs['coordinate_system_name'])
    User-specific name of the coordinate system.
    
    "field_region" (da.attrs['field_region'])
    The coordinate system can refer to the near- or to the farfield.
    - near (all classes)
    - far (only "spherical_cut" and "spherical_grid")
    --> Remark: for the classes "surface_cut" and "surface_grid", 
    
    "field_region_distance_m" (da.attrs['field_region_distance'])
    - numeric (for "surface_cut" and "surface_grid" set to zero)
    - inf (by definition)
    
    -----------
    | da.comp |
    -----------
    
    The components are accessible as follows: da.X, da.Y, da.comp, da.freq
    
    --------
    | da.X | (e.g. the dimensionless coordinate "u" in the coordinate system "uv")
    --------
    
    <xarray.DataArray 'X' (X: 11)> Size: 88B
    array([-7.071068e-01, -5.656854e-01, -4.242641e-01, -2.828427e-01,
        -1.414214e-01, -1.110223e-16,  1.414214e-01,  2.828427e-01,
            4.242641e-01,  5.656854e-01,  7.071068e-01])
    Coordinates:
    * X        (X) float64 88B -0.7071 -0.5657 -0.4243 ... 0.4243 0.5657 0.7071
    Attributes:
        long_name:  co-polar
        texname:    u
        units:      

        
    --------
    | da.Y | (e.g. the dimensionless coordinate "v" in the coordinate system "uv")
    --------
    
    <xarray.DataArray 'Y' (Y: 13)> Size: 104B
    array([ 0.707107,  0.589256,  0.471405,  0.353553,  0.235702,  0.117851,
            0.      , -0.117851, -0.235702, -0.353553, -0.471405, -0.589256,
        -0.707107])
    Coordinates:
    * Y        (Y) float64 104B 0.7071 0.5893 0.4714 ... -0.4714 -0.5893 -0.7071
    Attributes:
        long_name:  cross-polar
        texname:    v
        units:      

    -----------
    | da.comp |
    -----------
    
    <xarray.DataArray 'comp' (comp: 3)> Size: 12B
    array(['a', 'b', 'c'], dtype='<U1')
    Coordinates:
    * comp     (comp) <U1 12B 'a' 'b' 'c'
    Attributes:
        long_name:     field comopnents
        field_type:    h_field
        polarisation:  linear
        names_math:    ['H_{co}', 'H_{cx}', 'H_r']
        units_math:    ['W$^{0.5}$', 'W$^{0.5}$', 'W$^{0.5}$']
        unitsystem:    TICRA
    
    "field_type" (da.comp.attrs['field_type'])
    Depending on the class, there are different types of fields that is evaluated at the above-specified coordinates. 
    See e.g. TICRA-Tools Manual 23.1.0, p. 2144.
    - For the classes "surface_cut" and "surface_grid": 'incident_e_field', 'incident_h_field', 'reflected_e_field', 'reflected_h_field', 'currents'
    - For the other classes: 'e_field', 'h_field'
    
    "polarisation" (da.comp.attrs['polarisation'])
    The fields can have different polarisations. Example:
    For the class "cylindrical_cut" and "cylindrical_grid": "circular", "linear", "major_minor", "circular_xpd", "major_minor_xpd", "power"
    
    -----------
    | da.freq |
    -----------
    
    <xarray.DataArray 'freq' (freq: 1)> Size: 8B
    array([9.993082e+09])
    Coordinates:
    * freq     (freq) float64 8B 9.993e+09
    Attributes:
        long_name:  frequency
        units:      Hz    
        
    """
        
    directory = './offset_reflector/Job_01'
    
    # torfile
    torfilepath = os.path.join(directory, 'Job_01.tor')
    tordict = torfile.tor2dict(torfilepath)
    
    # class_name: spherical_cut
    filepath_spherical_cut_farfield_E = os.path.join(directory, 'spherical_cut_farfield_E.cut')
    filepath_spherical_cut_nearfield_E = os.path.join(directory, 'spherical_cut_nearfield_E.cut')
    filepath_spherical_cut_nearfield_H = os.path.join(directory, 'spherical_cut_nearfield_H.cut')
    
    # class_name: spherical_grid
    filepath_spherical_grid_farfield_thetaphi_E = os.path.join(directory, 'spherical_grid_farfield_thetaphi_E.grd')
    filepath_spherical_grid_nearfield_uv_H = os.path.join(directory, 'spherical_grid_nearfield_uv_H.grd')
    
    # class_name: planar_grid
    filepath_planar_grid_nearfield_front_01_poynting = os.path.join(directory, 'planar_grid_nearfield_front_01_poynting.grd')
    
    # glass_name: surface_grid
    filepath_surface_grid_Hr = os.path.join(directory, 'surface_grid_Hr.grd')
    filepath_surface_grid_I = os.path.join(directory, 'surface_grid_I.grd')
    
    print('------------------------------------------')
    print('Example: spherical_grid_nearfield_uv_H.grd')
    print('------------------------------------------')
    print('\n')
    
    # Method 1: provide torfilepath to gridfile.readgrid (or cutfile.readcut)
    da = gridfile.readgrid(filepath_spherical_grid_nearfield_uv_H, torfilepath=torfilepath)
    print(da)
    print('\n')
    
    # # Method 2: read torfile to dictionary (see above) and provide to gridfile.readgrid (or cutfile.readcut)
    # # If you wish to read several files from the same project (i.e. same .tor file) this is faster,
    # # because the .tor file is read only once.
    # da = gridfile.readgrid(filepath_spherical_grid_nearfield_uv_H, tordict=tordict)
    # print(da)
    # print('\n')
    
    # # Method 3: no torfile available (or suppose there is some error when reading the latter)
    # userinfo = {
    #     'class_name': 'spherical_grid',                 # (required)
    #     'field_name': 'h_field',                        # (required)
    #     'coordinate_system_name': 'single_cut_coor',    # (optional)
    #     'nearfield_distance_m': 1,                      # (optional)
    #     'freqs_Hz': [9993081933.333334]}                # (optional)
    # da = gridfile.readgrid(filepath_spherical_grid_nearfield_uv_H, userinfo=userinfo)
    # print(da)
    # print('\n')
    
    # # Without optional inputs
    # userinfo = {
    #     'class_name': 'spherical_grid',
    #     'field_name': 'h_field'}
    # da = gridfile.readgrid(filepath_spherical_grid_nearfield_uv_H, userinfo=userinfo)
    # print(da)
    # print('\n')
    
    print('--------------------------------------')
    print('Example: spherical_cut_nearfield_E.cut')
    print('--------------------------------------')
    print('\n')
    
    # Method 1: provide torfilepath to gridfile.readgrid (or cutfile.readcut)
    da = cutfile.readcut(filepath_spherical_cut_nearfield_H, torfilepath=torfilepath)
    print(da)
    print('\n')
    
    # # Method 2: ... (similar to above)
    # da = cutfile.readcut(filepath_spherical_cut_nearfield_H, tordict=tordict)
    # print(da)
    # print('\n')
    
    # # Method 3:
    # userinfo = {
    #     'class_name': 'spherical_cut',                  # (required)
    #     'field_name': 'h_field',                        # (required)
    #     'coordinate_system_name': 'single_cut_coor',    # (optional)
    #     'field_region_distance_m': 1,                   # (optional)
    #     'freqs_Hz': [9993081933.333334]}                # (optional)
    # da = cutfile.readcut(filepath_spherical_cut_nearfield_H, userinfo=userinfo)
    # print(da)
    # print('\n')
    
    # userinfo = {
    #     'class_name': 'spherical_cut',
    #     'field_name': 'h_field'}
    # da = cutfile.readcut(filepath_spherical_cut_nearfield_H, userinfo=userinfo)
    # print(da)
    # print('\n')
    
    return

if __name__ == '__main__':
    main()