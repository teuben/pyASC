#! /usr/bin/env python
import argparse as ap
import glob
from astropy.table import Table
from astropy.table import Column
from astropy.io import ascii
import numpy as np
import os
import time

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def get_row(file_path):
    summary = open(file_path+"/summary.txt", 'r')
    row = [file_path]
    for line in summary:
            line = line.strip()
            if line.startswith("Streaks detected:"):
                row.append(line[18:])
    while len(row) < 3:
        row.append('0')

    return row

 
date = False

parser = ap.ArgumentParser()
parser.add_argument('-i','--filein', nargs=1, help = 'Directory of outputs of try_astride.py')
parser.add_argument('-a', '--alldir', nargs=1, help = 'All sub directories in given path')
parser.add_argument('-l', '--latest', nargs=1, help = 'looks at latest directory in given path')
parser.add_argument('-d', '--date', action = 'store_const', const = date, help = 'tell program what year each file was made in') 
args = vars(parser.parse_args())

if args['date'] != None:
    date = True

time_set = []
table_set = []
file_paths = []

if args['filein'] != None: 
    file_paths = [(args['filein'][0])]
    time_set.append(time.gmtime(os.path.getctime(file_paths[0])).tm_year)

if args['alldir'] != None:
    file_paths = listdir_fullpath(args['alldir'][0])
    file_paths.sort(key = lambda x: int(x[len(args['alldir'][0]):]))
    for file in file_paths:
        time_set.append(time.gmtime(os.path.getctime(file)).tm_year)
    time_set = list(set(time_set))
    time_set.sort()

if args['latest'] != None:
    file_paths = listdir_fullpath(args['latest'][0])
    file_paths = [max(file_paths, key=os.path.getctime)]
    time_set.append(time.gmtime(os.path.getctime(file_paths[0])).tm_year)

# if date:
#     for file in file_paths:
#         year = input('Enter year for directory ' + file + '\n')
#         times.append(int(year))
#     time_set = list(set(times))
#     time_set.sort()

if date:
    time_set = []
    year = input('Enter year for directory\n')
    time_set.append(int(year))

min_year = time_set[0]

for counter, year in enumerate(time_set):
    try:
        table_set.append(ascii.read("table"+year+".html"))
    except:
        arr = np.arange(3).reshape(1,3)
        table_set.append(Table(arr, names=('file', 'reg', 'diff'),dtype=('S32', 'S2', 'S2')))
        table_set[counter].remove_row(0)

for counter, file in enumerate(file_paths):
    if date:
        year = time_set[0]
    else:
        year = time.gmtime(os.path.getctime(file)).tm_year
    table_set[year-min_year].add_row(get_row(file))

for counter, table in enumerate(table_set):
    table.write("table"+str(time_set[counter])+".html", format="html", overwrite = True)





