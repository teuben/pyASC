#! /usr/bin/env python
#
#   1440 files took about 38 mins
#

from __future__ import print_function

from astride import Streak
import glob
import sys

def do_dir(d):
    """
    process a directory 'd'
    """
    ffs = glob.glob(d+'/*.FIT*')     # results in a non-numeric order
    for ff in ffs:
        # print(ff)
        do_one(ff,ff[:ff.rfind('.')])

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
#do_one('20151108_MD01_raw/IMG00681.FIT')
#do_dir('20151108_MD01_raw')

if __name__ == '__main__':
    print("Running in data directory %s" % sys.argv[1])
    do_dir(sys.argv[1])
