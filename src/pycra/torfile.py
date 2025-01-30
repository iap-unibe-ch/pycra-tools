import re
import pint
import numpy as np
from pathlib import Path

def tor2dict(filepath: str) -> dict:
    """
    Read objects from .tor file into a dictionary for further processing.

    Idea (terms: GRASP manual description of the 'objects window'):
        dict_graspobj = {object_name: {'class_name': categorizing_name, attribute1: values, ...}, ...}

    Example:
        dict_grasoobj = {'single_frequencies': {'class_name': 'frequency', 'frequency_list': 'sequence(11.0 GHz,12.0 GHz)'}, ...}

    """
    
    # read the file
    with open(Path(filepath)) as f:
        lines = f.readlines()
    
    # drop tailing spaces and return characters. Identify related rows.
    lines = [line.rstrip() for line in lines]
    lines = [line for line in lines if line] # drop empty lines (needed?)
    sidx = [ii for ii,line in enumerate(lines) if line=='(']
    eidx = [ii for ii,line in enumerate(lines) if line==')']
    assert len(sidx) == len(eidx) # or some more advanced testing...

    # dynamically create dictionary of dictionaries
    tordict = {}
    for ii,jj in zip(sidx, eidx):
        # initialize dictionary for each object and store categorizing name
        # see manual 10.5.0 p. 171
        display_name, class_name = lines[ii-1].split()
        tordict[display_name] = {'class_name': class_name}
        for idx in range(ii+1,jj):
            # search and store attributes and corresponding values
            # non-empty lines between parenthesis start with indent line: '  frequency_list   : '
            mm = re.search(r'\s{2}([^\s]*)\s+:\s(.*)', lines[idx])
            add_to_previous = False
            if not mm:
                add_to_previous = True
            elif len(mm.groups()) != 2:
                add_to_previous = True
            else:
                attr = mm.groups()[0]
                specs = mm.groups()[1]
                tordict[display_name][attr] = specs
            if add_to_previous:
                try:
                    tordict[display_name][attr] += lines[idx]
                except Exception as ee:
                    print(repr('Problem in line %s: %s' % (idx, lines[idx])))

        # drop tailing commas (...)
        for key in tordict[display_name]:
            tordict[display_name][key] = tordict[display_name][key].rstrip(',')
        # for x, y in dict_graspobj.items():
        #     print('%s: %s' % (x, y))

    return tordict

def read_frequencies(tordict, objname):
    """
    Read frequency values from .tor file.
    To do so, find first object of object class "frequency" and extract frequencies.
    """
    
    ureg = pint.UnitRegistry()
    
    # get frequency key
    if not 'frequency' in tordict[objname].keys():
        print('Frequency field not found for object: %s' % objname)
        print('torinfo: %s' % tordict[objname])
        raise
    else: # check reference to another frequency object
        mm = re.search(r'ref\((.*)\)', tordict[objname]['frequency'])
        frequency_object_name = mm.groups()[0] if mm else ''
        #########
        if not frequency_object_name:
            print('Please inspect frequency attribute of tor-format: %s' % objname)
            raise
        # if 'frequency' in tordict[objname].keys():
        #     freqkey = 'frequency'
        # elif 'frequency_range' in tordict[objname].keys():
        #     freqkey = 'frequency_range'        
        # elif 'wavelength' in tordict[objname].keys():
        #     freqkey = 'wavelength'
        # elif 'wavelength_range' in tordict[objname].keys():
        #########

    freqdict = tordict[frequency_object_name]

    if freqdict['class_name'] == 'frequency':

        freqstr = tordict[frequency_object_name]['frequency_list']
        
        # replace references
        references = re.findall(r'ref\(([^\)]+)\)',freqstr)
        for reference in references:
            valstr = get_real_variable(tordict,reference)
            freqstr = freqstr.replace('ref(%s)'%reference, valstr)
        
        # retrieve numeric values
        mm = re.search(r'sequence\((.*)\)', freqstr)
        if not mm:
            print('Failed to read frequencies: %s' % freqstr)
            raise
        else:
            freqs_units = re.findall(r'"?([^\s"]+)"?\s([a-zA-Z]+),?', mm.groups()[0]) # '(\-?[0-9\.E\-]+)\s([a-zA-Z]+)'
            freqs_Hz = [(eval(freq)*ureg[unit]).to('Hz').magnitude for freq,unit in freqs_units]

    elif freqdict['class_name'] == 'frequency_range':

        freqstr = tordict[frequency_object_name]['frequency_range']
        
        # replace references
        references = re.findall(r'ref\(([^\)]+)\)',freqstr)
        for reference in references:
            valstr = get_real_variable(tordict,reference)
            freqstr = freqstr.replace('ref(%s)'%reference, valstr)
        
        # retrieve numeric values
        mm_startfreq = re.search(r'start_frequency:\s'+'"?([^\s"]+)"?\s([a-zA-Z]+)', freqstr) # '(\-?[0-9\.E\-]+)\s([a-zA-Z]+)'
        mm_endfreq = re.search(r'end_frequency:\s'+'"?([^\s"]+)"?\s([a-zA-Z]+)', freqstr) # '(\-?[0-9\.E\-]+)\s([a-zA-Z]+)'
        mm_nrfreq = re.search(r'number_of_frequencies:\s'+'"?([^\s"\)]+)"?', freqstr) # ([0-9]+)
        startfreq = eval(mm_startfreq.groups()[0]) * ureg[mm_startfreq.groups()[1]]
        startfreq_Hz = startfreq.to('Hz').magnitude
        endfreq = eval(mm_endfreq.groups()[0]) * ureg[mm_endfreq.groups()[1]]
        endfreq_Hz = endfreq.to('Hz').magnitude
        nrfreqs = int(eval(mm_nrfreq.groups()[0]))
        freqs_Hz = np.linspace(startfreq_Hz,endfreq_Hz,nrfreqs)
        
    elif freqdict['class_name'] == 'wavelength':
        
        speedoflight = 299792458
        freqstr = tordict[frequency_object_name]['wavelength_list']
        
        # replace references
        references = re.findall(r'ref\(([^\)]+)\)',freqstr)
        for reference in references:
            value = get_real_variable(tordict,reference)
            freqstr = freqstr.replace('ref(%s)'%reference, str(value))
        
        # retrieve numeric values
        mm = re.search(r'sequence\((.*)\)', freqstr)
        if not mm:
            print('Failed to read wavelengths: %s' % freqstr)
            raise
        else: 
            wavelengths_units = re.findall(r'"?([^\s"]+)"?\s([a-zA-Z]+),?', mm.groups()[0]) # '(\-?[0-9\.E\-]+)\s([a-zA-Z]+)'
            wavelengths = [(eval(wavelength)*ureg[unit]).to('m').magnitude for wavelength,unit in wavelengths_units]
            freqs_Hz = [speedoflight / wavelength for wavelength in wavelengths]
        
    elif freqdict['class_name'] == 'wavelength_range':
        
        speedoflight = 299792458
        freqstr = tordict[frequency_object_name]['wavelength_range']
        
        # replace references
        references = re.findall(r'ref\(([^\)]+)\)',freqstr)
        for reference in references:
            valstr = get_real_variable(tordict,reference)
            freqstr = freqstr.replace('ref(%s)'%reference, valstr)
        
        # retrieve numeric values
        mm_startw = re.search(r'start_wavelength:\s'+'"?([^\s"]+)"?\s([a-zA-Z]+)', freqstr) # '(\-?[0-9\.E\-]+)\s([a-zA-Z]+)'
        mm_endw = re.search(r'end_wavelength:\s'+'"?([^\s"]+)"?\s([a-zA-Z]+)', freqstr) # '(\-?[0-9\.E\-]+)\s([a-zA-Z]+)'
        mm_nrw = re.search(r'number_of_wavelengths:\s'+'"?([^\s"\)]+)"?', freqstr) # ([0-9]+)
        startw = eval(mm_startw.groups()[0]) * ureg[mm_startw.groups()[1]]
        startw_m = startw.to('m').magnitude
        endw = eval(mm_endw.groups()[0]) * ureg[mm_endw.groups()[1]]
        endw_m = endw.to('m').magnitude
        nrw = int(eval(mm_nrw.groups()[0]))
        wavelengths = np.linspace(startw_m,endw_m,nrw)
        freqs_Hz = [speedoflight / wavelength for wavelength in wavelengths]
        
    else:
        
        print('Please implement class name: %s' % freqdict['class_name'])
        raise

    return freqs_Hz

def get_coordinate_system_name(torinfo):

    if 'coor_sys' in torinfo.keys():
        mm = re.search(r'ref\((.*)\)', torinfo['coor_sys'])
        coordinate_system_name = mm.groups()[0]
    else:
        coordinate_system_name = 'None'

    return coordinate_system_name

def get_nearfield_distance(tordict, gridname):

    torinfo = tordict[gridname]
    if torinfo['class_name'] in ['spherical_cut', 'planar_cut', 'spherical_grid', 'planar_grid']:
        keyword = 'near_dist'
    elif torinfo['class_name'] in ['cylindrical_cut', 'cylindrical_grid']:
        keyword = 'radius'
    else:
        print('"get_nearfield_distance" not implemented for given class_name: %s' % torinfo['class_name'])
        raise

    if 'near_dist' not in torinfo.keys():
        distance = 0
        units = 'm'
    else:
        mm = re.search(r'"ref\((.*)\)" (.*)', torinfo[keyword])
        if mm:
            varname = mm.groups()[0]
            units = mm.groups()[1]
            distance = float(get_real_variable(tordict, varname))
        else:
            distance_units = torinfo[keyword].split(' ')
            distance = float(distance_units[0])
            units = distance_units[1]

    return distance, units

def get_real_variable(tordict, varname):
    """
    resolve real variables
    
    Example tor-file
    -----------------
    
    # testvar  real_variable  
    # (
    # value            : "ref(dradome)/ref(something)"
    # )
    
    # something  real_variable  
    # (
    # value            : "ref(distance_antenna2radome)"
    # )
    
    # dradome  real_variable  
    # (
    # value            : "ref(dskin)+ref(dcore)+ref(dskin)"
    # )
    
    # distance_antenna2radome  real_variable  
    # (
    # value            : 1040.0
    # )
    
    # dskin  real_variable  
    # (
    # value            : 0.5
    # )
    
    # dcore  real_variable  
    # (
    # value            : 38.0
    # )
    
    Example usage
    -------------
    
    from pycra import torfile
    testvar = torfile.get_real_variable(tordict,'testvar')
    print(eval(testvar)) # --> 0.0375
    print(testvar) # --> ((0.5)+(38.0)+(0.5))/((1040.0))
    
    """

    valstr = tordict[varname]['value']
    references = re.findall(r'ref\(([^\)]+)\)',valstr)
    for reference in references:
        valstr_next = get_real_variable(tordict,reference) # recursion
        valstr = valstr.replace('ref(%s)'%reference, "(%s)"%valstr_next) # add brackets to ensure correct multiplications etc. in equations
    valstr = re.search(r'^"?([^"]+)"?$',valstr).groups()[0] # drop quotation marks
        
    return valstr

def get_coordinate_systems(tordict):
    
    dict_coordinate_systems = dict([
        (key, tordict[key]) for key in tordict.keys() if 
        tordict[key]['class_name'] == 'coor_sys'])
    
    return dict_coordinate_systems