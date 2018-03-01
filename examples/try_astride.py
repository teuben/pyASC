#! /usr/bin/env python
#
#   1440 files took about 38 mins
#

from __future__ import print_function

from astride import Streak
import glob
import sys
import shutil
import os

def do_dir(d,dsum=None):
    """
    process a directory 'd'
    """
    print(d)
    print(dsum)
    if dsum == None:
        dsum = d
    else:
        if not os.path.exists(dsum):    
            os.mkdir(dsum)
    num = 0
    detected = 0
    fileCount = 0
    zero = 0
    ffs = glob.glob(d+'/*.FIT*')     # results in a non-numeric order
    ffs.sort()                       # on linux wasn't sorted, on dos it was
    f = open(dsum+'/summary.txt','w')   # Creates summary text file 
    f.write('Streaks found in files: \n')   #Creates first line for summary file
    for ff in ffs:
        # creates directory one directory back from the folder which contains fits files
        num = do_one(ff,dsum+'/'+ff[ff.rfind(os.sep)+1:ff.rfind('.')]) 
        if num == 0:
            zero += 1
        else:
            detected += int(num)    #Counter of how many streaks detected
            f.write(ff + '\n') 
        fileCount += 1   #Counter for how many files analyzed         
    # Produce and write summary file 
    f.write('\n' 'Files analyzed: ' + str(fileCount)+ '\n' )
    f.write('Streaks detected: ' + str(detected) + '\n' )
    f.write('Files with no detections: ' + str(zero))
    f.close()
    
def do_one(ff,output_path=None):
    """
    process a directory one fits-file (ff)
    """
    # Read a fits image and create a Streak instance.
    streak = Streak(ff,output_path=output_path)
    # Detect streaks.
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
    print("Running in data directory %s" % sys.argv[1])
    do_dir(sys.argv[1],sys.argv[2])
