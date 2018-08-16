#! /usr/bin/env python
#
# This routine can diff images from its neighbors.  For a series i=1,N
# this can loop over i=2,N to produce N-1 difference images
#
#   B_i = A_i - A_i-1 
#

from __future__ import print_function

import glob
import sys
import shutil
import os
import numpy as np


if len(sys.argv) == 3:
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    print("Using %s %s" % (f1,f2))

#  check file extension


if f1[f1.rfind('jpg'):] == 'jpg':
    use_fits = False
else:
    use_fits = True


if use_fits:
    from astropy.io import fits

    hdu1 = fits.open(f1)
    hdu2 = fits.open(f2)

    h2 = hdu2[0].header

    d1 = hdu1[0].data.astype(np.float32)
    d2 = hdu2[0].data.astype(np.float32)
else:
    from PIL import Image

    im1 = Image.open(f1)
    im2 = Image.open(f2)

    d1 = np.asarray(im1)
    d2 = np.asarray(im2)

print(f1,d1.min(),d1.max())
print(f2,d2.min(),d2.max())

diff = d2 - d1

max1 = d1.max()
std1 = diff.std()
fidelity = max1 / std1



print("MEAN/STD/FID:",diff.mean(), std1, fidelity)

if use_fits:
    fits.writeto('diff.fits',diff,h2,overwrite=True)
#
#fid  = np.abs(d2) / np.max(np.abs(diff),std1/1.4)
#fits.writeto('fidelity.fits',fid,h2,overwrite=True)

try:
    import matplotlib.pyplot as plt
    plt.figure(1)
    plt.hist(diff.ravel())
    plt.show()
except:
    print("Failing to plot")

