#! /usr/bin/env python
#
#   1440 files took about 38 mins
#

from __future__ import print_function
from tkinter import filedialog
from tkinter import *
from astride import Streak
import glob
import sys
import shutil
import os
import tkinter as tk
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np


class _Args:
    file_pathin = ""
    file_pathout = ""
    shape = 0.14
    area = 120
    contour = 12
    diff = False
    v = False
    start_frame = -1
    end_frame = -1
    
def get_arg(argv):
    
    arguments = _Args()
    
    if len(argv) == 1: 
        return get_int_arg(arguments)
    else:
        return get_cmd_arg(argv, arguments)    
 
def mk_diff(f0,f1,diff, v):
    hdu0 = fits.open(f0, ignore_missing_end=True)
    hdu1 = fits.open(f1, ignore_missing_end=True)
 
    h1 = hdu1[0].header

    d0 = hdu0[0].data
    d1 = hdu1[0].data
    if v:
        print("DEBUG mean/std: %s %s %s %g %g" % (f0,f1,diff,d0.mean(),d0.std()))

    d2 = d1-d0

    fits.writeto(diff,d2,h1,overwrite=True)
 
def get_cmd_arg(argv, arguments):
    import argparse as ap
    parser = ap.ArgumentParser()
    parser.add_argument('-i','--filein', nargs=1,help = 'Directory to input fits directory') 
    parser.add_argument('-o','--fileout', nargs=1,help = 'Directory to output folder') 
    parser.add_argument('-s','--shape', nargs=1,help = 'Shape factor') 
    parser.add_argument('-a','--area', nargs=1,help = 'Minimum area to be considered a streak')     
    parser.add_argument('-c','--contour',nargs=1,help = 'Control value')
    parser.add_argument('-d','--difference',action = 'store_const',const = arguments.diff , help = 'Create difference images')
    parser.add_argument('-v','--verbose', action = 'store_const', const = arguments.v, help = 'Verbose')
    parser.add_argument('-S','--start',nargs = 1, help = 'Start Frame (starts at 1)')
    parser.add_argument('-E','--end', nargs = 1, help = 'End Frame')
    args=vars(parser.parse_args())
    
    if args['filein'] != None: arguments.file_pathin = (args['filein'][0])  
    if args['fileout'] != None: arguments.file_pathout = (args['fileout'][0]) 
    else:
        if arguments.file_pathin.endswith("/"):
            arguments.file_pathout = arguments.file_pathin[0:len(arguments.file_pathin) -1] + "-output"
        else:
            arguments.file_pathout = arguments.file_pathin +"-output"
    if args['shape'] != None: arguments.shape = float(args['shape'][0])
    if args['area'] != None: arguments.area = float(args['area'][0])
    if args['contour'] != None: arguments.contour = float(args['contour'][0])
    if args['difference'] != None: arguments.diff = True
    if args['verbose'] != None: arguments.v = True
    if args['start'] != None: arguments.start_frame = int(args['start'][0])
    if args['end']   != None: arguments.end_frame   = int(args['end'][0])

    return arguments
    
def get_int_arg(arguments):
    
    #Creates folder input browsers
    winin = tk.Tk()
    winin.withdraw()
    winin.attributes('-topmost', True)
    arguments.file_pathin = filedialog.askdirectory(title = "Select input")
    
    #Creates folder output browsers   
    winout = tk.Tk()
    winout.withdraw()
    winout.attributes('-topmost', True)
    arguments.file_pathout = filedialog.askdirectory(title = "Select output")
    
    winout.destroy()
    winin.destroy()
    
    top = tk.Tk()
    nshape = tk.StringVar()
    narea = tk.StringVar()
    ncontour = tk.StringVar()
    nstart_frame = tk.StringVar()
    nend_frame = tk.StringVar()
    ndiff = tk.IntVar()
    nv = tk.IntVar()
    
    L1 = Label(top, text="Shape value (1=circle, .1=thin oval) (default = 0.14): ")
    L1.pack()
    eshape = Entry(top, textvariable=nshape)
    #nshape = float(nshape.get())
    eshape.pack()
    
    L2 = Label(top, text="Minimum area (default = 120): ")
    L2.pack()
    earea = Entry(top, textvariable=narea)
    #narea = float(narea.get())
    earea.pack()
    
    L3 = Label(top, text="Contour value (higher=only brighter streaks detected)(default = 12): ")
    L3.pack()
    econtour = Entry(top, textvariable=ncontour)
    #ncontour = float(ncontour.get())
    econtour.pack()
    
    L4 = Label(top, text="Frame at which to start (default = 1)")
    L4.pack()
    estart_frame = Entry(top, textvariable=nstart_frame)
    #nstart_frame = float(nstart_frame.get())
    estart_frame.pack()
    
    L5 = Label(top, text="Last frame (does not process last frame) (default goes to end)")
    L5.pack()
    eend_frame = Entry(top, textvariable=nend_frame)
    #nend_frame = float(nend_frame.get())
    eend_frame.pack()
    
    C1 = Checkbutton(top, text = "Difference imaging (default = false)", variable = ndiff, \
                     onvalue=1, offvalue=0 )
    C2 = Checkbutton(top, text = "Verbose mode (default = false)", variable = nv, \
                 onvalue = 1, offvalue = 0 )
    

    def save(nshape, narea, ncontour, nstart_frame, nend_frame, ndiff, nv):
        if len(nshape.get()) != 0:
            arguments.shape = float(nshape.get())
  
        if len(narea.get()) != 0:
            arguments.area = float(narea.get())
            
        if len(ncontour.get()) != 0:
            arguments.contour = float(ncontour.get())
           
        if len(nstart_frame.get()) != 0:
            arguments.start_frame = int(nstart_frame.get())
            
        if len(nend_frame.get()) != 0:
            arguments.end_frame = int(nend_frame.get())
        
        arguments.diff = ndiff.get()
      
        arguments.v = nv.get()
        
        top.destroy()
    
    s = Button(top, text="Save Values", command=lambda: save(nshape, narea, ncontour, nstart_frame, nend_frame, ndiff, nv))
    
    C1.pack()
    C2.pack()
    s.pack()
    top.mainloop()
          
    return(arguments)

def do_dir(arguments):
    """
    process a directory 'd'
    """
    #print("Outputting in directory: " + dsum)
   
    if not os.path.exists(arguments.file_pathout):    
        os.mkdir(arguments.file_pathout)

    num = 0
    detected = 0
    fileCount = 0
    zero_image = 0
    bad_image = 0
    bad_image_paths = []

    # debug/verbose
    if arguments.v:
          print('DEBUG: shape=%g area=%g contour=%g' % (arguments.shape,arguments.area,arguments.contour))
    
    ffs = glob.glob(arguments.file_pathin+'/*.FIT') + glob.glob(arguments.file_pathin+'/*.fit') + \
          glob.glob(arguments.file_pathin+'/*.FTS') + glob.glob(arguments.file_pathin+'/*.fts') + \
          glob.glob(arguments.file_pathin+'/*.FITS') + glob.glob(arguments.file_pathin+'/*.fits')
    ffs = list(set(ffs))             # needed for dos
    ffs.sort()                       # on linux wasn't sorted, on dos it was  
    f = open(arguments.file_pathout+'/summary.txt','w')   # Creates summary text file
    f.write('Streaks found in files: \n')   #Creates first line for summary file

    sf = arguments.start_frame
    ef = arguments.end_frame
    
    if sf <= 0:
        sf = 1
    
    if ef <= 0 or ef > len(ffs):
        ef = len(ffs)
    
    if ef < sf:
        temp = sf
        sf = ef
        ef = temp

    print('Processing %d files from %d to %d' % ((ef-sf+1), sf, ef))
    for ff in ffs[sf-1:ef]:
        # creates directory one directory back from the folder which contains fits files
        
        num = do_one(ff,arguments.file_pathout+'/'+ff[ff.rfind(os.sep)+1:ff.rfind('.')],arguments.shape,arguments.area,arguments.contour)
        
        
        if num == 0:
            zero_image += 1
        elif num < 0:
            bad_image += 1
            bad_image_paths.append(ff)
        else:
            detected += int(num)    #Counter of how many streaks detected
            f.write(ff + '\n') 
        fileCount += 1   #Counter for how many files analyzed         
    print("\n")
    # Produce and write summary file 
    f.write('\n' 'Files analyzed: ' + str(fileCount)+ '\n' )
    f.write('Streaks detected: ' + str(detected) + '\n' )
    f.write('Files with no detections: ' + str(zero_image) + '\n')
    f.write('Bad files: ' + str(bad_image)+ '\n')
    
    temp_string = "\n"
    temp_string = temp_string.join(bad_image_paths)
    f.write(temp_string)
    
    f.write('\n\n')

    if arguments.diff:
        f.write('Streaks found in Files: \n')
        num = 0
        detected = 0
        fileCount = 0
        zero_image = 0
        bad_image = 0
        bad_image_paths = []
        dfs = []
#        print('Computing %d differences' % (ef-sf+1))
        for i in range(len(ffs)-1):
            dfs.append(arguments.file_pathout+'/'+ffs[i+1][len(arguments.file_pathin):]+'DIFF')
#            mk_diff(ffs[i],ffs[i+1],dfs[i],v)
            
        if sf <= 0:
            sf = 1

        if ef <= 0 or ef > len(dfs):
            ef = len(dfs)
        
        if ef <= sf:
            temp = sf
            sf = ef
            ef = temp

        print('Processing %d files from %d to %d' % ((ef-sf+1), sf, ef))
        i = sf-1
        for df in dfs[sf-1:ef]:
            try:
                mk_diff(ffs[i],ffs[i+1],dfs[i],arguments.v)
                # num = do_one(df,dsum+'/'+df[df.rfind(os.sep)+1:df.rfind('.')],shape,area,contour)
                #diff_file = dsum+'/'+df[df.rfind(os.sep)+1:df.find('.')]+'DIFF'
            
                #directory one directory back
                new_dir = arguments.file_pathout+'/'+df[df.rfind(os.sep)+1:df.rfind('.')]+'DIFF'
                num = do_one(df,new_dir,arguments.shape,arguments.area,arguments.contour)
                os.remove(df)
                
            except:
                num=-1
                sys.stdout.write('X')
            


            if num == 0:
                zero_image += 1
            elif num < 0:
                bad_image += 1
                bad_image_paths.append(df)
            else:
                detected += int(num)    #Counter of how many streaks detected
                f.write(df + '\n') 
            fileCount += 1   #Counter for how many files analyzed         
            i += 1
        print("\n")
        # Produce and write summary file 
        f.write('\n' 'Files analyzed: ' + str(fileCount)+ '\n' )
        f.write('Streaks detected: ' + str(detected) + '\n' )
        f.write('Files with no detections: ' + str(zero_image) + '\n')
        f.write('Bad files: ' + str(bad_image)+ '\n')

        temp_string = "\n"
        temp_string = temp_string.join(bad_image_paths)
        f.write(temp_string)

        f.close()
    else:
        f.close()

def do_one(ff,output_path,shape,area,contour):
    """
    process a directory one fits-file (ff)
    """
    try:
        # Read a fits image and create a Streak instance.
        streak = Streak(ff,output_path=output_path)
        # Detect streaks.
        
        # streak.shape_cut = .14
        # streak.area_cut = 120
        # streak.contour_threshold = 12
        
        # Customization of values
        streak.shape_cut = shape
        streak.area_cut = area
        streak.contour_threshold = contour
        
        streak.detect()
        
        n = len(streak.streaks)
    
    except:
        n = -1

    if n > 0:
    # Write outputs and plot figures.
        streak.write_outputs()
        streak.plot_figures()

    if n == 0:
        sys.stdout.write('.')
    elif n < 0:
        sys.stdout.write('X')
    elif n < 10:
        sys.stdout.write('%d' % n)
    else:
        sys.stdout.write('*')
    sys.stdout.flush()
    
    return n
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

    n = len(streak.streaks)


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
    try:
        arguments = get_arg(sys.argv)
    except:
        print("An error occored getting the arguments for the function\n")
        sys.exit(0)
        
    


    #Prints selected folders
    print("Running in data directory %s" % arguments.file_pathin)
    print("Outputting in data directory %s" % arguments.file_pathout)
    do_dir(arguments)
    
    #print("Running in data directory %s" % sys.argv[1])

    #do_dir(sys.argv[1],sys.argv[2])


