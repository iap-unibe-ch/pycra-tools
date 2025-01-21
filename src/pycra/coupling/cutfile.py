import re
import numpy as np
import xarray as xr
from pathlib import Path

from .. import torfile

def readcut(cutfilepath: str, torfilepath: str = '', tordict: dict = {}) -> xr.DataArray:
    """
    
    Example
    -------
    
    from pycra import torfile
    from pycra.coupling import cutfile
    
    # define directory where the data is stored
    directory = './coupling_and_plate/Job_01'
    
    # define field-data
    cutfilepath = os.path.join(directory, 'coupling_system_horn2.cut')
    
    # define torfile
    torfilepath = os.path.join(directory, 'Job_01.tor')
    
    # ev. read torfile (faster when several files shall be read)
    tordict = torfile.tor2dict(torfilepath)
    
    # Read the field-data. The following two methods give the same result
    da = cutfile.readcut(cutfilepath, torfilepath=torfilepath)
    da = cutfile.readcut(cutfilepath, tordict=tordict)
    
    Inputs
    ------
    
    --> cutfilepath = './offset_reflector/Job_01/spherical_cut_farfield_E.cut'
    
    One of the following inputs:
    --> torfilepath = './offset_reflector/Job_01/Job_01.tor' 
    --> tordict = torfile.tor2dict(torfilepath)
    
    Introduction
    ------------
    
    See TICRA-TOOLS-23.1.0-Manual: 1674, 2229, 3317

    V_INI - Initial value of the movement
    V_INC - Increment of the movement
    V_NUM - Number of movement values in the cut
    C     - Dummy value
    ICOMP - Polarisation, not relevant. Fixed value = 3
    ICUT  - Control parameter of cut. Fixed value = 1
    NCOMP - Number of field components. Fixed value = 2

    cuts
        The coupling quotients are written as separate cuts in the file,
        each cut containing values for the fastest varying movement
        specified in the Movement Definition, and one cut for each of
        the steps in the slower varying movements specified. See also
        the remarks to Movement Definition.
    grid
        The coupling quotients are written as grids in the file, each
        grid containing values for the two fastest varying movement
        specified in the Movement Definition, and one grid for each of
        the steps in the slower varying movements specified. See also
        the remarks to Movement Definition.
    one_cut
        All the calculated coupling quotients are written as one sin-
        gle cut in the sequence specified in the Movement Definition
        object. This feature is useful in cases such as determining
        the coupling in a fixed geometry for a range of frequencies
        whereby a frequency sweep is generated in a cut.
        
    Remarks: 
    - The receiving sources may, as an entity, be translated and rotated relatively to the 
    fixed transmitters and the coupling is calculated as function of these movements.
    - It shall be noted that the transmitters are fixed while the receivers move.
        
    Every cut is organized as follows:
    ----------------------------------
    
    1. line with comment
    2. varying coordinate (freq for zero movement defintions, v1 for one movement definition, ...) vs. coupling quotients 
       Notice that "for backward compatibility, the coupling quotient is printed twice". For example:
        Coupling                                                                                                                            
        0.1000000000E+01  0.1000000000E+01  101  0.0000000000E+00    3    1    2
        -0.3663590861E-01  0.1008843458E+00 -0.3663590861E-01  0.1008843458E+00
        0.1064005106E+00 -0.2158923866E-01  0.1064005106E+00 -0.2158923866E-01
        ...
        
    The cut-header contains the following information:
    vN_1    vN_last(if vN_nrsteps = 1 --> vN_last = vN_1+1)     vN_nrsteps      vNminus1_value(0 if noi such movement)    3     2   1  
    0.1000000000E+01  0.1000000000E+01  101  0.0000000000E+00    3    1    2
    
    Cuts are stored one after the other:
    ------------------------------------
    
    Zero movement definitions
    --> nr. cuts = 1
    -------------------------------------------------
    | freq vs. coupling quotients                   |
    -------------------------------------------------
    
    One movement definition (e.g. translation or rotation)
    --> nr. cuts = len(freqs)
    # V_INI, V_INC, V_NUM : refer to the movement v1
    # C : zero because there is no N-1-th movement
    -------------------------------------------------
    | freq1 (v1 vs. coupling quotients)             |
    | freq2 (v1 vs. coupling quotients)             |
    | ...                                           |
    -------------------------------------------------
    
    Two movement definitions (e.g. translation and rotation)
    --> nr. cuts = len(freq)*len(v1)
    # V_INI, V_INC, V_NUM : refer to the movement v2 ("fast" coordinate)
    # C : refers to v1 ("slow" coordinate)
    # Analogy to field data in cuts:
    # freq -> freq
    # fix (e.g. phi) -> slow
    # varying (e.g. theta) -> fast
    -------------------------------------------------
    | freq1 - v11 (v2 vs. coupling quotients)       |
    |       - v12 (v2 vs. coupling quotients)       |
    |       - ...                                   |
    | freq2 - v11 (v2 vs. coupling quotients)       |
    |       - v12 (v2 vs. coupling quotients)       |
    |       - ...                                   |
    | ...                                           |
    -------------------------------------------------
    
    Three movement definitions
    --> nr. cuts = len(freq)*len(v1)*len(v2)
    # V_INI, V_INC, V_NUM : refer to the movement v3 ("fastest" coordinate)
    # C : refers to v2 ("second fastest" coordinate)
    -------------------------------------------------
    | freq1 - v11 - v21 (v3 vs. coupling quotients) |
    |             - v22 (v3 vs. coupling quotients) |
    |             - ...                             |
    |       - v12 - v21 (v3 vs. coupling quotients) |
    |             - v22 (v3 vs. coupling quotients) |
    |             - ...                             |
    |       - ...                                   |
    | freq2 - v11 - v21 (v3 vs. coupling quotients) |
    |             - v22 (v3 vs. coupling quotients) |
    |             - ...                             |
    |       - v12 - v21 (v3 vs. coupling quotients) |
    |             - v22 (v3 vs. coupling quotients) |
    |             - ...                             |
    |       - ...                                   |
    | ...                                           |
    -------------------------------------------------

    """

    if torfilepath:
        tordict = torfile.tor2dict(torfilepath)
    elif tordict:
        pass
    else:
        print('Provide either torfilepath or tordict!')
    
    # we first want to read the torfile: to read the cut-file, we must know
    # - number of frequencies
    # - number of non-trivial movement definitions (and the corresponding numbers of steps)
    infodict = gather_information(cutfilepath, tordict)
    
    # Notice: Trivial movement definitions with number=0 (zero steps) can be defined.
    # They are referenced in the tor-file, but ignored in the cut-file, so we drop them.
    infodict['movdicts'] = [movdict for movdict in infodict['movdicts'] if movdict['number']>0]
    
    # read cutfile to dictionary
    file_form = infodict['file_form']
    nrfreqs = len(infodict['freqs_Hz'])
    nrsteps_per_movement = [movdict['number'] for movdict in infodict['movdicts']]
    if file_form == 'cuts':
        cutdict = cut2dict_cuts(cutfilepath, nrfreqs, nrsteps_per_movement)
    elif file_form == 'one_cut':
        print('Please implement routine for file_form: %s' % file_form)
        raise
    else:
        print('No such file_form: %s' % file_form)
        raise

    # combine information
    cutdict = {**infodict, **cutdict}

    # store data as Xarray
    da = dict2xarray(cutdict)

    return da

def gather_information(cutfilepath: dict, tordict: dict = {}) -> dict:
    """
    Collect data from cut- and tor-file, and create an easy accessible database.
    """

    if tordict:
        
        cutname = Path(cutfilepath).stem
        torinfo = tordict[cutname]
        
        # get class_name ('coupling_system' / vs. 'spherical_cut', ...)
        class_name = torinfo['class_name']
        
        # check that the identified class_name is indeed coupling_system (to avoid wheird errors)
        if class_name != 'coupling_system':
            print('No such class_name: %s' % class_name)
            print('Class name must be "coupling_system"')
            raise

        comment = torinfo['comment'] if 'comment' in torinfo.keys() else None
        receiver_sources = re.findall('ref\((.*?)\)', torinfo['receiver_sources'])
        amplitude_only = torinfo['amplitude_only'] if 'amplitude_only' in torinfo.keys() else 'off'
        cqlist = torinfo['list'] if 'list' in torinfo.keys() else 'off'
        file_name = torinfo['file_name'] if 'file_name' in torinfo.keys() else None
        file_form = torinfo['file_form'] if 'file_form' in torinfo.keys() else 'cuts'
        movement_definition = re.search('ref\((.+)\)', torinfo['movement_definition']).groups()[0] if 'movement_definition' in torinfo.keys() else None
                
        # read frequencies
        freqs_Hz = torfile.read_frequencies(tordict, objname=cutname)
        
        # read movement_definition --> nrsteps_per_movement
        if not movement_definition:
            movdicts = []
        else:
            
            # Example with one movement:
            # sequence    (    struct(movement: translation_along, axis: z_original, start: 0.0, 
            #           end:"ref(distance_antenna2reflector)/2", number: 0, length_unit: mm)    )            
            
            # resolve references like ref(distance_antenna2reflector)
            movspecstring = tordict[movement_definition]['movements']
            references = re.findall('ref\(([^\)]+)\)',movspecstring)
            for reference in references:
                valstr = torfile.get_real_variable(tordict,reference) ### maybe iteratively continue
                movspecstring = movspecstring.replace('ref(%s)'%reference, valstr)
            
            # no there are no brackets left except for following: sequence( struct(...), struct(...), ... )
            movspecs = re.findall('(struct\([^\)]+\))', movspecstring)
            movdicts = [
                {'movement': re.search('movement:\s?([^,]+)', movspec).groups()[0], 
                'axis': re.search('axis:\s?([^,]+)', movspec).groups()[0],
                'start': eval(re.search('start:\s?"?([^,"]+)', movspec).groups()[0]),
                'end': eval(re.search('end:\s?"?([^,"]+)', movspec).groups()[0]),
                'number': int(eval(re.search('number:\s?"?([^,"]+)', movspec).groups()[0])),
                'length_unit': re.search('length_unit:\s?([^\)]+)', movspec).groups()[0]}
                for movspec in movspecs]
                                    
        infodict = {
            'file_name': file_name,
            'class_name': 'coupling_system',
            'file_form': file_form,
            'receiver_sources': receiver_sources,
            'amplitude_only': amplitude_only,
            'movement_definition': movement_definition,
            'cqlist': cqlist,
            'comment': comment,
            'freqs_Hz': freqs_Hz,
            'movdicts': movdicts
        }           
        
    else:

        print('Please provide either torfile of user information.')
        raise
    
    return infodict

def cut2dict_cuts(cutfilepath: str, nrfreqs: int, nrsteps_per_movement: list):
    """
    Read files with file_format = 'cuts'
    Other options: 'one_cut' (should be implemented in another function)
    """
    
    cutfilepath = Path(cutfilepath) # convert string to pathlib object
    with open(cutfilepath, 'r') as file_cut:
        lines = file_cut.readlines()

    line = lines[1].split()
    v_ini, v_inc, v_num, _, icomp, icut, ncomp = [float(s) if '.' in s else int(s) for s in line]
    
    # Read header information of the different cuts (blocks of information)
    no_of_cuts = len(lines) // (v_num + 2)
    cut_coordinates = [0.] * no_of_cuts
    for cut_index in range(no_of_cuts):
        cut_start = cut_index * (v_num + 2)
        line = lines[cut_start + 1].split()
        cut_coordinates[cut_index] = float(line[3])
    
    # check dimensions
    if len(nrsteps_per_movement) == 0:
        
        # --------
        # Example:
        # --------
        
        # rectangular_horn.cpl  coupling_system  
        # (
        #   frequency        : ref(frequency_range),
        #   receiver_sources : sequence(ref(rectangular_horn),ref(rectangular_horn_01)),
        #   movement_definition : ref(rectangular_horn.cpl_movement_definition)
        # )

        # rectangular_horn.cpl_movement_definition  movement_definition  
        # (
        #   coor_sys_for_movements : ref(single_feed_coor),
        #   moved_coordinate_systems : sequence(ref(single_feed_coor_01)),
        #   movements        : sequence
        #     (    struct(movement: rotation_around, axis: x_original, start: 14.0, end: 90.0, number: 0, length_unit: m
        # ),
        #     struct(movement: translation_along, axis: x_original, start: 0.5, end: 2.0, number: 0, length_unit: m)
        #     ),
        #   list             : on
        # )
        
        # Coupling                                                                                                                            
        # 0.1000000000E+01  0.1000000000E+01    3  0.0000000000E+00    3    1    2
        # -0.6705855055E-01  0.2025095553E+00 -0.6705855055E-01  0.2025095553E+00
        # -0.1851487637E+00  0.2689521661E+00 -0.1851487637E+00  0.2689521661E+00
        # -0.2881662806E+00  0.2302100073E+00 -0.2881662806E+00  0.2302100073E+00

        assert no_of_cuts == 1
        assert len(lines)-2 == nrfreqs # v_num
        
        data = np.array([complex(np.nan, np.nan)]*nrfreqs) # np.full(shape=(nrfreqs,), fill_value=complex(np.nan, np.nan), dtype=complex)
        for ii,line in enumerate(lines[2:]):
            line = line.strip().split()
            data[ii] = complex(float(line[0]), float(line[1]))

    elif len(nrsteps_per_movement) == 1:
        
        # --------
        # Example:
        # --------
        
        # rectangular_horn.cpl_01  coupling_system  
        # (
        #   frequency        : ref(frequency_range),
        #   receiver_sources : sequence(ref(rectangular_horn_01),ref(rectangular_horn)),
        #   movement_definition : ref(rectangular_horn.cpl_01_movement_definition_01),
        #   list             : off,
        #   file_form        : cuts,
        #   comment          : ""
        # )

        # rectangular_horn.cpl_movement_definition  movement_definition  
        # (
        # coor_sys_for_movements : ref(single_feed_coor),
        # moved_coordinate_systems : sequence(ref(single_feed_coor_01)),
        # movements        : sequence
        #     (    struct(movement: translation_along, axis: x_original, start: 0.0, end: 2.0, number: 2, length_unit: m
        # ),
        #     struct(movement: translation_along, axis: x_original, start: 0.0, end: 0.0, number: 0, length_unit: m)
        #     ),
        # list             : on
        # )
        
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.2000000000E+01    2  0.0000000000E+00    3    1    2
        # -0.3352927528E-01  0.1012547777E+00 -0.3352927528E-01  0.1012547777E+00
        # -0.3352927528E-01  0.1012547777E+00 -0.3352927528E-01  0.1012547777E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.2000000000E+01    2  0.0000000000E+00    3    1    2
        # -0.9257438186E-01  0.1344760830E+00 -0.9257438186E-01  0.1344760830E+00
        # -0.9257438186E-01  0.1344760830E+00 -0.9257438186E-01  0.1344760830E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.2000000000E+01    2  0.0000000000E+00    3    1    2
        # -0.1440831403E+00  0.1151050036E+00 -0.1440831403E+00  0.1151050036E+00
        # -0.1440831403E+00  0.1151050036E+00 -0.1440831403E+00  0.1151050036E+00

        assert no_of_cuts == nrfreqs
        assert v_num == nrsteps_per_movement[0]

        data = np.full(shape=(nrfreqs, *nrsteps_per_movement), fill_value=complex(np.nan, np.nan), dtype=complex)
        for ii in range(nrfreqs):
            startidx = ii*(v_num+2)
            for jj in range(v_num):
                line = lines[startidx + 2 + jj].split() # +2 means that first two lines are information
                data[ii,jj] = complex(float(line[0]), float(line[1]))

    elif len(nrsteps_per_movement) == 2:
        
        # --------
        # Example:
        # --------
        
        # rectangular_horn.cpl_01  coupling_system  
        # (
        #   frequency        : ref(frequency_range),
        #   receiver_sources : sequence(ref(rectangular_horn_01),ref(rectangular_horn)),
        #   movement_definition : ref(rectangular_horn.cpl_01_movement_definition_01),
        #   list             : off,
        #   file_form        : cuts,
        #   comment          : ""
        # )
        
        # rectangular_horn.cpl_01_movement_definition_01  movement_definition  
        # (
        #   coor_sys_for_movements : ref(single_feed_coor),
        #   moved_coordinate_systems : sequence(ref(single_feed_coor_01)),
        #   movements        : sequence
        #     (    struct(movement: rotation_around, axis: x_original, start: 0.0, end: 90.0, number: 2, length_unit: m)
        # ,
        #     struct(movement: translation_along, axis: x_original, start: 0.0, end: 2.0, number: 4, length_unit: m)
        #     ),
        #   list             : off
        # )
        
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.6666666667E+00    4  0.0000000000E+00    3    1    2
        # -0.6705855055E-01  0.2025095553E+00 -0.6705855055E-01  0.2025095553E+00
        # -0.9120438766E-01  0.1027269799E+00 -0.9120438766E-01  0.1027269799E+00
        # -0.3103615442E-01  0.9987898393E-01 -0.3103615442E-01  0.9987898393E-01
        # -0.3394857049E-01  0.1007650731E+00 -0.3394857049E-01  0.1007650731E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.6666666667E+00    4  0.9000000000E+02    3    1    2
        # -0.3296179779E-01  0.1015751659E+00 -0.3296179779E-01  0.1015751659E+00
        # -0.3383068038E-01  0.1007923738E+00 -0.3383068038E-01  0.1007923738E+00
        # -0.3357345488E-01  0.1017302812E+00 -0.3357345488E-01  0.1017302812E+00
        # -0.3345703846E-01  0.1012315008E+00 -0.3345703846E-01  0.1012315008E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.6666666667E+00    4  0.0000000000E+00    3    1    2
        # -0.1851487637E+00  0.2689521661E+00 -0.1851487637E+00  0.2689521661E+00
        # -0.5525163768E-01  0.1539673252E+00 -0.5525163768E-01  0.1539673252E+00
        # -0.9167157358E-01  0.1353423463E+00 -0.9167157358E-01  0.1353423463E+00
        # -0.9169112214E-01  0.1354078450E+00 -0.9169112214E-01  0.1354078450E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.6666666667E+00    4  0.9000000000E+02    3    1    2
        # -0.8817095792E-01  0.1285428565E+00 -0.8817095792E-01  0.1285428565E+00
        # -0.8905312639E-01  0.1347446937E+00 -0.8905312639E-01  0.1347446937E+00
        # -0.9274308446E-01  0.1341931639E+00 -0.9274308446E-01  0.1341931639E+00
        # -0.9257758450E-01  0.1344663841E+00 -0.9257758450E-01  0.1344663841E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.6666666667E+00    4  0.0000000000E+00    3    1    2
        # -0.2881662806E+00  0.2302100073E+00 -0.2881662806E+00  0.2302100073E+00
        # -0.1479215266E+00  0.8471153322E-01 -0.1479215266E+00  0.8471153322E-01
        # -0.1431595669E+00  0.1190970292E+00 -0.1431595669E+00  0.1190970292E+00
        # -0.1448019603E+00  0.1158624897E+00 -0.1448019603E+00  0.1158624897E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.6666666667E+00    4  0.9000000000E+02    3    1    2
        # -0.1445353148E+00  0.1085057646E+00 -0.1445353148E+00  0.1085057646E+00
        # -0.1458831268E+00  0.1136400368E+00 -0.1458831268E+00  0.1136400368E+00
        # -0.1439732904E+00  0.1151848423E+00 -0.1439732904E+00  0.1151848423E+00
        # -0.1443482388E+00  0.1150878105E+00 -0.1443482388E+00  0.1150878105E+00
        
        # --------
        # Example:
        # --------
        
        # rectangular_horn.cpl  coupling_system  
        # (
        #   frequency        : ref(frequency_range),
        #   receiver_sources : sequence(ref(rectangular_horn),ref(rectangular_horn_01)),
        #   movement_definition : ref(rectangular_horn.cpl_movement_definition)
        # )

        # rectangular_horn.cpl_movement_definition  movement_definition  
        # (
        #   coor_sys_for_movements : ref(single_feed_coor),
        #   moved_coordinate_systems : sequence(ref(single_feed_coor_01)),
        #   movements        : sequence
        #     (    struct(movement: rotation_around, axis: x_original, start: 14.0, end: 90.0, number: 1, length_unit: m
        # ),
        #     struct(movement: translation_along, axis: x_original, start: 0.5, end: 2.0, number: 0, length_unit: m),
        #     struct(movement: translation_along, axis: x_original, start: 2.0, end: 7.0, number: 5, length_unit: m)
        #     ),
        #   list             : on
        # )
        
        # Coupling                                                                                                                            
        # 0.2000000000E+01  0.1250000000E+01    5  0.1400000000E+02    3    1    2
        # -0.3404059938E-01  0.1010128450E+00 -0.3404059938E-01  0.1010128450E+00
        # -0.3334658070E-01  0.1012008835E+00 -0.3334658070E-01  0.1012008835E+00
        # -0.3354595813E-01  0.1013461757E+00 -0.3354595813E-01  0.1013461757E+00
        # -0.3351704384E-01  0.1013119266E+00 -0.3351704384E-01  0.1013119266E+00
        # -0.3348433764E-01  0.1012568413E+00 -0.3348433764E-01  0.1012568413E+00
        # Coupling                                                                                                                            
        # 0.2000000000E+01  0.1250000000E+01    5  0.1400000000E+02    3    1    2
        # -0.9172460936E-01  0.1341635519E+00 -0.9172460936E-01  0.1341635519E+00
        # -0.9281603084E-01  0.1352826135E+00 -0.9281603084E-01  0.1352826135E+00
        # -0.9335059238E-01  0.1341602406E+00 -0.9335059238E-01  0.1341602406E+00
        # -0.9304551676E-01  0.1350741392E+00 -0.9304551676E-01  0.1350741392E+00
        # -0.9194709761E-01  0.1342065380E+00 -0.9194709761E-01  0.1342065380E+00
        # Coupling                                                                                                                            
        # 0.2000000000E+01  0.1250000000E+01    5  0.1400000000E+02    3    1    2
        # -0.1438888616E+00  0.1154785121E+00 -0.1438888616E+00  0.1154785121E+00
        # -0.1442188631E+00  0.1147938877E+00 -0.1442188631E+00  0.1147938877E+00
        # -0.1439756223E+00  0.1152680581E+00 -0.1439756223E+00  0.1152680581E+00
        # -0.1439779346E+00  0.1151051544E+00 -0.1439779346E+00  0.1151051544E+00
        # -0.1441781739E+00  0.1151078581E+00 -0.1441781739E+00  0.1151078581E+00

        assert no_of_cuts == nrfreqs*sum(nrsteps_per_movement[0:-1]) # == nrfreqs*sum(nrsteps_per_movement[0])
        assert v_num == nrsteps_per_movement[-1]
        assert len(set(cut_coordinates)) == nrsteps_per_movement[0]

        data = np.full(shape=(nrfreqs, *nrsteps_per_movement), fill_value=complex(np.nan, np.nan), dtype=complex)
        for ii in range(nrfreqs):
            for jj in range(nrsteps_per_movement[0]):
                startidx = (ii*nrsteps_per_movement[0] + jj)*(v_num+2)
                for kk in range(v_num):
                    line = lines[startidx + 2 + kk].split() # +2 means that first two lines are information
                    data[ii,jj,kk] = complex(float(line[0]), float(line[1]))

    else:
        
        # --------
        # Example:
        # --------
        
        # rectangular_horn.cpl_01  coupling_system  
        # (
        # frequency        : ref(frequency_range),
        # receiver_sources : sequence(ref(rectangular_horn_01),ref(rectangular_horn)),
        # movement_definition : ref(rectangular_horn.cpl_01_movement_definition_01),
        # list             : off,
        # file_form        : cuts,
        # comment          : ""
        # )

        # rectangular_horn.cpl_01_movement_definition_01  movement_definition  
        # (
        # coor_sys_for_movements : ref(single_feed_coor),
        # moved_coordinate_systems : sequence(ref(single_feed_coor_01)),
        # movements        : sequence
        #     (    struct(movement: rotation_around, axis: x_original, start: 0.0, end: 90.0, number: 2, length_unit: m)
        # ,
        #     struct(movement: translation_along, axis: x_original, start: 0.0, end: 2.0, number: 4, length_unit: m),
        #     struct(movement: translation_along, axis: y_original, start: 0.0, end: 1.0, number: 1, length_unit: m)
        #     ),
        # list             : off
        # )
        
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.0000000000E+00    3    1    2
        # -0.6705855055E-01  0.2025095553E+00 -0.6705855055E-01  0.2025095553E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.6666666667E+00    3    1    2
        # -0.9120438766E-01  0.1027269799E+00 -0.9120438766E-01  0.1027269799E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.1333333333E+01    3    1    2
        # -0.3103615442E-01  0.9987898393E-01 -0.3103615442E-01  0.9987898393E-01
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.2000000000E+01    3    1    2
        # -0.3394857049E-01  0.1007650731E+00 -0.3394857049E-01  0.1007650731E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.0000000000E+00    3    1    2
        # -0.3296179779E-01  0.1015751659E+00 -0.3296179779E-01  0.1015751659E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.6666666667E+00    3    1    2
        # -0.3383068038E-01  0.1007923738E+00 -0.3383068038E-01  0.1007923738E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.1333333333E+01    3    1    2
        # -0.3357345488E-01  0.1017302812E+00 -0.3357345488E-01  0.1017302812E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.2000000000E+01    3    1    2
        # -0.3345703846E-01  0.1012315008E+00 -0.3345703846E-01  0.1012315008E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.0000000000E+00    3    1    2
        # -0.1851487637E+00  0.2689521661E+00 -0.1851487637E+00  0.2689521661E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.6666666667E+00    3    1    2
        # -0.5525163768E-01  0.1539673252E+00 -0.5525163768E-01  0.1539673252E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.1333333333E+01    3    1    2
        # -0.9167157358E-01  0.1353423463E+00 -0.9167157358E-01  0.1353423463E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.2000000000E+01    3    1    2
        # -0.9169112214E-01  0.1354078450E+00 -0.9169112214E-01  0.1354078450E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.0000000000E+00    3    1    2
        # -0.8817095792E-01  0.1285428565E+00 -0.8817095792E-01  0.1285428565E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.6666666667E+00    3    1    2
        # -0.8905312639E-01  0.1347446937E+00 -0.8905312639E-01  0.1347446937E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.1333333333E+01    3    1    2
        # -0.9274308446E-01  0.1341931639E+00 -0.9274308446E-01  0.1341931639E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.2000000000E+01    3    1    2
        # -0.9257758450E-01  0.1344663841E+00 -0.9257758450E-01  0.1344663841E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.0000000000E+00    3    1    2
        # -0.2881662806E+00  0.2302100073E+00 -0.2881662806E+00  0.2302100073E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.6666666667E+00    3    1    2
        # -0.1479215266E+00  0.8471153322E-01 -0.1479215266E+00  0.8471153322E-01
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.1333333333E+01    3    1    2
        # -0.1431595669E+00  0.1190970292E+00 -0.1431595669E+00  0.1190970292E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.2000000000E+01    3    1    2
        # -0.1448019603E+00  0.1158624897E+00 -0.1448019603E+00  0.1158624897E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.0000000000E+00    3    1    2
        # -0.1445353148E+00  0.1085057646E+00 -0.1445353148E+00  0.1085057646E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.6666666667E+00    3    1    2
        # -0.1458831268E+00  0.1136400368E+00 -0.1458831268E+00  0.1136400368E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.1333333333E+01    3    1    2
        # -0.1439732904E+00  0.1151848423E+00 -0.1439732904E+00  0.1151848423E+00
        # Coupling                                                                                                                            
        # 0.0000000000E+00  0.1000000000E+01    1  0.2000000000E+01    3    1    2
        # -0.1443482388E+00  0.1150878105E+00 -0.1443482388E+00  0.1150878105E+00

        print('Processing for more than two movements is not yet implemented.')
        print('General routine can be written for two or more movements: recursive for loop?')
        # https://stackoverflow.com/questions/7186518/function-with-varying-number-of-for-loops-python
        raise
    
        

        # assert no_of_cuts == nrfreqs*sum(nrsteps_per_movement[0:-2])
        # assert v_num == nrsteps_per_movement[-1]

        # data = np.full(shape=(nrfreqs, *nrsteps_per_movement), fill_value=complex(np.nan, np.nan), dtype=complex)
        
        # datacoords = [0]*(1+len(nrsteps_per_movement))
        # datadims = list(np.shape(data))
        
        # indexaux = datadims
        # indexaux[-1] += 2 # two info-lines
        # indexweights = [0]*len(datadims)
        # for ii,_ in enumerate(datadims[-1]):
        #     indexweights[ii] = np.prod(datadims[ii:])

        
        # # build indice
        # indice = [datacoords]*np.prod(datadims)
        # for ii,nrcoord in enumerate(datadims):


        # # loop over indice

        # datadims_reversed = list(reversed(datadims))
        # for ii,nrcoord in enumerate(datadims_reversed):
        #     for kk in range(nrcoord):
        #         datacoords[-(ii+1)] = kk
        #         fileidx = sum([idx*weight for idx,weight in zip(datacoords,indexweights)])


        # for ii in range(nrfreqs):
        #     freqstartidx = ii*np.prod(nrsteps_per_movement[0:-1])*(nrsteps_per_movement[-1]+2)
        #     datacoords[0] = ii
        #     for jj,nrcoord in enumerate(list(reversed(nrsteps_per_movement))):
        #         for kk in range(nrcoord):
        #             datacoords[-(jj+1)] = kk
        #             startidx = freqstartidx + 

    cutdict = {
        'file_name': str(cutfilepath.resolve()),
        'vNminus1_values': sorted(list(set(cut_coordinates))), # zeros if no N-1-th movement exists
        'vN_values': np.linspace(v_ini, v_ini + (v_num - 1) * v_inc, v_num), # coordinates of N-th movement,
        'data': data
    }

    return cutdict

def dict2xarray(cutdict: dict) -> xr.DataArray:
    """
    store dictionary as Xarray
    """

    # prepare coordinates to assign to array
    coords_freq = ('freq', cutdict['freqs_Hz'], {'long_name': 'frequency', 'units': 'Hz'})
    coords_movements = [None]*len(cutdict['movdicts'])
    for ii,movdict in enumerate(cutdict['movdicts']):
        vals = np.linspace(movdict['start'], movdict['end'], movdict['number'])
        coords_movements[ii] = ('m1', vals, 
                                {'long_name': "%s (%s)" % (movdict['movement'],movdict['axis']), 
                                 'name': "%s (%s)" % (movdict['movement'],movdict['axis']), 
                                 'units': movdict['length_unit']})

    da = xr.DataArray(
        # name = str(Path(cutdict['file_name']).stem,
        data = cutdict['data'],
        coords = [coords_freq] + coords_movements,
        name = cutdict['file_name'],
        attrs = {
            'file_name': cutdict['file_name'],
            'class_name': cutdict['class_name'],
            'file_form': cutdict['file_form'],
            'receiver_sources': cutdict['receiver_sources'],
            'amplitude_only': cutdict['amplitude_only'],
            'movement_definition': cutdict['movement_definition'],
            'cqlist': cutdict['cqlist'],
            'comment': cutdict['comment']})
    
    return da
