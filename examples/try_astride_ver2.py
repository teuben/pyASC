#! /usr/bin/env python
#
#   1440 files took about 38 mins
#
# This version of try_astride:
#   - adds new parameters: (see https://github.com/dwkim78/ASTRiDE for more details on the parameters)
#       + radius dev cut (rad)
#       + connectivity angle (angle)
#       + remove background (remove_bkg)
#       + background box size (bkg_box_size)
#       + min_points
#       + max_area
#   - changes the default parameter values to values that tend to work well
#   - improves the differencing option
#       + can either mask out everything that is not different or make cutours of what is different
#   - adds a masking option
#       + currently only circle mask is implemented
#   - adds some more comments to try to make code more readable
#   - was worked on my Michael Suehle for his SDU Capstone



from __future__ import print_function
from tkinter import filedialog
from tkinter import *
# To use masking, please use my version of astride by using the command pip install git+https://github.com/shwaylay/ASTRiDE.git@allow-masking
# My version of astride is same as astride but makes it so that background removal does not interfere with streak detection
# does cause errors with connectivity angle though so change back to astride if you want to use connectivity angle and not masking.
from astride import Streak
import glob
import sys
import shutil
import os
import tkinter as tk
import matplotlib.pyplot as plt
from astropy.io import fits
# this website is a good source for working with fits
# https://docs.astropy.org/en/stable/io/fits/
import numpy as np

# for differencing
from skimage.metrics import structural_similarity as ssim
import imutils
import cv2

# for cutouts
from astropy import wcs
from astropy.nddata import Cutout2D
from astropy.wcs import WCS


file_sep = os.path.sep
# sets the default values for the arguments
class _Args:
    file_pathin = ""
    file_pathout = ""
    shape = 0.5
    area = 20
    contour = 2.7
    diff = False
    v = False
    rad = .4
    angle = -1 #sometimes causes errors when not -1 and masking is used
    start_frame = -1
    end_frame = -1
    remove_bkg = 'constant'
    bkg_box_size = 35
    min_points = 1
    max_area = 1000
    cut_out = False
    mask = "none"
    mask_args = "500 700 350"

# Returns an arguments object with the arguments from either the command line or the gui
def get_arg(argv):

    arguments = _Args()

    if len(argv) == 1:
        return get_int_arg(arguments)
    else:
        return get_cmd_arg(argv, arguments)

# The improved mk_diff finds the parts of the fits file that are different and creates boxes around them.
# If cutout is true, it will generate fits files that are cutouts of the boxes.
# Otherwise, it will masked out the areas that are not different with black.
# image differencing technique is based on the code from:
# https://www.pyimagesearch.com/2017/06/19/image-difference-with-opencv-and-python/
def mk_diff(f0, f1, diff, cutout):

    hdu0 = fits.open(f0, ignore_missing_end=True)
    hdu1 = fits.open(f1, ignore_missing_end=True)

    # make a folder to put the differenced fits files in
    os.mkdir(diff)

    # extract the 2D array of pixel values from the fits files
    image_data0 = hdu0[0].data
    image_data1 = hdu1[0].data

    # compute the Structural Similarity Index (SSIM) between the two images
    # and stores the differences in difference
    (score, difference) = ssim(image_data0, image_data1, full=True)
    difference = (difference * 255).astype("uint8")

    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(difference, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # rects stores the coordinates for the rectangles around the differences
    # sizes stores the height and the width of each rectangle for making cutouts
    rects = list()
    sizes = list()
    # loop over the contours
    for c in cnts:
    	# compute the bounding box of the contour and then store the coordinates for the
    	# bounding boxs on both input images to represent where the two images differ
        (x, y, w, h) = cv2.boundingRect(c)
        if w > 10 and h > 10 and w < 500 and h < 500:
            rects.append(np.array([[x,y], [x+w,y], [x+w,y+h], [x,y+h]]))
            sizes.append((w+30,h+30))

    # this is used for naming the differenced files later
    f0_slash = f0.rindex(file_sep)
    f1_slash = f1.rindex(file_sep)
    # if not making cutouts make the files with the mask
    if not cutout:
        # this code is based on code from:
        # https://stackoverflow.com/questions/37912928/fill-the-outside-of-contours-opencv
        mask = np.zeros(image_data1.shape).astype(image_data1.dtype)
        cv2.fillPoly(mask, rects, (60000,60000,60000))
        image_data0 = cv2.bitwise_and(image_data0, mask)
        image_data1 = cv2.bitwise_and(image_data1, mask)

        hdu0[0].data = image_data0
        hdu1[0].data = image_data1

        diff0 = diff + file_sep + f0[f0_slash+1:]
        hdu0.writeto(diff0,overwrite=True)
        diff1 = diff + file_sep + f1[f1_slash+1:]
        hdu1.writeto(diff1,overwrite=True)
    # otherwise make the cutout files
    else:
        i = 0
        for rect in rects:
            diff0 = diff + file_sep + f0[f0_slash+1:]
            save_cutout(f0, rect[0], sizes[i], diff0, i)
            diff1 = diff + file_sep + f1[f1_slash+1:]
            save_cutout(f1, rect[0], sizes[i], diff1, i)
            i += 1

# This saves a cutout of a fits file centered at position and with a size of size
# wrote this code with help from:
# https://astropy-cjhang.readthedocs.io/en/latest/nddata/utils.html
def save_cutout(ff, position, size, output_path, num):
    # Get the image
    filename = ff

    # Load the image and the WCS
    hdu = fits.open(filename)[0]
    wcs = WCS(hdu.header)

    # Make the cutout, including the WCS
    cutout = Cutout2D(hdu.data, position=position, size=size, wcs=wcs)

    # Put the cutout image in the FITS HDU
    hdu.data = cutout.data

    # Update the FITS header with the cutout WCS
    hdu.header.update(cutout.wcs.to_header())

    # Write the cutout to a new FITS file
    out_slash = output_path.rindex(file_sep)
    ff_slash = ff.rindex(file_sep)
    cutout_filename = output_path[:out_slash] + file_sep + str(num) + ff[ff_slash+1:]
    hdu.writeto(cutout_filename, overwrite=True)

# makes a masked copy of the fits file. Currently, only circle mask is implemented
# mask_args should be in this order (y_center, x_center, radius)
# circular masking is based on code from:
# https://stackoverflow.com/questions/44865023/how-can-i-create-a-circular-mask-for-a-numpy-array
def make_mask(ff, output_path, mask, mask_args):

    filename = ff
    hdu = fits.open(filename)[0]
    image_data = hdu.data

    #apply mask here -----v
    mask = mask.casefold()

    if mask == 'circle':
        y_cen = mask_args[0]
        x_cen = mask_args[1]
        radius = mask_args[2]

        # if the distance of a pixel from the center is larger than the radius,
        # set it to black
        for y in range(0, len(image_data)):
            for x in range(0, len(image_data[0])):
                distance_from_cen = np.sqrt((x-x_cen)**2 + (y-y_cen)**2)
                if distance_from_cen > radius:
                    image_data[y,x] = 0

        # Write the cutout to a new FITS file
        f_slash = ff.rindex(file_sep)
        mask_filename = output_path + ff[f_slash:]
        hdu.writeto(mask_filename, overwrite=False)

# reads arguments from the command line
def get_cmd_arg(argv, arguments):
    import argparse as ap
    parser = ap.ArgumentParser()
    # add all of the argument options
    parser.add_argument('-i','--filein', nargs = 1, help = 'Directory to input fits directory')
    parser.add_argument('-o','--fileout', nargs = 1, help = 'Directory to output folder')
    parser.add_argument('-s','--shape', nargs = 1, help = 'Shape factor')
    parser.add_argument('-a','--area', nargs = 1, help = 'Minimum area to be considered a streak')
    parser.add_argument('-c','--contour', nargs = 1, help = 'Control value')
    parser.add_argument('-d','--difference', action = 'store_const',const = arguments.diff, help = 'Create difference images')
    parser.add_argument('-v','--verbose', action = 'store_const', const = arguments.v, help = 'Verbose')
    parser.add_argument('-S','--start', nargs = 1, help = 'Start Frame (starts at 1)')
    parser.add_argument('-E','--end', nargs = 1, help = 'End Frame')
    parser.add_argument('-r','--rad', nargs = 1, help = 'Empirical cut for radius deviation')
    parser.add_argument('-A','--angle', nargs = 1, help = 'The maximum angle of slope to link each streak')
    parser.add_argument('-R','--remove_bkg', nargs = 1, help = 'Remove backgound type, can be \'constant\' or \'map\'')
    parser.add_argument('-b','--bkg_box_size', nargs = 1, help = 'Backgound box size, used when remove backgound type is \'map\'')
    parser.add_argument('-m','--min_points', nargs = 1, help = 'Min points value')
    parser.add_argument('-M','--max_area', nargs = 1, help = 'Max area value')
    parser.add_argument('-ma','--mask', nargs = 1, help = 'Mask type for image')
    parser.add_argument('-MA','--mask_args', nargs = 1, help = 'Arguments for mask, should be in order: y_center x_center radius_size')
    parser.add_argument('-C','--cutout', nargs = 1, help = 'If differencing should make cutouts rather than mask')
    args=vars(parser.parse_args())

    # set the arguments if they are given
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
    if args['rad']   != None: arguments.rad   = float(args['rad'][0])
    if args['angle']   != None: arguments.angle   = float(args['angle'][0])
    if args['remove_bkg']   != None: arguments.remove_bkg = args['remove_bkg'][0]
    if args['bkg_box_size']   != None: arguments.bkg_box_size = float(args['bkg_box_size'][0])
    if args['min_points']   != None: arguments.min_points = float(args['min_points'][0])
    if args['max_area']   != None: arguments.max_area = float(args['max_area'][0])
    if args['mask'] != None: arguments.mask = args['mask'][0]
    if args['mask_args']   != None: arguments.mask_args = args['mask_args'][0]
    if args['cutout']   != None: arguments.cutout = args['cutout'][0]

    return arguments

# gets the arguments from the gui
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

    # set up all of the arguments
    top = tk.Tk()
    nshape = tk.StringVar()
    narea = tk.StringVar()
    ncontour = tk.StringVar()
    nstart_frame = tk.StringVar()
    nend_frame = tk.StringVar()
    ndiff = tk.IntVar()
    nv = tk.IntVar()
    nrad = tk.StringVar()
    nangle = tk.StringVar()
    nremove_bkg = tk.StringVar()
    nbkg_box_size = tk.StringVar()
    nmin_points = tk.StringVar()
    nmax_area = tk.StringVar()
    nmask = tk.StringVar()
    nmask_args = tk.StringVar()
    ncutout = tk.IntVar()

    # create all the labels and input areas for the arguments
    L1 = Label(top, text="Shape value (1=circle, .1=thin oval) (default = 0.5): ")
    L1.pack()
    eshape = Entry(top, textvariable=nshape)
    #nshape = float(nshape.get())
    eshape.pack()

    L2 = Label(top, text="Minimum area (default = 20): ")
    L2.pack()
    earea = Entry(top, textvariable=narea)
    #narea = float(narea.get())
    earea.pack()

    L3 = Label(top, text="Contour value (higher=only brighter streaks detected)(default = 2.7): ")
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

    L6 = Label(top, text="Empirical cut for radius deviation (default is 0.4)")
    L6.pack()
    erad = Entry(top, textvariable=nrad)

    erad.pack()

    L7 = Label(top, text="The maximum angle of slope to link each streak (default is -1)")
    L7.pack()
    eangle = Entry(top, textvariable=nangle)

    eangle.pack()

    L8 = Label(top, text="Remove background type (\'constant\' or \'map\') (default is \'constant\')")
    L8.pack()
    eremove_bkg = Entry(top, textvariable=nremove_bkg)

    eremove_bkg.pack()

    L9 = Label(top, text="Background box size (only applies if remove background type is \'map\') (default is 35)")
    L9.pack()
    ebkg_box_size = Entry(top, textvariable=nbkg_box_size)

    ebkg_box_size.pack()

    L10 = Label(top, text="Minimum number of data points for the streak borders (default is 1)")
    L10.pack()
    emin_points = Entry(top, textvariable=nmin_points)

    emin_points.pack()

    L11 = Label(top, text="Max area the streaks can have (default is 1000)")
    L11.pack()
    emax_area = Entry(top, textvariable=nmax_area)

    emax_area.pack()

    L12 = Label(top, text="Mask type. (options are \'circle\' and \'none\') (default is \'none\')")
    L12.pack()
    emask = Entry(top, textvariable=nmask)

    emask.pack()

    L13 = Label(top, text="Mask arguments. (not used if mask is \'none\')(in form y_center x_center radius) (default is 500 700 350)")
    L13.pack()
    emask_args = Entry(top, textvariable=nmask_args)

    emask_args.pack()

    C1 = Checkbutton(top, text = "Difference imaging (default = false)", variable = ndiff, \
                     onvalue=1, offvalue=0 )
    C2 = Checkbutton(top, text = "Verbose mode (default = false)", variable = nv, \
                 onvalue = 1, offvalue = 0 )

    C3 = Checkbutton(top, text = "Differencing cutout? (has no effect if diff is false) (default = false)", variable = ncutout, \
                 onvalue = 1, offvalue = 0 )

    # save all of the arguments to the arguments object
    def save(nshape, narea, ncontour, nstart_frame, nend_frame, ndiff, nv, nrad, nangle, nremove_bkg, nbkg_box_size, nmin_points, nmax_area, nmask, nmask_args, ncutout):
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

        if len(nrad.get()) != 0:
            arguments.rad = float(nrad.get())

        if len(nangle.get()) != 0:
            arguments.angle = float(nangle.get())

        if len(nremove_bkg.get()) != 0:
            arguments.remove_bkg = nremove_bkg.get()

        if len(nbkg_box_size.get()) != 0:
            arguments.bkg_box_size = float(nbkg_box_size.get())

        if len(nmin_points.get()) != 0:
            arguments.min_points = float(nmin_points.get())

        if len(nmax_area.get()) != 0:
            arguments.max_area = float(nmax_area.get())

        if len(nmask.get()) != 0:
            arguments.mask = nmask.get()

        if len(nmask_args.get()) != 0:
            arguments.mask_args = nmask_args.get()

        arguments.diff = ndiff.get()

        arguments.v = nv.get()

        arguments.cutout = ncutout.get()

        top.destroy()

    s = Button(top, text="Save Values", command=lambda: save(nshape, narea, ncontour, nstart_frame, nend_frame, ndiff, nv, nrad, nangle, nremove_bkg, nbkg_box_size, nmin_points, nmax_area, nmask, nmask_args, ncutout))

    C1.pack()
    C2.pack()
    C3.pack()
    s.pack()
    top.mainloop()

    return(arguments)

# processes all fits images in the directory stored in arguments.file_pathin
def do_dir(arguments, diff):
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

    # debug/verbose (shows extra information)
    if arguments.v:
          print('DEBUG: shape=%g area=%g contour=%g' % (arguments.shape,arguments.area,arguments.contour))

    ffs = glob.glob(arguments.file_pathin+'/*.FIT') + glob.glob(arguments.file_pathin+'/*.fit') + \
          glob.glob(arguments.file_pathin+'/*.FTS') + glob.glob(arguments.file_pathin+'/*.fts') + \
          glob.glob(arguments.file_pathin+'/*.FITS') + glob.glob(arguments.file_pathin+'/*.fits')
    ffs = list(set(ffs))             # needed for dos
    ffs.sort()                       # on linux wasn't sorted, on dos it was
    f = open(arguments.file_pathout+'/summary.txt','w')   # Creates summary text file
    f.write('Streaks found in files: \n')   #Creates first line for summary file

    # if masking, create a folder for the masks and store the masked fits files in there
    if arguments.mask.casefold() != "none":
        new_output_path = arguments.file_pathout + '\\Masks'
        os.mkdir(new_output_path)

        # convert mask_args to an array of values
        mask_args = arguments.mask_args.split(" ")
        mask_args = [int(i) for i in mask_args]

        print("Generating masks...")
        for ff in ffs:
            make_mask(ff, new_output_path, arguments.mask, mask_args)

        # now that masked files are made, run do_dir again on the masked files
        arguments.mask = "none"
        arguments.file_pathin = new_output_path
        do_dir(arguments, diff)
        shutil.rmtree(new_output_path)
        return

    else:
        sf = arguments.start_frame
        ef = arguments.end_frame

        # if not doing differencing, process files like normal (this part is mostly same as before)
        if not diff:

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

                #num = do_one(ff,arguments.file_pathout+'/'+ff[ff.rfind(os.sep)+1:ff.rfind('.')],arguments.shape,arguments.area,arguments.contour, arguments.rad, arguments.angle, arguments.remove_bkg, arguments.bkg_box_size, arguments.min_points, arguments.max_area)
                num = do_one(ff,arguments.file_pathout,arguments.shape,arguments.area,arguments.contour, arguments.rad, arguments.angle, arguments.remove_bkg, arguments.bkg_box_size, arguments.min_points, arguments.max_area)

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

        # if doing differencing, make all the differenced fits files
        else:
            dfs = []

    #        print('Computing %d differences' % (ef-sf+1))
            # creates a file path for each differenced fits file
            for i in range(len(ffs)-1):
                dfs.append(arguments.file_pathout+file_sep+ffs[i+1][len(arguments.file_pathin):]+'DIFF')
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
            # try except block commented out for troubleshooting
            for df in dfs[sf-1:ef]:
                #try:
                mk_diff(ffs[i], ffs[i+1], dfs[i], arguments.cutout)

                arguments.file_pathin = dfs[i]
                # calls do_dir on each folder with differenced fits images
                do_dir(arguments, False)
                shutil.rmtree(dfs[i])

                #except:
                #    num=-1
                #    sys.stdout.write('X')



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

# processes an individual fits file
def do_one(ff,output_path,shape,area,contour, rad, angle, remove_bkg, bkg_box_size, min_points, max_area):
    """
    process a directory one fits-file (ff)
    """
    try:
        # Read a fits image and create a Streak instance.
        streak = Streak(ff,output_path=output_path)
        # Detect streaks.

        # Set the parameters
        streak.shape_cut = shape
        streak.area_cut = area
        streak.contour_threshold = contour

        streak.remove_bkg = remove_bkg
        streak.radius_dev_cut = rad
        streak.connectivity_angle = angle
        streak.remove_bkg = remove_bkg
        streak.bkg_box_size = bkg_box_size
        streak.min_points = min_points

        streak.detect()

        # filter out the detections that are too big
        for edge in streak.streaks:
            if edge['area'] > max_area:
                streak.streaks.remove(edge)

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

if __name__ == '__main__':

    arguments = get_arg(sys.argv)

    #Prints selected folders
    print("Running in data directory %s" % arguments.file_pathin)
    print("Outputting in data directory %s" % arguments.file_pathout)
    do_dir(arguments, arguments.diff)

    #print("Running in data directory %s" % sys.argv[1])

    #do_dir(sys.argv[1],sys.argv[2])
