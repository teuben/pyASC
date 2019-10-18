import cv2
import astropy.io.fits


def makeNightlyMovie(arch, node, date, outname):

    width, height = 100, 100
    size = (width, height)
    out = cv2.VideoWriter(outname, cv2.VideoWriter_fourcc(*'mp4v'), 15, size)

    for filename in arch.getFITS(node, date):
        # process filename (FITS file) into img_array
        hdul = astropy.io.fits.open(filename)
        print(hdul.info())
        hdul.close()
        # out.write(f.data)
        break
    out.release()

    return
