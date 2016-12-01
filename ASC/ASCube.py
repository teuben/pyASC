#! /usr/bin/env python
#
#    quick and dirty processing of the MD All Sky images

from astropy.io import fits
# from scipy.misc import imsave
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import argparse as ap
import os.path
import logging
import time
import Dtime
#import glob

class ASCube(object):
    """
    A cube object. Can load a cube and print its data currently.
    """
    day = 0
    pattern = 'IMG?????.FIT'
    def __init__(self, dirname = ".", box = [], frames = [], maxframes = 10000, 
        template = "IMG%05d.FIT", doload = True):

        self.dirname = dirname
        self.doload = doload
        self.dtime = Dtime.Dtime("ascube")
        self.box = box
        self.frames = frames
        self.maxframes = maxframes
        self.template = template
        self.numfiles = 0
        print("initializing directoy %s" %dirname)
        print(type(dirname), type(self.pattern))
        self.files = []
        self.headers = []
        self.dtime.tag("before iterating through frames")
        for s in self.frames:
            fname = dirname + "/" + self.template % s

            if os.path.isfile(fname):
                self.numfiles += 1
                self.files.append(fname)
            else:
                print("File not found %s" % fname)
        self.dtime.tag("after iterating through frames")
        #self.numFiles = len(files)
        if len(self.files) == 0:
            print("warning: no files %s found" %self.pattern)
        """else:
            print("Found %d files" %len(self.files))
            print("Box: ", box)
            print("Frames: ", frames)"""
        self.data = None
        self.nx = 0
        self.ny = 0
        self.nf = len(self.frames)
        self.dtime.tag("before loading")
        if doload:
            self.load()
        self.dtime.tag("after loading")
        self.dtime.end()

    def load(self):
        """ Load a cube into a 3-dimensional list of values 
        """
        for k in range(self.nf):
            (header, newData) = self.getData(self.files[k], self.box)
            newData = newData * header["BSCALE"] + header["BZERO"]
            self.headers.append(header)
            if k == 0:
                if self.nx == 0:
                    self.nx = newData.shape[1]
                    self.ny = newData.shape[0]
                self.data = np.zeros((self.nf, self.ny, self.nx))
            self.data[k,:,:] = newData
        print(self.data)

        arr = np.copy(self.data)

        for z in range(self.nf):
            if z == 0:
                arr[0] = 0.0
            else:
                arr[z] = self.data[z] - self.data[z-1]
        print(arr)

    def getData(self, fitsfile, box=[]):
        #very specific for 16 bit data, since we want to keep the data in uint16
        newData = fits.open(fitsfile, do_not_scale_image_data=True)
        if len(box)==0:
            return newData[0].header, newData[0].data
        else:
            # figure out 0 vs. 1 based offsets; box is 1 based
            return newData[0].header, newData[0].data[box[1]:box[3], box[0]:box[2]]

    def show(self):
        print("show")

    def __str__(self):
        """ to string function for printing out info about a cube
        """
        string = ""
        string += "Directory: " + self.dirname + "\n"
        string += "Box: " + str(self.box) + "\n"
        string += "Frames: " + str(self.frames) + "\n"
        string += "Max Frames: " + str(self.maxframes) + "\n"
        string += "Template: " + str(self.template) + "\n"
        string += "Load: " + str(self.doload) + "\n"
        return string


def strToIntArray(frames):
    """ converts a string of command line input into an int array 
        for use in determining which frames to use.
    """
    lst = []
    for word in frames.split(','):
        words = word.split(':')
        if len(words) == 1:
            lst.append(int(words[0]))
        elif len(words) == 2:
            if int(words[0]) > int(words[1]):
                lst = lst + list(range(int(words[0]), int(words[1])-1))
            else:
                lst = lst + list(range(int(words[0]), int(words[1])+1))
        elif len(words) == 3:
            if int(words[0]) > int(words[1]):
                lst = lst + list(range(int(words[0]), int(words[1])-1, int(words[2])))
            else:
                lst = lst + list(range(int(words[0]), int(words[1])+1, int(words[2])))
    return lst



def dsum(i0,i1,step = 1, box=[]):
    """ for a range of fits files
        compute the mean and dispersion from the mean
    """
    for i in range(i0,i1+1,step):
        ff = 'IMG%05d.FIT' % i
        h1, d1 = getData(ff,box)
        #very specific for 16 bit data, since we want to keep the data in uint16
        bzero = h1['BZERO']
        bscale = h1['BSCALE']
        if i == i0: 
            sum0 = 1.0
            sum1 = d1*bscale+bzero
            sum2 = sum1*sum1
            #sum1 = d1
            #sum2 = d1*d1
            h = h1
            nx = d1.shape[1]
            ny = d1.shape[0]
            nz = i1 + 1 - i0
            c = np.zeros((nz, ny, nx))
            c[0,:,:] = d1.reshape(ny,nx)
        else:
            sum0 = sum0 + 1.0
            sum1 = sum1 + (d1 * bscale + bzero)
            sum2 = sum2 + (d1 * bscale + bzero) * (d1 * bscale + bzero)
            #sum2 = sum2+d1*d1
            c[i - i0,:,:] = d1.reshape(ny,nx)
    sum1 = sum1 / sum0
    sum2 = sum2 / sum0 - sum1*sum1
    print (type(sum1), type(sum2))    
    return (h,sum1,np.sqrt(sum2),c)

def show(sum):
    """ some native matplotlib display,
        doesn't show pointsources well at all
    """
    ip = plt.imshow(sum)
    plt.show()

def show2(sum):
    """ aplpy is the better viewer clearly
    """
    import aplpy
    fig = aplpy.FITSFigure(sum)
    #fig.show_grayscale()
    fig.show_colorscale()

def show3(sum1,sum2):
    """ aplpy is the better viewer clearly
    """
    import aplpy
    fig = aplpy.FITSFigure(sum1,subplot=(2,2,1))
    #fig = aplpy.FITSFigure(sum2,subplot=(2,2,2),figure=1)
    #fig.show_grayscale()
    fig.show_colorscale()

