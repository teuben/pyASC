#! /usr/bin/env python

import os
import glob
import numpy as np
from astropy.io import fits
from astropy.nddata import CCDData
import tkinter as tk
from tkinter import filedialog

winin = tk.Tk()
winin.withdraw()
winin.attributes('-topmost', True)
input_path = filedialog.askdirectory(title = "Select input")

ffs = glob.glob(input_path +'/*.FIT') + glob.glob(input_path +'/*.fit') + \
      glob.glob(input_path +'/*.FTS') + glob.glob(input_path +'/*.fts') + \
      glob.glob(input_path +'/*.FITS') + glob.glob(input_path +'/*.fits')
ffs = list(set(ffs))             # needed for dos
ffs.sort()

overexposed = input_path + "/overexposed"
os.mkdir(overexposed)

threshold = 40000

print("file name\t\t\tmean")
for ff in ffs:
    hdu  = fits.open(ff,ignore_missing_end=True)
    data = hdu[0].data.astype(np.float32)
    dmean = data[175:780,400:1000].mean()
    f_sep = ff.rindex(os.path.sep)
    f_dot = ff.rindex('.')
    print(ff[f_slash+1:f_dot] + "\t" + str(dmean))

    hdu.close()

    if dmean > threshold:
        # Move a file by renaming it's path
        os.rename(ff, overexposed + ff[f_sep:])
