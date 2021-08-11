#! /usr/bin/env python
#
# Process a whole (typically a month) directory, in which each subdirectory contains FITS files
# for whichpiecharts tables are made, at the end a single large gallery of all skypie plots are
# made in a matrix
#
import matplotlib.pyplot as plt
import numpy as np
import os,sys
import glob

def run(cmd):
    print('CMD',cmd)
    os.system(cmd)

# these should loop over directories, within which each directory is a night
for dir in sys.argv[1:]:

    # these could be something like '2020-03-30 to 2020-03-31'
    dirs = glob.glob('%s/*' % dir)

    print('Found %d directories' % len(dirs))

    tmpdir = 'tmpday'

    tabs = ""

    for i in range(len(dirs)):
       d = dirs[i]
       label = d.split('/')[-1].split()[0]
       cmd = 'rm -rf %s; ln -s "%s" %s' % (tmpdir,d,tmpdir)
       run(cmd)
       tab = 'day%02d.tab' % i
       tab = label
       cmd = '/n/astromake/opt/allsky/pyASC/ASC/SkyStats.py %s/*.fits > %s' % (tmpdir,tab)
       run(cmd)
       tabs = tabs + tab + ' '

    cmd = '/n/astromake/opt/allsky/pyASC/ASC/SkyPie.py %s' % tabs
    run(cmd)

