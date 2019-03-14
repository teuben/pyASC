# /usr/bin/env python
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
 
def get_cmd_arg(argv,shape=.14,area=120,contour=12,diff = False, v = False, start_frame = -1, end_frame = -1):
    import argparse as ap
    parser = ap.ArgumentParser()
    parser.add_argument('-i','--filein', nargs=1,help = 'Directory to fits directory') 
    parser.add_argument('-o','--fileout', nargs=1,help = 'Directory to detection folder') 
    parser.add_argument('-s','--shape', nargs=1,help = 'Shape factor') 
    parser.add_argument('-a','--area', nargs=1,help = 'Minimum area to be considered a streak')     
    parser.add_argument('-c','--contour',nargs=1,help = 'blah Control value')
    parser.add_argument('-d','--difference',action = 'store_const',const = diff , help = 'Create difference images')
    parser.add_argument('-v','--verbose', action = 'store_const', const = v, help = 'Verbose')
    parser.add_argument('-S','--start',nargs = 1, help = 'Start Frame')
    parser.add_argument('-E','--end', nargs = 1, help = 'End Frame')
    args=vars(parser.parse_args())
    
    if args['filein'] != None: file_pathin = (args['filein'][0])  
    else:
         list_dir = glob.glob('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] to [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
         file_pathin = max(list_dir, key = lambda f:datetime.date(int(f[0:4]),int(f[5:7]),int(f[8:10])))
    if args['fileout'] != None: file_pathout = (args['fileout'][0]) 
    else:
        if file_pathin.endswith("/"):
            file_pathout = file_pathin[0:len(file_pathin) -1] + "-output"
        else:
            file_pathout = file_pathin +"-output"
    if args['shape'] != None: shape = float(args['shape'][0])
    if args['area'] != None: area = float(args['area'][0])
    if args['contour'] != None: contour = float(args['contour'][0])
    if args['difference'] != None: diff = True
    if args['verbose'] != None: v = True
    if args['start'] != None: start_frame = int(args['start'][0])
    if args['end']   != None: end_frame   = int(args['end'][0])

    return (file_pathin,file_pathout,shape,area,contour,diff, v, start_frame, end_frame)
    
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

    ndiff = input("Difference imaging (default = false)")
    if ndiff == "":
        diff = False
    else:
        diff = ndiff.lower() == 'true'
		
    nv = input("Verbose mode (enter t or f) (default = false)")
    if nv == "":
        v = False
    if nv == "t":
        v = True
    if nv == "f":
        v = False
    
    nstart_frame = input("Frame at which to start (default = 1)")
    if nstart_frame == "":
        start_frame = -1
    else:
        start_frame=float(nstart_frame)
        
    nend_frame = input("Last frame (does not process last frame) (default goes to end)")
    if nend_frame == "":
        end_frame = -1
    else:
        end_frame=float(nend_frame)
        
    return(file_pathin,file_pathout,shape,area,contour,diff,v,start_frame,end_frame)

def do_dir(d,dsum,shape,area,contour,diff, v, start_frame, end_frame):
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
    zero_image = 0
    bad_image = 0
    bad_image_paths = []

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
    
    sf = start_frame
    ef = end_frame
    
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
        
        num = do_one(ff,dsum+'/'+ff[ff.rfind(os.sep)+1:ff.rfind('.')],shape,area,contour) 

        
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

    if diff:
        f.write('Streaks found in Files: \n')
        num = 0
        detected = 0
        fileCount = 0
        zero_image = 0
        bad_image = 0
        bad_image_paths = []
        dfs = []
        print('Computing %d differences' % (ef-sf))
        for i in range(len(ffs)-1):
            dfs.append(dsum+'/'+ffs[i+1][len(d)+1:]+'DIFF')
#            mk_diff(ffs[i],ffs[i+1],dfs[i],v)

        if sf <= 0:
            sf = 1

        if ef <= 0 or ef > len(dfs):
            ef = len(dfs)
        
        if ef < sf:
            temp = sf
            sf = ef
            ef = temp

        print('Processing %d files from %d to %d' % ((ef-sf+1), sf, ef))
        i = sf-1
        for df in dfs[sf-1:ef]:
            mk_diff(ffs[i],ffs[i+1],dfs[i],v)
            # num = do_one(df,dsum+'/'+df[df.rfind(os.sep)+1:df.rfind('.')],shape,area,contour)
            #diff_file = dsum+'/'+df[df.rfind(os.sep)+1:df.find('.')]+'DIFF'
            
            #directory one directory back
            new_dir = dsum+'/'+df[df.rfind(os.sep)+1:df.rfind('.')]+'DIFF'
            num = do_one(df,new_dir,shape,area,contour) 
            os.remove(df)


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
    (file_pathin,file_pathout,shape,area,contour,diff,v, start_frame, end_frame) = get_arg(sys.argv)
    #Prints selected folders
    print("Running in data directory %s" % file_pathin)
    print("Outputting in data directory %s" % file_pathout)
    do_dir(file_pathin,file_pathout,shape,area,contour,diff,v, start_frame, end_frame)
    
    #print("Running in data directory %s" % sys.argv[1])
#do_dir(sys.argv[1],sys.argv[2])