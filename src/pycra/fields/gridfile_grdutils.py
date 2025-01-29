import re
import pint
import numpy as np
from pathlib import Path

from . import labels
from .. import torfile

def grid2dict_grd(gridfilepath: Path):
    """    
    See GRASP-10.5.0-Manual.pdf p. 1113 for more information:
    KTYPE (integer) - Specifies type of file format. KTYPE = 1 - standard format for 2D grid. For files used in GRASP this variable is always 1.
    NSET - Number of field sets or beams.
    ICOMP - Control parameter of field components.
    NCOMP - Number of components.
    IGRID - Control parameter of field grid type.

    """
    
    ureg = pint.UnitRegistry()
    
    with open(gridfilepath, 'r') as file_grid:

        # --------------------------------------------------------
        # Read information from the header.
        # Notice that this looks different for: 
        # - surface_grid vs. other grid-types
        # - type of frequency/wavelength definition
        #
        # Examples:
        #
        #   VERSION: TICRA-EM-FIELD-V0.1
        #   Field data in grid
        #   SOURCE_FIELD_NAME: single_feed
        #   SOURCE_FIELD_NAME: single_po
        #   FREQUENCY_NAME: single_frequencies
        #   FREQUENCIES [GHz]:
        #   0.1040000000E+02  0.1100000000E+02  0.1160000000E+02
        #   ++++
        #
        #   VERSION: TICRA-EM-FIELD-V0.1
        #   Field data in grid
        #   SOURCE_FIELD_NAME: strut_analysis_arbitrary_cross_01
        #   WAVELENGTH_RANGE_NAME: wavelength_range
        #   WAVELENGTHS [m]:
        #   0.3000000000E-01
        #   ++++
        #
        #   Field data in grid
        #   Field from source single_feed
        #   Field from source single_po
        #   Field from source strut_analysis_arbitrary_cross
        #   Field from source strut_analysis_arbitrary_cross_01
        #   ++++
        # --------------------------------------------------------

        # (1) parse relevant section (header ends with ++++). 
        header = []
        line = file_grid.readline()
        while line[0:4] != "++++":
            header.append(line)
            line = file_grid.readline()
        
        # (2) Store information in different format: 'headerinfo' being a list of tuples. Could look as follows:
        #     [('VERSION', 'TICRA-EM-FIELD-V0.1'), 
        #      ('SOURCE_FIELD_NAME', 'single_feed'), ('FREQUENCY_NAME', 'single_frequencies'), ('FREQUENCIES [GHz]', '0.1160000000E+02  0.1180000000E+02  0.1200000000E+02  0.1220000000E+02'), 
        #      ('SOURCE_FIELD_NAME', 'single_po'), ('FREQUENCY_NAME', 'single_frequencies'), ('FREQUENCIES [GHz]', '  0.1160000000E+02  0.1180000000E+02  0.1200000000E+02  0.1220000000E+02')]
        # headerinfo = re.findall('([^\n]*):\s+?([^\n]*)', ''.join(header))
        # attrs = [info[0] for info in headerinfo]
        # vals = [info[1] for info in headerinfo]
        # source_indice = [ii for ii,attr in enumerate(attrs) if attr.lower() == 'source_field_name']
        # sources = [vals[ii] for ii in source_indice]
        
        # Following ++++ comes more information about type of file format etc.
        # KTYPE = 1 - standard format for 2D grid. For files used in GRASP this variable is always 1.
        # NSET - Number of field sets or beams.
        # ICOMP - Control parameter of field components.
        # NCOMP - Number of components.
        # IGRID - Control parameter of field grid type.
        ktype = int(file_grid.readline().strip())
        nset, icomp, ncomp, igrid = [int(s) for s in file_grid.readline().split()]
        assert ktype == 1

        # (3) extract frequency information if available. Take frequencies from first appearance.
        # Notice that frequencies can be written over several lines (we discovered that every 5th frequency stands on a new line). Example for 5 frequencies:
        # ['VERSION: TICRA-EM-FIELD-V0.1\n', 'Field data in grid\n', 'SOURCE_FIELD_NAME: C1_all_feed\n', 'SOURCE_FIELD_NAME: C2_all_feed\n', 
        #    'SOURCE_FIELD_NAME: C3_all_feed\n', 'SOURCE_FIELD_NAME: C4_all_feed\n', 'FREQUENCY_NAME: C_f_all\n', 
        #    'FREQUENCIES [GHz]:\n', '  0.6665000000E+01  0.6675000000E+01  0.6875000000E+01  0.7075000000E+01\n', '  0.7087000000E+01\n']
        
        max_nrfreqs_per_line = 4
        freq_indice = [ii for ii,attr in enumerate(header) if re.search('(frequencies \[[a-zA-Z]+\]:)',attr.lower())]
        if freq_indice:
            freqs_unit = re.search('\[([a-zA-Z]+)\]', header[freq_indice[0]]).groups()[0]
            nrlines2read = nset//max_nrfreqs_per_line + 1 if nset%max_nrfreqs_per_line>0 else nset//max_nrfreqs_per_line
            freqstr = ' '.join([header[freq_indice[0]+1+ii].strip() for ii in range(nrlines2read)])
            freqs = [float(ff) for ff in freqstr.split()]
            freqs_Hz = [(freq * ureg[freqs_unit]).to('Hz').magnitude for freq in freqs]
        else:
            wavelength_indice = [ii for ii,attr in enumerate(header) if re.search('(wavelengths \[[a-zA-Z]+\]:)',attr.lower())]
            if wavelength_indice:
                speedoflight = 299792458
                wavelengths_unit = re.search('\[([a-zA-Z]+)\]', header[wavelength_indice[0]]).groups()[0]
                nrlines2read = nset//max_nrfreqs_per_line + 1 if nset%max_nrfreqs_per_line>0 else nset//max_nrfreqs_per_line
                freqstr = ' '.join([header[freq_indice[0]+1+ii].strip() for ii in range(nrlines2read)])
                wavelengths = [float(ff) for ff in freqstr.split()]
                wavelengths = [(wavelength * ureg[wavelengths_unit]).to('m').magnitude for wavelength in wavelengths]
                freqs_Hz = [speedoflight / wavelength for wavelength in wavelengths]
            else:
                freqs_Hz = [np.nan]*nset
                print('\n')
                print('No frequency information in grid-file (or error): %s' % gridfilepath)
                print(header)
                print('\n')

        # loop over lines with zeros... (see e.g. TICRA-TOOLS-23.1.0-Manual, p. 3257)
        beamc = [[float(s) for s in file_grid.readline().split()] for _ in range(nset)]
        
        # Read grid information (is repeated later)
        # Limits of 2D grid: xs, ys, xe, ye
        # Nr. of grid values and file structure: nx, ny, klimit
        limits = file_grid.readline().split()
        points = file_grid.readline().split()
        xlims = tuple([float(s) for s in limits[0:3:2]]) # (xs, xe)
        ylims = tuple([float(s) for s in limits[1:4:2]]) # (ys, ye)
        nx, ny, klimit = [int(s) for s in points]

        # build coordinate vectors
        xcoords = np.linspace(*xlims, nx)
        ycoords =  np.linspace(*ylims, ny)[::-1] # reverse the order

        # --------------------------------------------------------
        # Store data into array
        # row coordinates: [ymax, ..., ymin]
        # column coordinates: [xmin, ..., xmax]
        # --------------------------------------------------------

        data = np.full(shape=(ny, nx, ncomp, len(freqs_Hz)), fill_value=complex(np.nan, np.nan), dtype=complex)

        for frequency_index,_ in enumerate(freqs_Hz):

            if frequency_index > 0:

                limits_newfreq = file_grid.readline().split()
                nx_newfreq, ny_newfreq, klimit_newfreq = [int(s) for s in file_grid.readline().split()]
                xlims_newfreq = tuple([float(s) for s in limits_newfreq[0:3:2]])
                ylims_newfreq = tuple([float(s) for s in limits_newfreq[1:4:2]])
                assert nx_newfreq == nx
                assert ny_newfreq == ny
                assert klimit_newfreq == klimit
                assert xlims_newfreq == xlims
                assert ylims_newfreq == ylims

            if klimit != 0:
                raise Exception('KLIMIT != 0: please check code and implement! (Axel line 195)')
            else:
                # klimit=0: read data of rectangular grid
                for y_index in reversed(range(ny)):
                    for x_index in range(nx):
                        line = file_grid.readline().split()
                        values_complex = [complex(float(line[ii]), float(line[ii+1])) for ii in range(0, len(line), 2)]
                        data[y_index, x_index, :, frequency_index] = values_complex                
            
            # if klimit == 1: 
            #     # klimit=1: 2D data is truncated
            #     for y_index in range(ny):
            #         Is, In = [int(s) for s in file_grid.readline().split()]
            #         Is -= 1 # python indexing starts at zero (not at one)
            #         col = [Is + ii for ii in range(In-1)]
            #         for x_index in range(In):
            #             line = file_grid.readline().split()
            #             values_complex = [complex(float(line[ii]), float(line[ii+1])) for ii in range(0, len(line), 2)]
            #             da.data[y_index, x_index, :, frequency_index] = values_complex
            # else:
            #     raise Exception(f'Unknown KLIMIT = {klimit}')

            # # IS - Column number of first data point in row J.
            # # IN - Number of data points in row J
            # if klimit == 0:
            #     Is = 0  # python indexing starts at zero (not at one)
            #     In = nx
            #     # Ie = nx
            # elif klimit == 1:
            #     Is, In = [int(s) for s in file_grid.readline().split()]
            #     Is -= 1 # python indexing starts at zero (not at one)
            #     # # IE = IS+IN-1 (p. 1118)
            # else:
            #     raise Exception(f'Unknown KLIMIT = {klimit}')

            # for y_index in range(ny):
            #     # Axel does that here: 
            #     # Is, In = [int(s) for s in file_grid.readline().split()]
            #     # Is -= 1 # python indexing starts at zero (not at one)
            #     for x_index in range(In):
            #         line = file_grid.readline().split()
            #         values_complex = [complex(float(line[ii]), float(line[ii+1])) for ii in range(0, len(line), 2)]
            #         da.data[y_index, Is + x_index, :, frequency_index] = values_complex
            
    griddict = {
        'file_name': str(gridfilepath.resolve()),
        'freqs_Hz': freqs_Hz,
        'ktype': ktype,
        'nset': nset, 
        'icomp': icomp,
        'ncomp': ncomp, 
        'igrid': igrid,
        'beamc': beamc,
        'xlims': xlims,
        'ylims': ylims,
        'nx': nx,
        'ny': ny,
        'klimit': klimit,
        'data': data,
        'xcoords': xcoords,
        'ycoords': ycoords
    }
    
    return griddict

def gather_information(griddict: dict, tordict: dict = {}, userinfo: dict = {}) -> dict:
    """
    Combine data from gridfile + torfile/userinfo: dictionary with labels etc.
    """
    
    ureg = pint.UnitRegistry()
        
    if tordict:

        gridname = Path(griddict['file_name']).stem
        torinfo = tordict[gridname]
        
        # get class_name ('spherical_grid', ...)
        class_name = torinfo['class_name']     
        
        # field ('e_field', 'h_field', 'reflected_e_field', 'currents', ...)
        if class_name == 'surface_grid':
            field_name = tordict[gridname]['field_type'] if 'field_type' in tordict[gridname].keys() else 'indicent_e_field'
        else:
            field_name = tordict[gridname]['e_h'] if 'e_h' in tordict[gridname].keys() else 'e_field'
        
        # coordinate system ('single_cut_coor', ...)
        coordinate_system_name = torfile.get_coordinate_system_name(torinfo)
        
        # near- vs. farfield
        if class_name in ['planar_grid','surface_grid','cylindrical_grid']:
            field_region = 'near'
        elif 'near_far' in tordict[gridname].keys():
            field_region = tordict[gridname]['near_far'].split(',')[0]
        else: 
            field_region = 'far'
            
        # nearfield distance
        if class_name == 'surface_grid':
            field_region_distance_m = 0.
        elif field_region == 'far':
            field_region_distance_m = np.inf
        else:
            field_region_distance, field_region_distance_units = torfile.get_nearfield_distance(tordict, gridname)
            field_region_distance_m = (field_region_distance * ureg[field_region_distance_units]).to('m').magnitude            
            
        # frequency
        try:
            freqs_Hz_auxiliary = torfile.read_frequencies(tordict, objname=gridname)
            if len(freqs_Hz_auxiliary) != len(griddict['freqs_Hz']):
                print('Error with file: %s' % griddict['file_name'])
                print('Caution! Frequency indications are inconsistent with the computed nr. of frequencies!')
                print('gridfile: %d' % len(griddict['freqs_Hz']))
                print('torfile: %d' % len(freqs_Hz_auxiliary))
                print('Remark: maybe save GRASP project and retry: \
                    (unlike the .cut file, the .tor is exported only when saving)!')
                raise
            elif sum(np.isnan(griddict['freqs_Hz'])>0):
                freqs_Hz = freqs_Hz_auxiliary
            elif freqs_Hz_auxiliary != griddict['freqs_Hz']:
                print('Error with file: %s' % griddict['file_name'])
                print('Caution! Frequencies in grid- and torfile are inconsistent!')
                print('gridfile: %s' % griddict['freqs_Hz'])
                print('torfile: %s' % freqs_Hz_auxiliary)
            else:
                freqs_Hz = freqs_Hz_auxiliary
        except Exception as ee:
            print('Error with file: %s' % griddict['file_name'])
            print('Complete frequency/wavelength reading from torfile.')
            print(ee)
            raise
            
    elif userinfo:
                
        # TICRA TOOLS 23.1.0 p. 2109...
        class_name_options = labels.grid_type.keys() # ['spherical_grid', 'planar_grid', 'cylindrical_grid', 'surface_grid']
        field_name_options = {
            'spherical_grid': ['e_field', 'h_field'],
            'planar_grid': ['e_field', 'h_field'],
            'cylindrical_grid': ['e_field', 'h_field'],
            'surface_grid': ['incident_e_field', 'incident_h_field', 'reflected_e_field', 'reflected_h_field', 'currents']}

        # check user-defined class_name (e.g. 'surface_grid', ...)
        if 'class_name' not in userinfo.keys():
            print('Please provide "class_name":')
            print('Options: %s' % class_name_options)
            raise
        else: 
            class_name = userinfo['class_name']
            if class_name not in class_name_options:
                print('class_name "%s" not in options: %s' % (class_name, class_name_options))
                raise
        
        # check user-defined field_name (e.g. 'reflected_h_field', ...)
        if 'field_name' not in userinfo.keys():
            print('Please provide "field_name":')
            print('Options for %s: %s' % (field_name, field_name_options[class_name]))
            raise
        else: 
            field_name = userinfo['field_name']
            if field_name not in field_name_options[class_name]:
                print('field_name "%s" not in options: %s' % (field_name, field_name_options[class_name]))
                raise
           
        # optional: coordinate system name
        coordinate_system_name = userinfo['coordinate_system_name'] if 'coordinate_system_name' in userinfo.keys() else '???'
        if not (type(coordinate_system_name) is str):
            print('"coordinate_system_name" must be string')
           
        # optional: nearfield distance
        field_region_distance_m = userinfo['field_region_distance_m'] if 'field_region_distance_m' in userinfo.keys() else np.nan        
        if not ((type(field_region_distance_m) is int) | (type(field_region_distance_m) is float)):
            print('"nearfield_distance_m" must be numeric!')
        field_region = 'near' if griddict['ncomp'] > 2 else 'far'
        if class_name == 'surface_cut':
            field_region_distance_m = 0.
        elif (field_region == 'far') & (field_region_distance_m != np.inf):
            print('far-field --> reset field_region_distance_m to infinity') 
            field_region_distance_m = np.inf
        else:
            pass
            
        # frequencies
        if 'freqs_Hz' in userinfo.keys():
            freqs_Hz_auxiliary = userinfo['freqs_Hz']
            if len(freqs_Hz_auxiliary) != len(griddict['freqs_Hz']):
                print('Error with file: %s' % griddict['file_name'])
                print('Caution! Frequency indications are inconsistent with the computed nr. of frequencies!')
                print('gridfile: %d' % len(griddict['freqs_Hz']))
                print('torfile: %d' % len(freqs_Hz_auxiliary))
                print('Remark: maybe save GRASP project and retry: \
                    (unlike the .cut file, the .tor is exported only when saving)!')
                raise
            elif sum(np.isnan(griddict['freqs_Hz'])>0):
                freqs_Hz = freqs_Hz_auxiliary
            elif freqs_Hz_auxiliary != griddict['freqs_Hz']:
                print('Error with file: %s' % griddict['file_name'])
                print('Caution! Frequencies in gridfile and userinput are inconsistent!')
                print('gridfile: %s' % griddict['freqs_Hz'])
                print('userinput: %s' % freqs_Hz_auxiliary)
            else:
                freqs_Hz = freqs_Hz_auxiliary
        else:
            freqs_Hz = griddict['freqs_Hz']
    
    # given all the properties: define labels from user manual
    coordinate_system = labels.grid_type[class_name][griddict['igrid']] # e.g. {'name': 'uv', 'coords': ('u', 'v'), 'units': ('m', 'm'), 'tex': ('u', 'v')}
    polarisation = labels.grid_polarization[class_name][griddict['icomp']][0] # e.g. linear
    field_components_mathnames = labels.grid_polarization[class_name][griddict['icomp']][1] # e.g. ['E_{co}', 'E_{cx}', 'E_r']
    field_components_mathnames = field_components_mathnames[0:griddict['ncomp']] # e.g. ['E_{co}', 'E_{cx}']
    
    # replace fieldnames
    # surface_grid: e.g. E_{i,\,co} --> H_{r,\,co}
    # all other grids: e.g. E_{co} --> H_{co}
    if class_name == 'surface_grid': 
        if field_name == 'incident_h_field':
            field_components_mathnames = [el.replace('E', 'H') for el in field_components_mathnames]
        elif field_name == 'reflected_e_field':
            field_components_mathnames = [el.replace('E_{i','E_{r') for el in field_components_mathnames]
        elif field_name == 'reflected_h_field':
            field_components_mathnames = [el.replace('E_{i','E_{r') for el in field_components_mathnames]
            field_components_mathnames = [el.replace('E', 'H') for el in field_components_mathnames]
        elif field_name == 'currents':
            field_components_mathnames = [el.replace('E_{i,\,', 'J_{') for el in field_components_mathnames]
        else: # field_name == 'incident_e_field'
            pass
    elif field_name == 'h_field': 
            field_components_mathnames = [el.replace('E', 'H') for el in field_components_mathnames]
    else: # field_name == 'e_field'
        pass
    
    # determine units of the field components
    field_components_unitsystem, field_components_mathunits = labels.units_of_components(polarisation, field_region)
    
    # gather all the information
    inputinfodict = {
        'class_name': class_name, # torfile/user (required): e.g. spherical_cut (surface_cut)
        'field_name': field_name, # torfile/user (required): e.g. e_field (incident_e_field)
        'coordinate_system_name': coordinate_system_name, # torfile/user (optional)
        'field_region_distance_m': field_region_distance_m, # torfile/user (optional)
        'freqs_Hz': freqs_Hz} # torfile/user (optional)
    outputinfodict = {
        'coordinate_system': coordinate_system, # icut + class_name --> e.g. spherical_cut: polar, conical -->  {'name': 'polar', 'coords': ('phi', 'theta'), 'units': ('deg', 'deg'), 'tex': ('\\phi', '\\theta')}
        'polarisation': polarisation, # icomp + class_name --> e.g. spherical_cut: linear, total power, ...
        'field_region': field_region, # ncomp / torfile --> near_field / far_field
        'field_components_mathnames': field_components_mathnames, # ncomp + class_name + field_name --> e.g. spherical_cut: ['E_{co}', 'E_{cx}', 'E_r']
        'field_components_unitsystem': field_components_unitsystem, # icomp + class_name (polarisation & field_region) --> e.g. spherical
        'field_components_mathunits': field_components_mathunits} # icomp + class_name (polarisation & field_region)
    infodict = {**inputinfodict,**outputinfodict}

    return infodict