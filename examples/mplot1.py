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
    return h[0].data


def dsum(i0,i1):
    for i in range(i0,i1):
        ff = 'IMG%05d.FIT' % i
        d1 = d(ff)
        if i == i0: 
            sum0 = 1.0
            sum1 = d1
            sum2 = d1*d1
        else:
            sum0 = sum0 + 1.0
            sum1 = sum1 + d1
            sum2 = sum2 + d1*d1
    sum1 = sum1 / sum0
    sum2 = sum2 / sum0 - sum1*sum1
    return sum1,sum2

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
    sum1,sum2 = dsum(900,951)   #
    show(sum1)
    show(sum2)
    show2(sum1)
    show2(sum2)
    
    show3(sum1,sum2)
