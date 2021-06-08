""" smoke.py: smoke tests for JS9, calling much of the public API """
import time
import sys
import json
import pyjs9
from astropy.io import fits
from smokesubs import *

def fitsioTest(j, file):
    """
    test FITS IO routines
    """
    hdul = fits.open(file)
    hdul.info()
    j.SetFITS(hdul, file)

def smokeTests():
    """
    all the tests
    """
    j = pyjs9.JS9()
    fitsioTest(j, "good.fits")
    sleep(5)
    sys.exit()

if __name__ == '__main__':
    smokeTests()
