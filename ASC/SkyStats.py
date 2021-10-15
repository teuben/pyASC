#! /usr/bin/env python
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

if __name__ == '__main__':
    box = 200
    
    for ffile in sys.argv[1:]:
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
                if Qmoon:
                    # example iso_date (in UT):   2021-09-12T19:58:21.025
                    # print("HMS: ",iso_date)
                    t = Time(iso_date)
                    moon = moon_illumination(t)
        else:
            hms = -999.999
            moon = -2.0
        t = float(hms[0]) + float(hms[1])/60  + float(hms[2])/3600
        
        print("%.4f %g %g %g %s" % (t,np.median(dc),exp,moon,ffile))
        
