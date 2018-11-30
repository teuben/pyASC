#! /usr/bin/env python
#
#   1440 files took about 38 mins
#

from __future__ import print_function
from tkinter import filedialog
from astride import Streak
import glob
import sys
import shutil
import os
import tkinter as tk
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np

def get_arg(argv):
    if len(argv) == 1: 
        return get_int_arg(argv)
    else:
        return get_cmd_arg(argv)    
 
def mk_diff(f0,f1,diff):
    hdu0 = fits.open(f0)
    hdu1 = fits.open(f1)

    h1 = hdu1[0].header

    d0 = hdu0[0].data
    d1 = hdu1[0].data
    if v:
	    print("DEBUG mean/std: %s %s %s %g %g" % (f0,f1,diff,d0.mean(),d0.std()))

    d2 = d1-d0

    fits.writeto(diff,d2,h1,overwrite=True)
 
def get_cmd_arg(argv,shape=.14,area=120,contour=12):
    import argparse as ap
    parser = ap.ArgumentParser()
    parser.add_argument('-i','--filein', nargs=1,help = 'Directory to fits directory') 
    parser.add_argument('-o','--fileout', nargs=1,help = 'Directory to detection folder') 
    parser.add_argument('-s','--shape', nargs=1,help = 'Shape factor') 
    parser.add_argument('-a','--area', nargs=1,help = 'Minimum area to be considered a streak')     
    parser.add_argument('-c','--contour',nargs=1,help = 'blah Control value')
    args=vars(parser.parse_args())
    
    if args['filein'] != None: file_pathin = (args['filein'][0])  
    if args['fileout'] != None: file_pathout = (args['fileout'][0])   
    if args['shape'] != None: shape = float(args['shape'][0])
    if args['area'] != None: area = float(args['area'][0])
    if args['contour'] != None: contour = float(args['contour'][0])
    
    return (file_pathin,file_pathout,shape,area,contour)
    
def get_int_arg(argv):
    #Creates folder input browsers
    winin = tk.Tk()
    winin.withdraw()
    winin.attributes('-topmost', True)
    file_pathin = filedialog.askdirectory(title = "Select input")
    
    #Creates folder output browsers   
    winout = tk.Tk()
    winout.withdraw()
    winout.attributes('-topmost', True)
    file_pathout = filedialog.askdirectory(title = "Select output")
    
    winout.destroy()
    winin.destroy()
    
    #ask user for remaining arguments
    print("\nClicking enter will apply default values, entering a value will change it.")
    nshape = input("Shape value (1=circle, .1=thin oval) (default = 0.14): ")
    if nshape == "":
        shape = .14
    else:
        shape = float(nshape)
    
    narea = input("Minimum area (default = 120): ")
    if narea == "":
        area = 120
    else:
        area = float(narea)
        
    ncontour = input("Contour value (higher=only brighter streaks detected)(default = 12): ")
    if ncontour == "":
        contour = 12
    else:
        contour = float(ncontour)
	
    ndiff = input("Create difference images (default = False): ")
    if ndiff == "":
	    diff = False
    else:
	    diff = ndiff.lower() == 'true'
    
    nv = input("Enable verbose mode (default = False): ")
    if nv == "":
	    v = False
    else:
	    v = nv.lower() == 'true'
    
    
    return(file_pathin,file_pathout,shape,area,contour,diff,v)

def do_dir(d,dsum,shape,area,contour,diff,v):
    """
    process a directory 'd'
    """
    #print("Outputting in directory: " + dsum)
    if dsum == None:
        dsum = d
    else:
        if not os.path.exists(dsum):    
            os.mkdir(dsum)
    num = 0
    detected = 0
    fileCount = 0
    zero = 0

    # debug/verbose
    if v:
        print('DEBUG: shape=%g area=%g contour=%g' % (shape,area,contour))
    
    ffs = glob.glob(d+'/*.FIT') + glob.glob(d+'/*.fit') + \
          glob.glob(d+'/*.FTS') + glob.glob(d+'/*.fts') + \
          glob.glob(d+'/*.FITS') + glob.glob(d+'/*.fits')
    ffs = list(set(ffs))             # needed for dos
    ffs.sort()                       # on linux wasn't sorted, on dos it was  
    f = open(dsum+'/summary.txt','w')   # Creates summary text file 
    f.write('Streaks found in files: \n')   #Creates first line for summary file
    print('Processing %d files' % len(ffs))
    for ff in ffs:
        # creates directory one directory back from the folder which contains fits files
        num = do_one(ff,dsum+'/'+ff[ff.rfind(os.sep)+1:ff.rfind('.')],shape,area,contour) 
        
        if num == 0:
            zero += 1
        else:
            detected += int(num)    #Counter of how many streaks detected
            f.write(ff + '\n') 
        fileCount += 1   #Counter for how many files analyzed         
    # Produce and write summary file 
    f.write('\n' 'Files analyzed: ' + str(fileCount)+ '\n' )
    f.write('Streaks detected: ' + str(detected) + '\n' )
    f.write('Files with no detections: ' + str(zero) + '\n\n\n')
    if diff:
        num = 0
        detected = 0
        fileCount = 0
        zero = 0
        dfs = []
        print('Computing %d differences' % (len(ffs)-1))
        for i in range(len(ffs)-1):
            dfs.append(ffs[i+1]+'.diff')
            mk_diff(ffs[i],ffs[i+1],dfs[i])
        print('Processing %d files' % (len(ffs)-1))
        for df in dfs:
            num = do_one(df,dsum+'/'+df[df.rfind(os.sep)+1:df.find('.')]+'DIFF',shape,area,contour)
            if num == 0:
                zero += 1
            else:
                detected += int(num)    #Counter of how many streaks detected
                f.write(df + '\n') 
            fileCount += 1   #Counter for how many files analyzed         
        # Produce and write summary file 
        f.write('\n' 'Files analyzed: ' + str(fileCount)+ '\n' )
        f.write('Streaks detected: ' + str(detected) + '\n' )
        f.write('Files with no detections: ' + str(zero) + '\n')
        f.close()
    else:
        f.close()

def do_one(ff,output_path=None,shape=None,area=None,contour=None):
    """
    process a directory one fits-file (ff)
    """
    # Read a fits image and create a Streak instance.
    streak = Streak(ff,output_path=output_path)
    # Detect streaks.
    
    # streak.shape_cut = .14
    # streak.area_cut = 120
    # streak.contour_threshold = 12
    
    #Customization of values
    streak.shape_cut = shape
    streak.area_cut = area
    streak.contour_threshold = contour
    
    streak.detect()
    # Write outputs and plot figures.
    streak.write_outputs()
    streak.plot_figures()
    streakfile=output_path+"/streaks.txt"
    fp=open(streakfile)
    lines=fp.readlines()
    fp.close()
    #print("streaks found %d" % (len(lines)-1))
    #print("%d " % (len(lines)-1))
    n = len(lines)-1
    if n == 0:
        sys.stdout.write('.')
    elif n < 10:
        sys.stdout.write('%d' % n)
    else:
        sys.stdout.write('*')
    sys.stdout.flush()
    
    #Delete/move files
    #if n == 0:
       # shutil.rmtree(output_path)
    
    return int(n)
#def do_one(ff,output_path=None,shape=None,area=None,contour=None):  BACKUP
    """
    process a directory one fits-file (ff)
    """
    # Read a fits image and create a Streak instance.
    streak = Streak(ff,output_path=output_path)
    # Detect streaks.
    
    # streak.shape_cut = .14
    # streak.area_cut = 120
    # streak.contour_threshold = 12
    
    #Customization of values
    streak.shape_cut = shape
    streak.area_cut = area
    streak.contour_threshold = contour
    
    streak.detect()
    # Write outputs and plot figures.
    streak.write_outputs()
    streak.plot_figures()
    streakfile=output_path+"/streaks.txt"
    fp=open(streakfile)
    lines=fp.readlines()
    fp.close()
    #print("streaks found %d" % (len(lines)-1))
    #print("%d " % (len(lines)-1))
    n = len(lines)-1
    if n == 0:
        sys.stdout.write('.')
    elif n < 10:
        sys.stdout.write('%d' % n)
    else:
        sys.stdout.write('*')
    sys.stdout.flush()
    
    #Delete/move files
    if n == 0:
        shutil.rmtree(output_path)
    
    return int(n)
    
#do_one('20151108_MD01_raw/IMG00681.FIT')
#do_dir('20151108_MD01_raw')

if __name__ == '__main__':    
    (file_pathin,file_pathout,shape,area,contour,diff,v) = get_arg(sys.argv)
    #Prints selected folders
    print("Running in data directory %s" % file_pathin)
    print("Outputting in data directory %s" % file_pathout)
    do_dir(file_pathin,file_pathout,shape,area,contour,diff,v)
    
    #print("Running in data directory %s" % sys.argv[1])
    #do_dir(sys.argv[1],sys.argv[2])
