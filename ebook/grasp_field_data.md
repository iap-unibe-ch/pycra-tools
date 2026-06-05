# GRASP field data
Field data from the TICRA\'s *General Reflector Antenna Software Package* (GRASP) can be stored in the following formats:
- GRASP field data in cuts: `.cut`
- GRASP field data in grids: `.grd` / `.h5`

To correctly interpret the numerical data, additional information is needed. 
This information can be retrieved from the `.tor` file associated with the project, or can be passed via dictionary `{userinfo}` by the user.
The pycra-tools package gathers the information, and returns an [Xarray](https://docs.xarray.dev/en/stable/) labeled multi-dimensional array. 
Say **da** is the name of the resulting dataframe. It has the following attributes:

- **da.attrs['class_name']**: Fundamentally, there is different *classes* of cuts and grids:\
`spherical`, `cylindrical`, `planar`, `surface`, and `RCS` (not implemented).\
The different classes class has several attributes. Important distinctions are the following.
- **da.attrs['coordinate_system']** ({cite}`ticra_tools_2024` manual: *cut_type*, *grid_type*): Depending on the class, different *types* of coordinate systems are eligible. The options differ between cuts and grids (see subsections below), e.g. `polar` (only cuts) and `uv` (only grids).
- **da.comp.attrs['field_type']** ({cite}`ticra_tools_2024` manual: *e_h*, *field_type*): Depending on the class, different kinds of fields can be evaluated. For instance:
    - `spherical`: e_field, h_field
    - `cylindrical`: e_field, h_field
    - `planar`: e_field, h_field
    - `surface`: incident_e_field, incident_h_field, reflected_e_field, reflected_h_field, currents
    - `RCS` (not implemented)
- **da.comp.attrs['polarisation']**: Depending on the class, different kinds of *polarization* can be chosen to parameterise the fields. For instance:
    - `spherical`: theta_phi, circular, linear, major_minor, theta_phi_xpd, circular_xpd, linear_xpd, major_minor_xpd, power
    - `cylindrical`: circular, linear, major_minor, circular_xpd, major_minor_xpd, power
    - `planar`: rho_phi, circular, linear, major_minor, rho_phi_xpd, circular_xpd, linear_xpd, major_minor_xpd, power, poynting
    - `surface`: rho_phi, circular, linear, major_minor, rho_phi_xpd, circular_xpd, linear_xpd, major_minor_xpd, power
    - `RCS` (not implemented)
- **da.attrs['field_region']** ({cite}`ticra_tools_2024` manual: *near_far*): Depending on the class, the fields can be evaluated in the `near`-field (all classes), or in the `far`-field (only for spherical cuts and grids).

Additional attributes are useful to :
- **da.attrs['coordinate_system_name']** ({cite}`ticra_tools_2024` manual: *coor_sys*): The name of the coordinate system.
- **da.attrs['field_region_distance_m']** ({cite}`ticra_tools_2024` manual: *near_dist*): Radius of the near-field sphere.

## GRASP field data in cuts: `.cut`
The different cut *classes* allow the following coordinate system *types*:
- `spherical`: polar, conical
- `cylindrical`: axial, circular
- `planar`: radial, circular
- `surface`: radial, circular
- `RCS` (not implemented)

Complementary information can be provided by the user as follows:
```python
userinfo = {
        'class_name': 'spherical_cut',                  # (required)
        'field_name': 'e_field',                        # (required)
        'coordinate_system_name': 'single_cut_coor',    # (optional)
        'field_region_distance_m': 1,                   # (optional)
        'freqs_Hz': [9993081933.333334]                 # (optional)
}
```

```{bibliography}
```

## GRASP field data in grids: `.grd` / `.h5`
The different grid *classes* allow the following coordinate system *types*:
- `spherical`: uv, elevation_over_azimuth, elevation_and_azimuth, azimuth_over_elevation, theta_phi, azimuth_over_elevation_edx, elevation_over_azimuth_edx
- `cylindrical`: phi_z
- `planar`: rho_phi, xy
- `surface`: xy
- `RCS` (not implemented)

### `.grd` file format
TICRA\'s classical data format used for storing field values in a rectangular grid. 
Complementary information can be provided by the user as follows:
```python
userinfo = {
    'class_name': 'spherical_grid',                 # (required)
    'field_name': 'h_field',                        # (required)
    'coordinate_system_name': 'single_cut_coor',    # (optional)
    'field_region_distance_m': 1,                   # (optional)
    'freqs_Hz': [9993081933.333334]                 # (optional)
}
```

### `.h5` file format
Data storage option with which the generated files have reduced size compared to `.grd` files.


