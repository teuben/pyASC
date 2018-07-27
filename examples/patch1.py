#! /usr/bin/env python
#

from astropy.io import fits
import numpy as np
import math
import sys



#  806 in the abs() algorithm
#  635 in the v1-v2>eps
def patch_badpixels1(data, eps=0.1):
    nx = data.shape[1]
    ny = data.shape[0]
    nbad = 0
    for ix in range(1,nx-1):
        for iy in range(1,ny-1):
            v1 = data[iy,ix]
            # v2 = (data[iy-1,ix] + data[iy+1,ix] + data[iy,ix-1] + data[iy,ix+1])/4.0      # 4 points
            # v2 =  (data[iy-1:iy+2,ix-1:ix+2].sum() - v1)/8.0      # 8 points
            if v1 - data[iy-1,ix]  < eps: continue
            if v1 - data[iy+1,ix]  < eps: continue
            if v1 - data[iy,ix-1]  < eps: continue
            if v1 - data[iy,ix+1]  < eps: continue
            v2 = (data[iy-1,ix] + data[iy+1,ix] + data[iy,ix-1] + data[iy,ix+1])/4.0        # 4 points
            nbad = nbad + 1
            print("Bad pixel",nbad,ix+1,iy+1,v1,v2)
            data[iy,ix] = v2
    return nbad

def patch_badpixels2(data, eps=0.1):
    def good_pixel(v1,v2,dat,eps):
        if v1-dat < eps: return True
        v2.append(dat)
        return False
    
    nx = data.shape[1]
    ny = data.shape[0]
    nbad = 0
    for ix in range(1,nx-1):
        for iy in range(1,ny-1):
            v1 = data[iy,ix]
            v2 = []

            if good_pixel(v1,v2,data[iy-1,ix],eps): continue
            if good_pixel(v1,v2,data[iy+1,ix],eps): continue
            if good_pixel(v1,v2,data[iy,ix-1],eps): continue
            if good_pixel(v1,v2,data[iy,ix+1],eps): continue
            nbad = nbad + 1
            print("Bad pixel",nbad,ix+1,iy+1,v1,v2)
            data[iy,ix] = np.array(v2).mean()
    return nbad


def get_hdu(filename):
    """   get the primary HDU of a FITS file
          also reports the mean/std/min/max

          Note we are returning a float converted array, since
          match on the 16-bit "ushort" will quickly result in
          overflow and data corruption
    """
    hdu  = fits.open(filename,ignore_missing_end=True)
    head = hdu[0].header
    data = hdu[0].data.astype(np.float32)
    dmax = data.max()
    dmin = data.min()
    dmean = data.mean()
    dstd  = data.std()
    print("Stats: ",dmean,dstd,dmin,dmax)

    return (head,data)


if __name__ == '__main__':

    filename = sys.argv[1]
    eps      = float(sys.argv[2])

    (h,d) = get_hdu(filename)

    d0 = d.copy()
    nbad = patch_badpixels1(d0, eps)
    print("Found ",nbad," to patch")
