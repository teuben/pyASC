#! /usr/bin/env python
#
#    quick and dirty processing of the MD All Sky images

from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import aplpy

def d(ff):
    h = fits.open(ff)
    return h[0].header, h[0].data


def dsum(i0,i1):
    for i in range(i0,i1):
        ff = 'IMG%05d.FIT' % i
        h1, d1 = d(ff)
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
    return h,sum1,sum2

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
    h1,sum1,sum2 = dsum(180,184)   #
    dsumy = sum2 - np.roll(sum2, 1, axis = 0) #change in the y axis
    dsumx = sum2 - np.roll(sum2, 1, axis = 1) #change in the x axis
    show(sum1)
    show(sum2)
    show2(sum1)
    show2(sum2)
    
    show3(sum1,sum2)
    
    
    fits.writeto('dsumx.fits', dsumx, h1, clobber=True)
    fits.writeto('dsumy.fits', dsumy, h1, clobber=True)
    fits.writeto('sum1.fits', sum1, h1, clobber=True)
    fits.writeto('sum2.fits', sum2, h1, clobber=True)
