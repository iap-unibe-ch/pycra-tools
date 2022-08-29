#%%
import xarray as xr
import numpy as np
import sys

f = open('farfield_54.grd','r')

header=[]
while 1:
    line = f.readline()
    if line[0:4] == "++++":
        break
    else:
        header.append(line)

freq=[]
for i in header[5].split():
    freq.append(float(i))

ktype=f.readline()
nset,icomp,ncomp,igrid=[int(s) for s in f.readline().split()]

beamc=[]
for i in range(int(nset)):
    beamc.append([float(s) for s in f.readline().split()])

lims=f.readline().split()
xlims=[float(s) for s in lims[0:3:2]]
ylims=[float(s) for s in lims[1:4:2]]

nx,ny,klimit=[int(s) for s in f.readline().split()]

stpx=(xlims[1]-xlims[0])/(nx-1)
stpy=(ylims[1]-ylims[0])/(ny-1)

if klimit==1:
    sys.exit("In .grd file KLIMIT = 1. Code not finished for this")
else:
    Is=1
    Ie=nx

matrix=np.zeros(shape=(nx,ny,2),dtype=complex)
for x in range(nx):
    for y in range(ny):
        line=f.readline().split()
        matrix[x,y,0]=complex(float(line[0]), float(line[1]))
        matrix[x,y,1]=complex(float(line[2]), float(line[3]))

ds = xr.Dataset(
    data_vars=dict(
        Field=(["x","y","field_component"], matrix)
    ),
    coords=dict(
        xcor=(["x"],np.linspace(xlims[0],xlims[1],nx)),
        ycor=(["y"],np.linspace(ylims[0],ylims[1],ny)),
        fco=(["field_component"],["x","y"])
    ),
    attrs=dict(description="What am I doing?"),
)
