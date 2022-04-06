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
from astropy.coordinates import EarthLocation
from scipy.fftpack import ss_diff
import datetime
import pytz

try:
    from astropy.time import Time
    import astropy.units as u
    from astroplan.moon import moon_illumination
    from astroplan import Observer
    Qmoon = True
except:
    Qmoon = False

# function to check if sunset or sunrise are during daylight savings in a given timeZone
def is_dst(dt,timeZone):
   aware_dt = timeZone.localize(dt)
   return aware_dt.dst() != datetime.timedelta(0,0)

# local time, used in is_dst
timeZone = pytz.timezone("US/Eastern")

def my_moon(ffile, Qcalc, box, m):
    hdu = fits.open(ffile)
    h = hdu[0].header
    d = hdu[0].data
    nx = d.shape[1]
    ny = d.shape[0]
    dc = d[ny//2-box:ny//2+box, nx//2-box:nx//2+box]
    moon = -16.0
    sunset = -1
    sunrise = -1
    if 'EXPTIME' in h:
        exp = float(h['EXPTIME'])
    else:
        exp = -1.0
    if 'TIME-OBS' in h:
        #
        iso_date = h['TIME-OBS']
        hms = iso_date.split(':')
        moon = -17.0
    elif 'DATE-LOC' in h:
        # '2020-02-29T20:13:34.920'
        iso_date = h['DATE-LOC']
        hms = iso_date.split('T')[1].split(':')
        if len(hms) == 1:
            # '2017-11-19T22-43-30.506'
            # there was a time we did it wrong....
            hms = h['DATE-LOC'].split('T')[1].split('-')
            moon = -18.0
        else:
            # Qmoon is true if astroplan succesfully opened
            if Qmoon:
                # Qmiddle is true if currently on an image you want to calc
                # the moon phase for
                if Qcalc:
                    # example iso_date (in UT):   2021-09-12T19:58:21.025
                    # print("HMS: ",iso_date)
                    t = Time(iso_date)
                    moon = moon_illumination(t)

                    # also get the sunset/sunrise, the UMD Observatory, where MASN01 is,
                    # closest observatory that astropy gives us
                    # MASN01 Coords: +39.0021 (N), -76.9560 (W), ele = 56m
                    location = EarthLocation.from_geodetic(-76.9560*u.deg, 39.0021*u.deg, 56*u.m)
                    UMD_obs = Observer(location = location, name = "UMD_obs", timezone = "US/Eastern")
                    
                    sunset = "{0.iso}".format(UMD_obs.sun_set_time(t, which = 'nearest')).split(' ')
                    sunrise = "{0.iso}".format(UMD_obs.sun_rise_time(t, which = 'nearest')).split(' ')

                    # checking for daylight savings for both sunrise and sunset
                    # clock change: summer = EDT = UTC - 4, is_dst = True
                    # winter = EST = UTC - 5, is_dst = False
                    ss = [int(x) for x in sunset[0].split('-')]
                    sr = [int(x) for x in sunrise[0].split('-')]
                    sunset_dst = is_dst(datetime.datetime(ss[0],ss[1],ss[2]), timeZone)
                    sunrise_dst = is_dst(datetime.datetime(sr[0],sr[1],sr[2]), timeZone)

                    # x is the sunset hour difference from UTC to local time (EST)
                    # y is the sunrise hour difference from UTC to local time (EST)
                    x,y = 5,5
                    if sunset_dst:
                        x = 4
                    if sunrise_dst:
                        y = 4

                    # split the time up. It comes back in UTC, so change it to EST,
                    # that is, subtract x (5 or 4 depending on timezone),
                    # make sure it does not go negative
                    ss = sunset[1].split(':')
                    sr = sunrise[1].split(':')
                    if int(ss[0]) - x < 0:
                        ss[0] = int(ss[0]) + 24 - x
                    else:
                        ss[0] = int(ss[0]) - x
                    sunset = float(ss[0]) + float(ss[1])/60 + float(ss[2])/3600
                    if int(sr[0]) - y < 0:
                        sr[0] = int(sr[0]) + 24 - y
                    else:
                        sr[0] = int(sr[0]) - y
                    sunrise = float(sr[0]) + float(sr[1])/60 + float(sr[2])/3600

                # else, use m value passed in, which should be the middle 
                # argument's moon phase.
                else:
                    moon = m
    else:
        hms = -999.999
        moon = -2.0
    t = float(hms[0]) + float(hms[1])/60  + float(hms[2])/3600
    return (t,np.median(dc),exp,moon,ffile,sunset,sunrise)

if __name__ == '__main__':
    
    box = 200

    # gather first image of the night's moon illumination
    first_moon = my_moon(sys.argv[1], True, box, -19.0)
    # gather middle image of the night's moon illumination, 
    middle_moon = my_moon(sys.argv[(len(sys.argv)+2)//2], True, box, -11.0)

    # print out commented sunrise and sunset
    #print('#',first_moon[5],first_moon[6])
    print('#%.4f %.4f' % (first_moon[5],first_moon[6]))

    # if moon illumination is decreasing then mark it with a negative to know 
    # that the moon is waning, else the moon is waxing so keep it positive
    if middle_moon[3] < first_moon[3]:
        middle_moon[3] = (-1) * middle_moon[3]

    # for each file name sent in, calculate all stats except moon illumination.
    # The moon illumination value is defaulted with middle_moon
    for ffile in sys.argv[1:]:
        moon = my_moon(ffile, False, box, middle_moon[3])
        print("%.4f %g %g %g %s" % (moon[0],moon[1],moon[2],moon[3],moon[4]))