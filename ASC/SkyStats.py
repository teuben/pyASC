#! /usr/bin/env python3
#
#	load a cube with the given command line arguments
#
#  Usage:
#       SkyStats.py  file1.fits [file2.fits ...]
#
#  Output:  an ASCII table with the following columns
#       local_time median_sky exp_time moon_phase file_name

import sys
import numpy as np
from astropy.io import fits

try:
    from astropy.time import Time
    from astroplan.moon import moon_illumination
    Qmoon = True
except:
    Qmoon = False

def my_moon(ffile, Qmiddle, box, m):
    hdu = fits.open(ffile)
    h = hdu[0].header
    d = hdu[0].data
    nx = d.shape[1]
    ny = d.shape[0]
    dc = d[ny//2-box:ny//2+box, nx//2-box:nx//2+box]
    if 'EXPTIME' in h:
        exp = float(h['EXPTIME'])
    else:
        exp = -1.0
    if 'TIME-OBS' in h:
        #
        iso_date = h['TIME-OBS']
        hms = iso_date.split(':')
        moon = -1.0
    elif 'DATE-LOC' in h:
        # '2020-02-29T20:13:34.920'
        iso_date = h['DATE-LOC']
        hms = iso_date.split('T')[1].split(':')
        if len(hms) == 1:
            # '2017-11-19T22-43-30.506'
            # there was a time we did it wrong....
            hms = h['DATE-LOC'].split('T')[1].split('-')
            moon = -3.0
        else:
            # Qmoon is true if astroplan succesfully opened
            if Qmoon:
                # Qmiddle is true if currently on an image you want to calc
                # the moon phase for
                if Qmiddle:
                    # example iso_date (in UT):   2021-09-12T19:58:21.025
                    # print("HMS: ",iso_date)
                    t = Time(iso_date)
                    moon = moon_illumination(t)
                # else, use m value passed in, which should be the middle 
                # argument's moon phase
                else:
                    moon = m
    else:
        hms = -999.999
        moon = -2.0
    t = float(hms[0]) + float(hms[1])/60  + float(hms[2])/3600
    return (t,np.median(dc),exp,moon,ffile)
    #print("%.4f %g %g %g %s" % (t,np.median(dc),exp,moon,ffile))

if __name__ == '__main__':
    
    box = 200

    # Sets Qmiddle to true so it only calculates the moon once, that spot 
    # being the middle of the arguments sent in to SkyStats.py
    middle_moon = my_moon(sys.argv[(len(sys.argv)+2)//2], True, box, -1.0)[3]

    # for each file name sent in, calculate all stats using
    for ffile in sys.argv[1:]:
        moon = my_moon(ffile, False, box, middle_moon)
        print("%.4f %g %g %g %s" % (moon[0],moon[1],moon[2],moon[3],moon[4]))

