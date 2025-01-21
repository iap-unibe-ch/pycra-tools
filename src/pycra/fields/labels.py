# each class has the following characteristics:
# - cut/grid type (igrid/icut)
# - polarization (icomp)

polarization_type_spherical = {
        1: ('theta_phi',        ['E_\\theta', 'E_\\phi', 'E_r']),
        2: ('circular',         ['E_{rhc}', 'E_{lhc}', 'E_r']),
        3: ('linear',           ['E_{co}', 'E_{cx}', 'E_r']),
        4: ('major_minor',      ['E_{maj}', 'E_{min}', 'E_r']),
        5: ('theta_phi_xpd',    ['E_\\theta/E_\\phi', 'E_\\phi/E_\\theta', 'E_r']),
        6: ('circular_xpd',     ['E_{rhc}/E_{lhc}', 'E_{lhc}/E_{rhc}', 'E_r']),
        7: ('linear_xpd',       ['E_{co}/E_{cx}', 'E_{cx}/E_{co}', 'E_r']),
        8: ('major_minor_xpd',  ['E_{maj}/E_{min}', 'E_{min}/E_{maj}', 'E_r']),
        9: ('power',            ['|E|', '\sqrt{E_{rhc}/E_{lhc}}', 'E_r'])}
        # |E|, 0, Re( \sqrt{E_{rhc}/E_{lhc}} ), Im( \sqrt{E_{rhc}/E_{lhc}} ), Re(E_r), Im(E_r)

polarization_type_planar = { 
        1: ('rho_phi',          ['E_\\rho', 'E_\\phi', 'E_z']),
        2: ('circular',         ['E_{rhc}', 'E_{lhc}', 'E_z']),
        3: ('linear',           ['E_{co}', 'E_{cx}', 'E_z']),
        4: ('major_minor',      ['E_{maj}', 'E_{min}', 'E_z']),
        5: ('rho_phi_xpd',      ['E_\\rho/E_\\phi', 'E_\\phi/E_\\rho', 'E_z']),
        6: ('circular_xpd',     ['E_{rhc}/E_{lhc}', 'E_{lhc}/E_{rhc}', 'E_z']),
        7: ('linear_xpd',       ['E_{co}/E_{cx}', 'E_{cx}/E_{co}', 'E_z']),
        8: ('major_minor_xpd',  ['E_{maj}/E_{min}', 'E_{min}/E_{maj}', 'E_z']),
        9: ('power',            ['|E|', '\sqrt{E_{rhc}/E_{lhc}}', 'E_z']),
        11: ('poynting',        ['P_x', 'P_y', 'P_z'])} # pp. 2133, 3256

polarization_type_surface = { # similar to planar, but no type 'poynting
        1: ('rho_phi',          ['E_{i,\,\\rho}', 'E_{i,\,\\phi}', 'E_{i,\,z}']),
        2: ('circular',         ['E_{i,\,rhc}', 'E_{i,\,lhc}', 'E_{i,\,z}']),
        3: ('linear',           ['E_{i,\,co}', 'E_{i,\,cx}', 'E_{i,\,z}']),
        4: ('major_minor',      ['E_{i,\,maj}', 'E_{i,\,min}', 'E_{i,\,z}']),
        5: ('rho_phi_xpd',      ['E_{i,\,\\rho}/E_{i,\,\\phi}', 'E_{i,\,\\phi}/E_{i,\,\\rho}', 'E_{i,\,z}']),
        6: ('circular_xpd',     ['E_{i,\,rhc}/E_{i,\,lhc}', 'E_{i,\,lhc}/E_{i,\,rhc}', 'E_{i,\,z}']),
        7: ('linear_xpd',       ['E_{i,\,co}/E_{i,\,cx}', 'E_{i,\,cx}/E_{i,\,co}', 'E_{i,\,z}']),
        8: ('major_minor_xpd',  ['E_{i,\,maj}/E_{i,\,min}', 'E_{i,\,min}/E_{i,\,maj}', 'E_{i,\,z}']),
        9: ('power',            ['|E_{i}|', '\sqrt{E_{i,\,rhc}/E_{i,\,lhc}}', 'E_{i,\,z}'])}

polarization_type_cylindrical = {
        2: ('circular',         ['E_{rhc}', 'E_{lhc}', 'E_\\rho']),
        3: ('linear',           ['E_{co}', 'E_{cx}', 'E_\\rho']),
        4: ('major_minor',      ['E_{maj}', 'E_{min}', 'E_\\rho']),
        6: ('circular_xpd',     ['E_{rhc}/E_{lhc}', 'E_{lhc}/E_{rhc}', 'E_\\rho']),
        7: ('linear_xpd',       ['E_{co}/E_{cx}', 'E_{cx}/E_{co}', 'E_\\rho']),
        8: ('major_minor_xpd',  ['E_{maj}/E_{min}', 'E_{min}/E_{maj}', 'E_\\rho']),
        9: ('power',            ['|E|', '\sqrt{E_{rhc}/E_{lhc}}', 'E_\\rho'])}

# ========================================================
# Field data in cuts
# ========================================================

# --------------------------------------------------------
# cut type (control parameter ICUT)
# --------------------------------------------------------

cut_type_radial = {'name': 'radial',      
            'coords': ('phi', 'rho'), 
            'units': ('deg', 'm'), 
            'coords_math': ('\\phi', '\\rho'),
            'units_math': ('$^\\circ$', 'm')}

cut_type_circular = {'name': 'circular',      
            'coords': ('rho', 'phi'), 
            'units': ('m', 'deg'), 
            'coords_math': ('\\rho', '\\phi'),
            'units_math': ('m','$^\\circ$')}

cut_type = {

    # Manual 750, 1109
    'spherical_cut' : {
        1: {'name': 'polar', 
            'coords': ('phi', 'theta'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\phi', '\\theta'),
            'units_math': ('$^\\circ$', '$^\\circ$')}, 
        2: {'name': 'conical',      
            'coords': ('theta', 'phi'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\theta', '\\phi'),
            'units_math': ('$^\\circ$', '$^\\circ$')}},

    # Manual 758, 1110
    'planar_cut': {
        1: cut_type_radial,
        2: cut_type_circular},

    # Manual 771, 1110
    'surface_cut': {
        1: cut_type_radial,
        2: cut_type_circular},

    # Manual 765, 1111
    'cylindrical_cut': {
        1: {'name': 'axial',      
            'coords': ('phi', 'z'), 
            'units': ('deg', 'm'), 
            'coords_math': ('\\phi', 'z'),
            'units_math': ('$^\\circ$', 'm')},
        2: {'name': 'cylindrical',      
            'coords': ('z', 'phi'), 
            'units': ('m', 'deg'), 
            'coords_math': ('z', '\\phi'),
            'units_math': ('m', '$^\\circ$')}}
}

# --------------------------------------------------------
# polarization (control parameter ICOMP)
# --------------------------------------------------------

cut_polarization = {
    'spherical_cut': polarization_type_spherical, # Manual 751, 1110
    'planar_cut': polarization_type_planar, # Manual 759, 1110
    'surface_cut': polarization_type_surface, # Manual 772, 1110
    'cylindrical_cut': polarization_type_cylindrical # Manual 766, 1111
}

# ========================================================
# Field data in rectangular grids
# ========================================================

# --------------------------------------------------------
# grid type (control parameter ICUT)
# --------------------------------------------------------

grid_type_xy = {'name': 'xy',     
            'coords': ('x', 'y'), 
            'units': ('m', 'm'), 
            'coords_math': ('x', 'y'),
            'units_math': ('m', 'm')}

grid_type = {

    # Manual 779, 1115
    'spherical_grid': {
        1: {'name': 'uv', 
            'coords': ('u', 'v'), 
            'units': ('', ''), 
            'coords_math': ('u', 'v'),
            'units_math': ('', '')}, 
        4: {'name': 'elevation_over_azimuth', 
            'coords': ('az', 'el'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\text{azimuth}', '\\text{elevation}'),
            'units_math': ('$^\\circ$', '$^\\circ$')}, ##
        5: {'name': 'elevation_and_azimuth', 
            'coords': ('az', 'el'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\text{azimuth}', '\\text{elevation}'),
            'units_math': ('$^\\circ$', '$^\\circ$')}, ##
        6: {'name': 'azimuth_over_elevation', 
            'coords': ('az', 'el'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\text{azimuth}', '\\text{elevation}'),
            'units_math': ('$^\\circ$', '$^\\circ$')}, ##
        7: {'name': 'theta_phi', 
            'coords': ('phi', 'theta'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\phi', '\\theta'),
            'units_math': ('$^\\circ$', '$^\\circ$')}, 
        9: {'name': 'azimuth_over_elevation_edx', 
            'coords': ('az', 'el'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\text{azimuth}', '\\text{elevation}'),
            'units_math': ('$^\\circ$', '$^\\circ$')}, ##
        10: {'name': 'elevation_over_azimuth_edx', 
            'coords': ('az', 'el'), 
            'units': ('deg', 'deg'), 
            'coords_math': ('\\text{azimuth}', '\\text{elevation}'),
            'units_math': ('$^\\circ$', '$^\\circ$')}}, ##

    # Manual 797, 1116
    'planar_grid': {
        2: {'name': 'rho_phi',     
            'coords': ('rho', 'phi'), 
            'units': ('m', 'deg'), 
            'coords_math': ('\\rho', '\\phi'),
            'units_math': ('m', '$^\\circ$')},
        3: grid_type_xy},

    # Manual (808), 1116
    'surface_grid': {
        3: grid_type_xy},

    # Manual (802), 1116
    'cylindrical_grid': {
        3: grid_type_xy}

}

# --------------------------------------------------------
# polarization (control parameter ICOMP)
# --------------------------------------------------------

grid_polarization = {
    'spherical_grid': polarization_type_spherical, # Manual 781, 1114
    'planar_grid': polarization_type_planar, # Manual 797, 1116
    'surface_grid': polarization_type_surface, # Manual 801, 1116
    'cylindrical_grid': polarization_type_cylindrical # Manual 804, 1117
}

# --------------------------------------------------------
# units
# --------------------------------------------------------

def units_of_components(polarization_type, field_region):

    # # initialize quantities
    # if field_region == 'far':
    #     unitsystem = 'SI'
    #     if field_name == 'e_field':
    #         fieldunit = 'V/m'
    #     elif field_name == 'h_field':
    #         fieldunit = 'A/m'
    #     else:
    #         raise
    #     units = [fieldunit, fieldunit]
    # else:

    unitsystem = 'TICRA'
    units = ['W^0.5', 'W^0.5', 'W^0.5']
        
    # overwrite quantities where needed
    if polarization_type.endswith('_xpd'):
        units[0] = ''
        units[1] = ''
    elif polarization_type == 'power':
        units[1] = ''
    elif polarization_type == 'poynting': # for planar grids in the nearfield
        unitsystem = 'SI'
        units = ['W/m^2' for _ in units]

    if field_region == 'far':
        units = units[:2]
    elif field_region == 'near':
        pass
    else:
        raise

    return unitsystem, units