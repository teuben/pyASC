import numpy as np
import cv2
import astropy.io.fits
# import matplotlib.pyplot as plt


def makeNightlyMovie(arch, node, date, outname):

    width, height = 1392, 1040
    size = (width, height)
    out = cv2.VideoWriter(outname, cv2.VideoWriter_fourcc(*'mp4v'), 10.0, size,
                          isColor=False)

    frameData = np.empty((height, width), dtype=np.uint8)

    for i, filename in enumerate(arch.getFITS(node, date)):
        # process filename (FITS file) into img_array
        print(i, filename)
        with astropy.io.fits.open(filename) as hdul:
            hdu = hdul[0]
            data = hdu.data/256
            frameData[:, :] = data
        out.write(frameData)

    out.release()
