#! /usr/bin/env python
#
#    quick and dirty processing of the All Sky images

from astropy.io import fits
from scipy.misc import imsave
from scipy import ndimage
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import numpy.ma as ma
import aplpy
import argparse as ap
import os.path
import logging
import time
import Dtime
import networkx as nx
from radial_data import radial_data
#import glob

class ASCube(object):
    """
    A cube object. Can load a cube and print its data currently.
    """
    day = 0
    pattern = 'IMG?????.FIT'
    def __init__(self, dirname = ".", box = [], frames = [], maxframes = 10000, 
                 template = "IMG%05d.FIT", doload = True, difference = False, sig_frames = False, meteor = True,
                 xslice = -1, yslice = -1,
                 debug = True):

        self.dirname   = dirname
        self.doload    = doload
        self.dtime     = Dtime.Dtime("ascube")
        self.debug     = debug
        self.box       = box
        self.frames    = frames
        self.maxframes = maxframes
        self.template  = template
        self.numfiles  = 0
        self.files     = []
        self.headers   = []
        self.xslice    = xslice
        self.yslice    = yslice
        print('PJT',xslice,yslice)
        if xslice>0 or yslice>0:
            self.radial   = False
        else:
            self.radial   = True   # hack
            self.rmax     = 450            # fixme
            self.center   = (716,465)      # fixme
            self.nxy      = (1392,1040)    # fixme
        print("initializing directory %s" %dirname)
        print(type(dirname), type(self.pattern))
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
        else:
            print("Found %d files" %len(self.files))
            print("Box: ", box)
            print("Frames: ", frames)
        self.data = None
        self.nx = 0
        self.ny = 0
        self.nf = len(self.frames)
        self.dtime.tag("before loading")
        if doload:
            self.load()
            if difference:
                self.computeDifference()
                if sig_frames:
                    self.get_spec()
            if meteor:
                self.computeDifference()
                self.find_met()
        self.dtime.tag("after loading")
        self.dtime.end()

    def load(self):
        """ Load a cube into a 3-dimensional list of values 
        """
        for k in range(self.nf):
            (header, newData) = self.getData(self.files[k], self.box)
            newData = newData * header["BSCALE"] + header["BZERO"]
            self.headers.append(header)
            if self.radial:
                if k==0:
                    nx = newData.shape[1]
                    ny = newData.shape[0]
                    x1 = np.arange(1,nx+1) - self.center[0]
                    y1 = np.arange(1,ny+1) - self.center[1]
                    x,y = np.meshgrid(y1,x1)
                    print('pjt',newData.shape)
                    self.ndim = 0                    
                r = radial_data(newData.T,x=x,y=y,rmax=self.rmax)
            if k == 0:
                if self.nx == 0:
                    self.nx = newData.shape[1]
                    self.ny = newData.shape[0]
                if self.radial:
                    self.nr = len(r.r)
                    self.mean   = np.zeros((self.nf, self.nr))
                    self.std    = np.zeros((self.nf, self.nr))
                    self.median = np.zeros((self.nf, self.nr))
                elif self.xslice > 0:
                    self.data = np.zeros((self.nf, self.ny))
                    self.ndim = 2
                elif self.yslice > 0:
                    self.data = np.zeros((self.nf, self.nx))
                    self.ndim = 2                    
                else:
                    self.data = np.zeros((self.nf, self.ny, self.nx))
                    self.ndim = 3                    
            if self.radial:
                self.mean[k,:]   = r.mean
                self.std[k,:]    = r.std
                self.median[k,:] = r.median
                print(k)
            elif self.xslice > 0:
                self.data[k,:] = newData[:,self.xslice]
            elif self.yslice > 0:
                self.data[k,:] = newData[self.yslice,:]
            else:
                self.data[k,:,:] = newData
                                         
        #print(self.data)

    def computeDifference(self):
        for z in range(self.nf):
            if z == self.nf-1:
                self.data[z] = 0.0
            else:
                self.data[z] = self.data[z] - self.data[z+1]

    def iterate(self, arr):
        # iterate through a matrix and accept or reject various indices
        m = np.mean(arr)
        s = np.std(arr)
        ym = ma.masked_inside(arr, m-5*s, m+5*s)
        return ma.where(ym == False)

    def get_spec(self):
        modData = []
        for z in range(self.nf):
            if(len(self.iterate(self.data[z])) > 600):
                modData.append(self.data[z])
        self.data = modData  

    def find_met(self):
        for z in range(self.nf):
            ym = self.iterate(self.data[z])
            shapes = self.find_shapes(ym)
            for s in shapes:
                print(linreg_accept(s))  

    def adj(self, i1, i2):
        # Are the two indices adjacent
        if (i1[0] == i2[0]):
            return i1[1] == i2[1] + 1 or i1[1] == i2[1] - 1
        elif (i1[1] == i2[1]):
            return i1[0] == i2[0] + 1 or i1[0] == i2[0] - 1
        else:
            return False

    def build_graph(self, arr):
        # Build the graph, being sure to add every index
        gr = nx.Graph()
        for i in arr:
            for j in arr:
                if self.adj(i, j):
                    gr.add_edge(i, j)
            gr.add_node(i)
        return gr

    def dfs_mod(self, graph, node, arr):
        # Do a DFS. Each time DFS is performed on a node, remove that node from the array.
        visited, stack = set(), [node]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                stack.extend(graph.neighbors(vertex))
                arr.remove(vertex)
        return list(visited)

    def find_shapes(self, tup):
        # apply the modified DFS to each node
        arr = []
        for (x,y) in zip(tup[0],tup[1]):
            arr.append((x,y))
        graph = self.build_graph(arr)
        shapes = []
        for i in arr:
            shapes.insert(0, self.dfs_mod(graph, i, arr))
        return shapes

    def linreg_accept(self, arr):
        # apply linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(arr)
        return r_value

    def getData(self, fitsfile, box=[]):
        # very specific for 16 bit data, since we want to keep the data in uint16
        newData = fits.open(fitsfile, do_not_scale_image_data=True)
        if len(box)==0:
            return newData[0].header, newData[0].data
        else:
            # figure out 0 vs. 1 based offsets; box is 1 based
            return newData[0].header, newData[0].data[box[1]:box[3], box[0]:box[2]]

    def downsample(self, zoom=0.5, order=3):
        self.data = ndimage.zoom(self.data, [1,zoom,zoom], order=order)

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
        string += "Ndim: " + str(self.ndim) + "\n"
        string += "Data: " + str(self.data) + "\n"
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
    fig = aplpy.FITSFigure(sum)
    #fig.show_grayscale()
    fig.show_colorscale()

def show3(sum1,sum2):
    """ aplpy is the better viewer clearly
    """
    fig = aplpy.FITSFigure(sum1,subplot=(2,2,1))
    #fig = aplpy.FITSFigure(sum2,subplot=(2,2,2),figure=1)
    #fig.show_grayscale()
    fig.show_colorscale()

