#! /usr/bin/env python
#
# This routine can diff images from its neighbors.  For a series i=1,N
# this can loop over i=2,N-2 to produce N-2 difference images
#
#   B_i = A_i - (A_i-1 + A_i+1) / 2
#
# Optionally some hanning smoothing could be applied to the difference
# image to improved source detection
#

from __future__ import print_function

import glob
import sys
import shutil
import os
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np


if False:
    # first one
    f1 = 'MASN01-2018-03-24T01-30-16-112Z.fits'  
    f2 = 'MASN01-2018-03-24T01-29-17-685Z.fits'    # has object
    f3 = 'MASN01-2018-03-24T01-28-19-258Z.fits'
else:
    # second one
    f1 = 'MASN01-2018-03-24T01-55-35-096Z.fits'
    f2 = 'MASN01-2018-03-24T01-56-33-509Z.fits'
    f3 = 'MASN01-2018-03-24T01-57-31-931Z.fits'

hdu1 = fits.open(f1)
hdu2 = fits.open(f2)
hdu3 = fits.open(f3)

h2 = hdu2[0].header

d1 = hdu1[0].data
d2 = hdu2[0].data
d3 = hdu3[0].data

print(f1,d1.min(),d1.max())
print(f2,d2.min(),d2.max())
print(f3,d3.min(),d3.max())

diff = d2 - 0.5*(d2+d3)

fits.writeto('diff.fits',diff,h2,overwrite=True)
