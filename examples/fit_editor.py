# python system modules
import sys
import astropy.io.fits as fits
import glob

argv = sys.argv

for ff in argv[1:]:
    if '/' in ff:
        fn = ff.rsplit('/', 1)[1]
    else:
        fn = ff
        
    for wildcard in glob.glob(fn):
        hdulist = fits.open(wildcard, 'update')
        hdu = hdulist[0]
        hdu.header['TELESCOP'] = 'MDallsky_1'
        hdu.header['ORIGIN'] = 'Oculus_USB'
        #eventually will want to just have system clock be in UTC so a time offset is not needed
        hdu.header['UTOFFSET'] = -4
        hdu.header['comment'][0] = 'Elizabeth Warner'
        hdu.header['comment'][1] = 'warnerem@astro.umd.edu'
        hdu.header['comment'][2] = '301-405-6555'
        hdu.header['comment'][3] = 'mdallsky.astro.umd.edu'
        hdulist.close()
