#! /usr/bin/env python
#
#   1440 files took about 38 mins

from astride import Streak
import glob


def do_dir(d):
    ffs = glob.glob(d+'/*.FIT*')     # results in a non-numeric order
    for ff in ffs:
        print ff
        do_one(ff,ff[:ff.rfind('.')])

def do_one(ff,output_path=None):
    # Read a fits image and create a Streak instance.
    streak = Streak(ff,output_path=output_path)

    # Detect streaks.
    streak.detect()
    
    # Write outputs and plot figures.
    streak.write_outputs()
    streak.plot_figures()

#do_one('20151108_MD01_raw/IMG00681.FIT')
do_dir('20151108_MD01_raw')

