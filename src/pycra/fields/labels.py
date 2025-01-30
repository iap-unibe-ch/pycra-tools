polarisation_type_spherical = {
        1: ('theta_phi',        [r'E_\theta', r'E_\phi', r'E_r']),
        2: ('circular',         [r'E_{rhc}', r'E_{lhc}', r'E_r']),
        3: ('linear',           [r'E_{co}', r'E_{cx}', r'E_r']),
        4: ('major_minor',      [r'E_{maj}', r'E_{min}', r'E_r']),
        5: ('theta_phi_xpd',    [r'E_\theta/E_\phi', r'E_\phi/E_\theta', r'E_r']),
        6: ('circular_xpd',     [r'E_{rhc}/E_{lhc}', r'E_{lhc}/E_{rhc}', r'E_r']),
        7: ('linear_xpd',       [r'E_{co}/E_{cx}', r'E_{cx}/E_{co}', r'E_r']),
        8: ('major_minor_xpd',  [r'E_{maj}/E_{min}', r'E_{min}/E_{maj}', r'E_r']),
        9: ('power',            [r'|E|', r'\sqrt{E_{rhc}/E_{lhc}}', r'E_r'])}
        # |E|, 0, Re( \sqrt{E_{rhc}/E_{lhc}} ), Im( \sqrt{E_{rhc}/E_{lhc}} ), Re(E_r), Im(E_r)

polarisation_type_planar = { 
        1: ('rho_phi',          [r'E_\rho', r'E_\phi', r'E_z']),
        2: ('circular',         [r'E_{rhc}', r'E_{lhc}', r'E_z']),
        3: ('linear',           [r'E_{co}', r'E_{cx}', r'E_z']),
        4: ('major_minor',      [r'E_{maj}', r'E_{min}', r'E_z']),
        5: ('rho_phi_xpd',      [r'E_\rho/E_\phi', r'E_\phi/E_\rho', r'E_z']),
        6: ('circular_xpd',     [r'E_{rhc}/E_{lhc}', r'E_{lhc}/E_{rhc}', r'E_z']),
        7: ('linear_xpd',       [r'E_{co}/E_{cx}', r'E_{cx}/E_{co}', r'E_z']),
        8: ('major_minor_xpd',  [r'E_{maj}/E_{min}', r'E_{min}/E_{maj}', r'E_z']),
        9: ('power',            [r'|E|', r'\sqrt{E_{rhc}/E_{lhc}}', r'E_z']),
        11: ('poynting',        [r'P_x', r'P_y', r'P_z'])} # pp. 2133, 3256

polarisation_type_surface = { # similar to planar, but no type 'poynting
        1: ('rho_phi',          [r'E_{i,\,\rho}', r'E_{i,\,\phi}', r'E_{i,\,z}']),
        2: ('circular',         [r'E_{i,\,rhc}', r'E_{i,\,lhc}', r'E_{i,\,z}']),
        3: ('linear',           [r'E_{i,\,co}', r'E_{i,\,cx}', r'E_{i,\,z}']),
        4: ('major_minor',      [r'E_{i,\,maj}', r'E_{i,\,min}', r'E_{i,\,z}']),
        5: ('rho_phi_xpd',      [r'E_{i,\,\rho}/E_{i,\,\phi}', r'E_{i,\,\phi}/E_{i,\,\rho}', r'E_{i,\,z}']),
        6: ('circular_xpd',     [r'E_{i,\,rhc}/E_{i,\,lhc}', r'E_{i,\,lhc}/E_{i,\,rhc}', r'E_{i,\,z}']),
        7: ('linear_xpd',       [r'E_{i,\,co}/E_{i,\,cx}', r'E_{i,\,cx}/E_{i,\,co}', r'E_{i,\,z}']),
        8: ('major_minor_xpd',  [r'E_{i,\,maj}/E_{i,\,min}', r'E_{i,\,min}/E_{i,\,maj}', r'E_{i,\,z}']),
        9: ('power',            [r'|E_{i}|', r'\sqrt{E_{i,\,rhc}/E_{i,\,lhc}}', r'E_{i,\,z}'])}

polarisation_type_cylindrical = {
        2: ('circular',         [r'E_{rhc}', r'E_{lhc}', r'E_\rho']),
        3: ('linear',           [r'E_{co}', r'E_{cx}', r'E_\rho']),
        4: ('major_minor',      [r'E_{maj}', r'E_{min}', r'E_\rho']),
        6: ('circular_xpd',     [r'E_{rhc}/E_{lhc}', r'E_{lhc}/E_{rhc}', r'E_\rho']),
        7: ('linear_xpd',       [r'E_{co}/E_{cx}', r'E_{cx}/E_{co}', r'E_\rho']),
        8: ('major_minor_xpd',  [r'E_{maj}/E_{min}', r'E_{min}/E_{maj}', r'E_\rho']),
        9: ('power',            [r'|E|', r'\sqrt{E_{rhc}/E_{lhc}}', r'E_\rho'])}

# ========================================================
# Field data in cuts
# ========================================================

# --------------------------------------------------------
# cut type (control parameter ICUT)
# --------------------------------------------------------
# Manual: the polar angle "phi" is called "conventional azimuth angle measured in the xy -plane with the x-axis defining phi = 0"
# On the other hand, for spherical grids the manual defines: azimuth = -theta*cos(phi), and elevation = theta*sin(phi) [Ticra-Tools-23.0.0-Manual p. 2111].
# So probably it makes sense to talk about "polar angle" here.

cut_type_radial = {'name': 'radial',     
            'coords': ('polar angle', 'radius'), 
            'coords_math': (r'\phi', r'\rho'),
            'units': ('deg', 'm')}

cut_type_circular = {'name': 'circular',      
            'coords': ('radius', 'polar angle'), 
            'coords_math': (r'\rho', r'\phi'),
            'units': ('m', 'deg')}

cut_type = {

    # Ticra-Tools-23.0.0-Manual p. 2090, 3248
    'spherical_cut' : {
        1: {'name': 'polar', 
            'coords': ('polar angle', 'zenith angle'), 
            'coords_math': (r'\phi', r'\theta'),
            'units': ('deg', 'deg')}, 
        2: {'name': 'conical',      
            'coords': ('zenith angle', 'polar angle'), 
            'coords_math': (r'\theta', r'\phi'),
            'units': ('deg', 'deg')}},

    # Ticra-Tools-23.0.0-Manual p. 2090, 3249
    'planar_cut': {
        1: cut_type_radial,
        2: cut_type_circular},

    # Ticra-Tools-23.0.0-Manual p. 2097, 3250
    'cylindrical_cut': {
        1: {'name': 'axial',      
            'coords': ('polar angle', 'z'), 
            'coords_math': (r'\phi', 'z'),
            'units': ('deg', 'm')},
        2: {'name': 'circular',      
            'coords': ('z', 'polar angle'), 
            'coords_math': ('z', r'\phi'),
            'units': ('m', 'deg')},
    
    # Ticra-Tools-23.0.0-Manual p. 2103, 3249
    'surface_cut': {
        1: cut_type_radial,
        2: cut_type_circular}}
}

# --------------------------------------------------------
# polarisation (control parameter ICOMP)
# --------------------------------------------------------

cut_polarisation = {
    'spherical_cut': polarisation_type_spherical, # Manual 751, 1110
    'planar_cut': polarisation_type_planar, # Manual 759, 1110
    'surface_cut': polarisation_type_surface, # Manual 772, 1110
    'cylindrical_cut': polarisation_type_cylindrical # Manual 766, 1111
}

# ========================================================
# Field data in rectangular grids
# ========================================================

# --------------------------------------------------------
# grid type (control parameter ICUT)
# --------------------------------------------------------

grid_type_xy = {'name': 'xy',     
            'coords': ('x', 'y'), 
            'coords_math': ('x', 'y'),
            'units': ('m', 'm')}

grid_type = {

    # Ticra-Tools-23.0.0-Manual p. 2111-2112, 3255
    'spherical_grid': {
        1: {'name': 'uv', 
            'coords': ('co-polar', 'cross-polar'), 
            'coords_math': ('u', 'v'),
            'units': ('', '')}, 
        4: {'name': 'elevation_over_azimuth', 
            'coords': ('azimuth angle', 'elevation angle'), 
            'coords_math': (r'\phi', r'\theta'),
            'units': ('deg', 'deg')},
        5: {'name': 'elevation_and_azimuth', 
            'coords': ('azimuth angle', 'elevation angle'), 
            'coords_math': (r'\phi', r'\theta'),
            'units': ('deg', 'deg')},
        6: {'name': 'azimuth_over_elevation', 
            'coords': ('azimuth angle', 'elevation angle'), 
            'coords_math': (r'\phi', r'\theta'),
            'units': ('deg', 'deg')},
        7: {'name': 'theta_phi', 
            'coords': ('polar angle', 'zenith angle'), 
            'coords_math': (r'\phi', r'\theta'),
            'units': ('deg', 'deg')},
        9: {'name': 'azimuth_over_elevation_edx', 
            'coords': ('azimuth angle', 'elevation angle'), 
            'coords_math': (r'\phi', r'\theta'),
            'units': ('deg', 'deg')},
        10: {'name': 'elevation_over_azimuth_edx', 
            'coords': ('azimuth angle', 'elevation angle'), 
            'coords_math': (r'\phi', r'\theta'),
            'units': ('deg', 'deg')}},

    # Ticra-Tools-23.0.0-Manual p. 2130, 3256
    'planar_grid': {
        2: {'name': 'rho_phi',     
            'coords': ('radius', 'polar angle'), 
            'coords_math': (r'\rho', r'\phi'),
            'units': ('m', 'deg')},
        3: grid_type_xy},

    # Ticra-Tools-23.0.0-Manual p. 2130, 3256
    'surface_grid': { # p. 3256
        3: grid_type_xy},

    # Ticra-Tools-23.0.0-Manual p. 2130, 3257
    'cylindrical_grid': {
        3: {'name': 'phi_z', # p. 3257      
            'coords': ('azimut angle', 'z'), 
            'coords_math': (r'\phi', 'z'),
            'units': ('deg', 'm')}}

}

# --------------------------------------------------------
# polarisation (control parameter ICOMP)
# --------------------------------------------------------

grid_polarisation = {
    'spherical_grid': polarisation_type_spherical, # Manual 781, 1114
    'planar_grid': polarisation_type_planar, # Manual 797, 1116
    'surface_grid': polarisation_type_surface, # Manual 801, 1116
    'cylindrical_grid': polarisation_type_cylindrical # Manual 804, 1117
}

# --------------------------------------------------------
# units
# --------------------------------------------------------

def units_of_components(polarisation_type, field_region):

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
    units = [r'W$^{0.5}$', r'W$^{0.5}$', r'W$^{0.5}$']
        
    # overwrite quantities where needed
    if polarisation_type.endswith('_xpd'):
        units[0] = ''
        units[1] = ''
    elif polarisation_type == 'power':
        units[1] = ''
    elif polarisation_type == 'poynting': # for planar grids in the nearfield
        unitsystem = 'SI'
        units = [r'W/m$^2$' for _ in units]

    if field_region == 'far':
        units = units[:2]
    elif field_region == 'near':
        pass
    else:
        raise

    return unitsystem, units