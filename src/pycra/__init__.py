"""Package to process Ticra Tools .grd and .cut files"""

# This allows user to just write "from pycra import GridFile" without having to dig through subscripts
from .gridfile import GridFile
from .cutfile import CutFile

__version__ = "0.0.1"
__author__ = "Roland Albers"
__email__ = "roland.albers@unibe.ch"
__all__ = ['GridFile','CutFile']

