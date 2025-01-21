import os

from pycra import torfile
from pycra.fields import cutfile, gridfile

def main():
    
    directory = './offset_reflector/Job_01'
    
    filepath_torfile = os.path.join(directory, 'Job_01.tor')
    tordict = torfile.tor2dict(filepath_torfile)
    
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
    
    da_spherical_cut_farfield_E = cutfile.readcut(filepath_spherical_cut_farfield_E, tordict=tordict)
    print(da_spherical_cut_farfield_E)
    
    da_spherical_grid_nearfield_uv_H = gridfile.readgrid(filepath_spherical_grid_nearfield_uv_H, tordict=tordict)
    print(da_spherical_grid_nearfield_uv_H)
    
    # speedoflight = 299792458
    # userinfodict = {
    #     'class_name': 'spherical_grid', # torfile/user (required): e.g. spherical_cut (surface_cut)
    #     'field_name': 'h_field', # torfile/user (required): e.g. e_field (incident_e_field)
    #     #'coordinate_system_name': da_spherical_grid_nearfield_uv_H.coordinate_system_name, # torfile/user (optional)
    #     #'nearfield_distance_m': da_spherical_grid_nearfield_uv_H.field_region_distance_m,  # torfile/user (optional)
    #     #'freqs_Hz': da_spherical_grid_nearfield_uv_H.freq.values
    #     }
    # da_spherical_grid_nearfield_uv_H = gridfile.readgrid(filepath_spherical_grid_nearfield_uv_H, userinfodict=userinfodict)
    # print(da_spherical_grid_nearfield_uv_H)
        
    da_surface_grid_Hr = gridfile.readgrid(filepath_surface_grid_Hr, tordict=tordict)
    print(da_surface_grid_Hr)
    print(da_surface_grid_Hr.comp)
        
    da_surface_grid_I = gridfile.readgrid(filepath_surface_grid_I, tordict=tordict)
    print(da_surface_grid_I)
    print(da_surface_grid_I.comp)

    
    return

if __name__ == '__main__':
    main()