#! /usr/bin/env python
import argparse as ap
import glob
from astropy.table import Table
from astropy.table import Column
from astropy.io import ascii
import numpy as np
import os


parser = ap.ArgumentParser()
parser.add_argument('-i','--filein', nargs=1, help = 'Directory of outputs of try_astride.py')
parser.add_argument('-a', '--alldir', nargs=1, help = 'All sub directories in given path')
parser.add_argument('-l', '--latest', nargs=1, help = 'looks at latest directory in given path')
args = vars(parser.parse_args())

all = False

table_set = {}

if args['filein'] != None: 
    file_path = (args['filein'][0])
    

if args['alldir'] != None:
    file_path = (args['alldir'][0])
    all = True

if args['latest'] != None:
    list = os.listdir(args['latest'][0])
    for i in range(len(list)):
        list[i] = args['latest'][0] + list[i]
    file_path = max(list, key=os.path.getctime)


try:
    t = ascii.read("table1.html")
except:
    arr = np.arange(3).reshape(1,3)
    t = Table(arr, names=('file', 'reg', 'diff'),dtype=('S32', 'S2', 'S2'))
    t.remove_row(0)


if all:
    list = os.listdir(file_path)
    list.sort()

    for file in list:
        row = [file]
        summary = open(file_path+file+"/summary.txt", 'r')
        for line in summary:
            line = line.strip()
            if line.startswith("Streaks detected:"):
                row.append(line[18:])
        while len(row) < 3:
            row.append('0')
        t.add_row(row)        
else:

    summary = open(file_path+"/summary.txt", 'r')
    row = [file_path]
    for line in summary:
            line = line.strip()
            if line.startswith("Streaks detected:"):
                row.append(line[18:])
    while len(row) < 3:
        row.append('0')
    t.add_row(row)


t.write("table1.html", format="html", overwrite = True)

print(t)

# if args['filein'] != None: 
#     file_path = (args['filein'][0])

# if args['alldir'] != None:
#     file_path = (args['alldir'][0])
#     all = True

# if args['latest'] != None:
#     list = os.listdir(args['latest'][0])
#     for i in range(len(list)):
#         list[i] = args['latest'][0] + list[i]
#     file_path = max(list, key=os.path.getctime)

# try:
#     t = ascii.read("table1.html")
# except:
#     arr = np.arange(3).reshape(1,3)
#     t = Table(arr, names=('file', 'reg', 'diff'),dtype=('S32', 'S2', 'S2'))
#     t.remove_row(0)


# if all:
#     list = os.listdir(file_path)
#     list.sort()

#     for file in list:
#         row = [file]
#         summary = open(file_path+file+"/summary.txt", 'r')
#         for line in summary:
#             line = line.strip()
#             if line.startswith("Streaks detected:"):
#                 row.append(line[18:])
#         while len(row) < 3:
#             row.append('0')
#         t.add_row(row)        
# else:

#     summary = open(file_path+"/summary.txt", 'r')
#     row = [file_path]
#     for line in summary:
#             line = line.strip()
#             if line.startswith("Streaks detected:"):
#                 row.append(line[18:])
#     while len(row) < 3:
#         row.append('0')
#     t.add_row(row)


# t.write("table1.html", format="html", overwrite = True)

# print(t)

