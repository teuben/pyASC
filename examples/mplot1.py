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


def dsum(i0,i1,step = 1, box=[]):
    """ for a range of fits files
        compute the mean and dispersion from the mean
    """
    for i in range(i0,i1+1,step):
        ff = 'IMG%05d.FIT' % i
        h1, d1 = d(ff,box)
        if i == i0: 
            sum0 = 1.0
            sum1 = d1
            sum2 = d1*d1
            h = h1
            nx = d1.shape[1]
            ny = d1.shape[0]     #   d1[ny][nx]
            c = d1.reshape(1,ny,nx)
        else:
            sum0 = sum0 + 1.0
            sum1 = sum1 + d1
            sum2 = sum2 + d1*d1
            c = np.append(c,d1.reshape(1,ny,nx),axis=0)
    sum1 = sum1 / sum0
    sum2 = sum2 / sum0 - sum1*sum1
    return h,sum1,np.sqrt(sum2),c

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
    parser.add_argument('-f', '--frame', nargs = '*', required = True, type = int, help = 'Starting and ending parameters for the frames analyzed')
    parser.add_argument('-b', '--box', nargs = 4, type = int, help = 'Coordinates for the bottom left corner and top right corner of a rectangle of pixels to be analyzed from the data. In the structure x1, y1, x2, y2 (1 based numbers)')
    args = vars(parser.parse_args())

    if len(args['frame']) >= 2:
        start = args['frame'][0]           # starting frame (IMGnnnnn.FIT)
        end   = args['frame'][1]           # ending frame
        if len(args['frame']) == 3:
            step = args['frame']
        else:
            step = 1
    else:
        raise Exception,"-f needs at least 2 arguments"
    box   = args['box']                # BLC and TRC
    if box == None:
        box = []

    # compute the average and dispersion of the series        
    h1,sum1,sum2,cube = dsum(start,end,step,box=box)           # end can be uninitialized here might throw an error?
    nz = cube.shape[0]
    
    # delta X and Y images
    dsumy = sum1 - np.roll(sum1, 1, axis = 0)    # change in the y axis
    dsumx = sum1 - np.roll(sum1, 1, axis = 1)    # change in the x axis

    # write them to FITS
    fits.writeto('dsumx.fits', dsumx, h1, clobber=True)
    fits.writeto('dsumy.fits', dsumy, h1, clobber=True)
    fits.writeto('sum1.fits', sum1, h1, clobber=True)
    fits.writeto('sum2.fits', sum2, h1, clobber=True)
    # 3D cube to
    h1['NAXIS']  = 3
    h1['NAXIS3'] = nz
    fits.writeto('cube.fits', cube, h1, clobber=True)

    # display a few
    #show(sum1)
    #show(sum2)
    show2(sum1)
    show2(sum2)
    #show3(sum1,sum2)

    # plot the sum1 and sum2 correllation (glueviz should do this)
    s1 = sum1.flatten()
    s2 = sum2.flatten()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(s1,s2)
    plt.show()
    

