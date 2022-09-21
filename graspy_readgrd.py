#%%
import xarray as xr
import numpy as np
import sys
import matplotlib.pyplot as plt

attr_sphere= [
    {1: "linear thet and phi",2: "rhc and lhc",3: "ludwigs co and cx",4: "major and minor axes",5: "xpd E_thet/E_phi and E_phi/E_thet",6: "xpd rhc/lhc and lhc/rhc",7: "xpd co/cx and cx/co",8: "xpd major/minor and minor/major",9: "total power and sqrt rhc/lhc"},
    {2: "two field comp",3: "three field comp",5: "rcs for both polarisations"},
    {1: "uv-grid",4: "elevation over azimuth",5: "elevation and azimuth",6: "azimuth over elevation",7: "theta_phi grid", 9: "azimuth over elevation,edx",10: "elevation over azimuth,edx"}
    ]

axis_label= {1: ["u","v"],4:["Azimuth (deg)","Elevation (deg)"],5:["Azimuth (deg)","Elevation (deg)"],6:["Azimuth (deg)","Elevation (deg)"],7:["Phi (deg)","Theta (deg)"],9:["Azimuth (deg)","Elevation (deg)"],10:["Azimuth (deg)","Elevation (deg)"]}

class gridfile:
    def __init__(self, fname: str) -> xr.DataArray:
        self.data=self.readgrid(fname)

    def readgrid(self,fname: str,attr_key=attr_sphere) -> xr.DataArray:
        f_grid = open(fname,'r')

        header=[]
        while 1:
            line = f_grid.readline()
            if line[0:4] == "++++":
                break
            else:
                header.append(line)

        freq=[]
        for i in header[5].split():
            freq.append(float(i))

        ktype=f_grid.readline()
        nset,icomp,ncomp,igrid=[int(s) for s in f_grid.readline().split()]

        beamc=[]
        for i in range(int(nset)):
            beamc.append([float(s) for s in f_grid.readline().split()])

        list_da=[]
        for idx,f in enumerate(freq):
            lims=f_grid.readline().split()
            xlims=[float(s) for s in lims[0:3:2]]
            ylims=[float(s) for s in lims[1:4:2]]

            nx,ny,klimit=[int(s) for s in f_grid.readline().split()]

            stpx=(xlims[1]-xlims[0])/(nx-1)
            stpy=(ylims[1]-ylims[0])/(ny-1)

            matrix=np.zeros(shape=(ny,nx,4),dtype=float)

            if klimit==1:
                sys.exit("In .grd file KLIMIT = 1. Code not finished for this")
            else:
                Is=1
                Ie=nx
            for y in range(ny):
                for x in range(nx):
                    line=f_grid.readline().split()
                    matrix[y,x,0]=float(line[0])
                    matrix[y,x,1]=float(line[1])
                    matrix[y,x,2]=float(line[2])
                    matrix[y,x,3]=float(line[3])
            matrix4d = np.expand_dims(matrix, 3)
            da = xr.DataArray(
                data=matrix4d,
                dims=["ycor","xcor","comp","band"],
                name=fname,
                coords=dict(
                    xcor=(["xcor"],np.linspace(xlims[0],xlims[1],nx)), 
                    ycor=(["ycor"],np.linspace(ylims[0],ylims[1],ny)),
                    comp=(["comp"],["E_re","E_i","H_re","H_i"]),
                    band=(["band"],[idx+1]),
                ),
                attrs=dict(
                    filename=fname,
                    nset=[nset,"number of field sets or beams"],
                    icomp=[icomp,attr_key[0][icomp]],
                    ncomp=[ncomp,attr_key[1][ncomp]],
                    igrid=[igrid,attr_key[2][igrid]],
                    source_field=header[2][19:],
                    freq_name=header[3][16:],
                    freqs=freq
                ),
            )
            list_da.append(da)
        da=xr.concat(list_da,dim="band")
        return da

    def power(self,grid_array: xr.DataArray) -> xr.DataArray:
        # This is a "shortcut" way of computing the power without having to convert to complex values first
        power_grid=grid_array**2
        power_grid=power_grid.sum(dim="comp")
        power_grid.name="power"
        max_dB=[]
        for it in power_grid.band:
            s=power_grid.sel(band=it).where(power_grid.sel(band=it)==power_grid.sel(band=it).max(dim=["xcor","ycor"]),drop=True).squeeze()
            max_dB.append(10*np.log10(s))
        else:
            xr.merge([self.data,power_grid]) 
            return max_dB

    def co_cross(self,grid_array: xr.DataArray) -> None:
        max_v=self.power(grid_array)
        cmplx_E=grid_array.isel(comp=0)+grid_array.isel(comp=1)*1j
        cmplx_H=grid_array.isel(comp=2)+grid_array.isel(comp=3)*1j
        for it in max_v: #this will still break if its more than one band
            x_max_val=cmplx_E.sel(xcor=it.coords['xcor'].values,ycor=it.coords['ycor'].values)
            y_max_val=cmplx_H.sel(xcor=it.coords['xcor'].values,ycor=it.coords['ycor'].values)
        r = np.arctan2(1,np.real(y_max_val/x_max_val))
        v_co=cmplx_E*np.sin(r)+cmplx_H*np.cos(r)
        v_cross=cmplx_E*np.cos(r)-cmplx_H*np.sin(r)
        # #normalise main beam phase to 0 deg wtf does this do
        pr=v_co.isel(ycor=np.abs(v_co).argmax(dim='ycor')) #fun fact np.max only looks at real part. MATLAB max looks at abs. value
        b=np.abs(pr)
        b=np.array(b)
        b=b.reshape((1,241))
        a=np.array(pr)
        a=a.reshape((1,241))
        pr=np.linalg.lstsq(a.T,b.T)[0]
        v_co=v_co*pr
        v_co.name="co_polar"
        v_cross=v_cross*pr
        v_cross.name="x_polar"
        #add x y z to this function at some point later
        co_dB=20*np.log10(np.abs(v_co/v_co.isel(np.abs(v_co).argmax(dim=['ycor','xcor']))))
        co_dB.name="co_dB"
        cross_dB=20*np.log10(np.abs(v_cross/v_co.isel(np.abs(v_co).argmax(dim=['ycor','xcor']))))
        cross_dB.name="x_dB"
        self.data=xr.merge([self.data,v_co,v_cross,co_dB,cross_dB])

    def plotcont(self,grid_array: xr.DataArray) -> None:
        fig,ax = plt.subplots()
        con=grid_array.plot.contour(colors='k',levels=[-30,-20,-10,-6,-3,-0.1])
        ax.set_xlabel(axis_label[test.data.igrid[0]][0])
        ax.set_ylabel(axis_label[test.data.igrid[0]][1])
        return fig,ax,con

    def save(self) -> None:
        self.data.to_netcdf(self.data.filename[:-4]+'.nc')

    
# %%

test=gridfile('asym_test.grd')
maxdB=test.power(test.data)
test.co_cross(test.data)
fig,ax,con=test.plotcont(test.data.co_dB.sel(band=1))
