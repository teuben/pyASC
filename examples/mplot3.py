from astropy.io import fits
import argparse as ap
import mplot1 as mp

#Takes a 3D numpy array and takes a slice of it on the given axis with a given value
#*Errors are not handled in this script*

#slices the given data. NOTE: the header must have NAXIS = 3. Maybe change this later? option for NAXIS 2 or 3?
def cslice(header, data, flag, value):
    h = header.copy()
    h.pop('NAXIS3')
    h['NAXIS'] = 2
    nx = data.shape[2]
    ny = data.shape[1]
    nz = data.shape[0]
    if flag == 'x':
        d = data[:,:,args['x'][0]]
        h['NAXIS1'] = ny
        h['NAXIS2'] = nz
    elif flag == 'y':
        d = data[:,args['y'][0],:]
        h['NAXIS1'] = nx
        h['NAXIS2'] = nz
    else:
        d = data[args['z'][0],:,:]
        h['NAXIS1'] = nx
        h['NAXIS2'] = ny
    #returns data and a header
    return d, h
    
#calls the function cslice() with proper parameters based on the given arguments
#returns a list of tuples containing a tuple of data and header and a filename
#so sliceList[0] = ((data, header), filename)
#   sliceList[0][0] = (data, header)
#   sliceList[0][0][0] = data and sliceList[0][0][1] = header
#seems crazy, but works fine in the for loop
def sliceHandler(args):
    
    #Open the cube and extract the data and header from it
    c = fits.open('cube.fits')
    d = c[0].data
    h = c[0].header

    #list to hold each slice
    sliceList = []
    #if an argument was used, then take a slice of it and add that slice to the lists
    if args['x'] != None:
        s = (cslice(h, d, 'x', args['x'][0]), 'slice_x.fits')
        sliceList.append(s)
    if args['y'] != None:
        s = (cslice(h, d, 'y', args['y'][0]), 'slice_y.fits')
        sliceList.append(s)
    if args['z'] != None:
        s = (cslice(h, d, 'z', args['z'][0]), 'slice_z.fits')
        sliceList.append(s)
    return sliceList
    
if __name__ == '__main__':
    
    parser = ap.ArgumentParser(description='Slicing 3D numpy arrays')
    parser.add_argument('-x',nargs = 1, type = int, required = False, help = 'Value for x as sliced axis')
    parser.add_argument('-y',nargs = 1, type = int, required = False, help = 'Value for y as sliced axis')
    parser.add_argument('-z',nargs = 1, type = int, required = False, help = 'Value for z as sliced axis')
    args = vars(parser.parse_args())
    
    
    sliceList = sliceHandler(args)

    #Show each image and save it
    for s in sliceList:
        data = s[0][0]
        header = s[0][1]
        mp.show(data)
        fits.writeto(s[1], data, header, clobber=True)