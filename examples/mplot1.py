#! /usr/bin/env python
#
#    quick and dirty processing of the MD All Sky images

from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import aplpy
import argparse as ap

def d(ff,box=[]):
    h = fits.open(ff)
    if len(box)==0:
        return h[0].header, h[0].data
    else:
        # figure out 0 vs. 1 based offsets; box is 1 based
        return h[0].header, h[0].data[box[1]:box[3], box[0]:box[2]]


def dsum(i0,i1, box=[]):
    """ for a range of fits files
        compute the mean and dispersion from the mean
    """
    for i in range(i0,i1):
        ff = 'IMG%05d.FIT' % i
        h1, d1 = d(ff,box)
        if i == i0: 
            sum0 = 1.0
            sum1 = d1
            sum2 = d1*d1
            h = h1
        else:
            sum0 = sum0 + 1.0
            sum1 = sum1 + d1
            sum2 = sum2 + d1*d1
    sum1 = sum1 / sum0
    sum2 = sum2 / sum0 - sum1*sum1
    return h,sum1,np.sqrt(sum2)

def show(sum):
    """ some native matplotlib display,
    doesn't show pointsources well at all
    """
    ip = plt.imshow(sum)
    plt.show()

def show2(sum):
    """ aplpy is the better viewer clearly
    """
    fig = aplpy.FITSFigure(sum)
    fig.show_grayscale()

def show3(sum1,sum2):
    """ aplpy is the better viewer clearly
    """
    fig = aplpy.FITSFigure(sum1,subplot=(2,2,1))
    #fig = aplpy.FITSFigure(sum2,subplot=(2,2,2),figure=1)
    fig.show_grayscale()


if __name__ == '__main__':
    #sum1,sum2 = dsum(130,500)   #star
    #sum1,sum2 = dsum(600,700)   #6 clouds
    #sum1,sum2 = dsum(500,600)   #7 star
    #sum1,sum2 = dsum(700,800)   #9 clouds
    #sum1,sum2 = dsum(800,900)   #8 clouds + star
    
    #--start, -s n
    #--end, -e n
    #--box x1 y1 x2 y2
    parser = ap.ArgumentParser(description='Plotting .fits files.')
    parser.add_argument('-s', '--start', required = True, type = int, help = 'Starting parameter for fits files')
    parser.add_argument('-e', '--end', required = True, type = int, help = 'Ending parameter for the fits files')
    parser.add_argument('-b', '--box', nargs = 4, type = int, help = 'Coordinates for the bottom left corner and top right corner of a rectangle of pixels to be analyzed from the data. In the structure x1, y1, x2, y2 (1 based numbers)')
    args = vars(parser.parse_args())

    start = args['start']              # starting frame (IMGnnnnn.FIT)
    end   = args['end']                # ending frame
    box   = args['box']                # BLC and TRC
    if box == None:
        box = []

    h1,sum1,sum2 = dsum(start,end,box) # The fact that end can be uninitialized here might throw an error
    #if args['box'] != None:
       # sum1 = sum1[args['box'][0]:args['box'][2]][args['box'][1]:args['box'][3]]
       # sum2 = sum2[args['box'][0]:args['box'][2]][args['box'][1]:args['box'][3]]
    dsumy = sum1 - np.roll(sum1, 1, axis = 0) #change in the y axis
    dsumx = sum1 - np.roll(sum1, 1, axis = 1) #change in the x axis
        
    fits.writeto('dsumx.fits', dsumx, h1, clobber=True)
    fits.writeto('dsumy.fits', dsumy, h1, clobber=True)
    fits.writeto('sum1.fits', sum1, h1, clobber=True)
    fits.writeto('sum2.fits', sum2, h1, clobber=True)

    
    show(sum1)
    show(sum2)
    show2(sum1)
    show2(sum2)
    
    show3(sum1,sum2)

    s1 = sum1.flatten()
    s2 = sum2.flatten()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(s1,s2)
    plt.show()
    

