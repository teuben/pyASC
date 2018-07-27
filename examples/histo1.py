#! /usr/bin/env python
#

from astropy.io import fits
import numpy as np
import math
import sys
import matplotlib.pyplot as plt






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
    print("Stats-full: ",dmean,dstd,dmin,dmax)

    return (head,data)


if __name__ == '__main__':

    filename = sys.argv[1]
    (h,d) = get_hdu(filename)

    x0 = int(sys.argv[2])
    y0 = int(sys.argv[3])
    r0 = int(sys.argv[4])
    
    dc = d[y0-r0:y0+r0,x0-r0:x0+r0]

    dc0 = dc.ravel()
    dmax = dc.max()
    dmin = dc.min()
    dmean = dc.mean()
    dstd  = dc.std()
    print("Stats-box : ",dmean,dstd,dmin,dmax)
    print("Exposure  : ",h['EXPTIME'])


    plt.figure()
    plt.subplot(121)
    plt.title("%s %d %d %d" % (filename,x0,y0,r0))    
    plt.imshow(dc)
    plt.subplot(122)
    plt.title("%g %g" % (dmean,dstd))
    plt.hist(dc0,32)
    plt.show()
    
