from astropy.io import fits
import argparse as ap
import mplot1 as mp

#Takes a 3D numpy array and takes a slice of it on the given axis with a given value
#*Errors are not handled in this script*

def splice(args):
    cube = fits.open('cube.fits')
    data = cube[0].data
    header = cube[0].header
    if args['x'] != None:
        splice = data[:,:,args['x']]
    elif args['y'] != None:
        splice = data[:,args['y'],:]
    else:
        splice = data[args['z'],:,:]
    #using squeeze because data[:,:,int] is returning a 3D array for some reason. squeeze() gets rid of the length 1 side
    splice = splice.squeeze()
    return splice, header
    
if __name__ == '__main__':
    
    parser = ap.ArgumentParser(description='Slicing 3D numpy arrays')
    parser.add_argument('-x',nargs = 1, type = int, required = False, help = 'Value for x as sliced axis')
    parser.add_argument('-y',nargs = 1, type = int, required = False, help = 'Value for y as sliced axis')
    parser.add_argument('-z',nargs = 1, type = int, required = False, help = 'Value for z as sliced axis')
    args = vars(parser.parse_args())
    
    data, header = splice(args)
    
    #It's a 2D array now
    header.pop('NAXIS3')
    header['NAXIS'] = 2

    #Show the image and save it
    mp.show(data)
    fits.writeto('splice.fits', data, header, clobber=True)