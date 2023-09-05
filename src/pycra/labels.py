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