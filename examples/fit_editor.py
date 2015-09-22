# python system modules
import sys, os
import astropy.io.fits as fits
import glob

argv = sys.argv

for ff in argv[1:]:
    if '/' in ff:
        fn = ff.rsplit('/', 1)[1]
    else:
        fn = ff
        
    for wildcard in glob.glob(fn):
        
        #Editing the original fits file with the correct values
        hdulist = fits.open(wildcard, 'update')
        hdu = hdulist[0]
        hdu.header['TELESCOP'] = 'MDallsky_1'
        hdu.header['ORIGIN']   = 'Oculus_USB'
        #eventually will want to just have system clock be in UTC so a time offset is not needed
        hdu.header['UTOFFSET'] = -4
        hdu.header['comment'][0] = 'Elizabeth_Warner'
        hdu.header['comment'][1] = 'warnerem@astro.umd.edu'
        hdu.header['comment'][2] = '301-405-6555'
        hdu.header['comment'][3] = 'mdallsky.astro.umd.edu'
        hdulist.flush()
        
        #Now creating the .fits file with the specified file name and organized into directories by \year\month\day\yyyymmdd_zzz_xxxx.fits
        
        
        #Create a String for the name of the file in format <yyyymmdd_zzz_xxxx.fits>
        #first an array of the date split into year, month, and day
        date = hdu.header['DATE-OBS'].rsplit('-')
        file_name = date[0] + date[1] + date[2] + '_'
        #now get the telescope location and number (e.g. MDallsky_1 would be MD1)
        file_name += hdu.header['TELESCOP'][:2] + hdu.header['TELESCOP'][-1:] + '_'
        #finally get the frame number from the original .FIT file (IMG00002.FIT would be 0002)
        file_name += wildcard[-8:-4] + '.fits'
        #create the directory for the file to be written to if it doesn't already exist
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dir_path = os.path.join(script_dir, date[0], date[1], date[2])
        try:
            os.makedirs(dir_path)
        except OSError:
            pass # already exists
        path = os.path.join(dir_path, file_name)
        #get data and header to be written to the file
        data, header = fits.getdata(wildcard, 0, header = True)
        fits.writeto(path, data, header)
        hdulist.close()
