import numpy as np
import aplpy as apl
import argparse as ap
from astropy.io import fits
import scipy.ndimage.filters as filters
import mplot1 as mp

if __name__ == '__main__':
    
    #--start, -s n
    #--end, -e n
    #--box x1 y1 x2 y2
    parser = ap.ArgumentParser(description='Plotting .fits files.')
    parser.add_argument('-f', '--frame', nargs = 2, required = True, type = int, help = 'Starting and ending parameters for the frames analyzed')
    parser.add_argument('-b', '--box', nargs = 4, type = int, help = 'Coordinates for the bottom left corner and top right corner of a rectangle of pixels to be analyzed from the data. In the structure x1, y1, x2, y2 (1 based numbers)')
    args = vars(parser.parse_args())

    start = args['frame'][0]           # starting frame (IMGnnnnn.FIT)
    end   = args['frame'][1]           # ending frame
    box   = args['box']                # BLC and TRC
    if box == None:
        box = []

    # compute the average and dispersion of the series        
    h1,sum1,sum2,cube = mp.dsum(start,end,box)           # end can be uninitialized here might throw an error?
    n = 5
    msum = filters.median_filter(sum1, size = (n,n))
    rmsum = (sum1 - msum) / msum
    mp.show(msum)
    fits.writeto('sum1.fits', sum1, h1, clobber=True)
    fits.writeto('msum.fits', msum, h1, clobber=True)
    fits.writeto('rmsum.fits', rmsum, h1, clobber=True)