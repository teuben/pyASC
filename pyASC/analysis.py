import os
import time
import numpy as np
import cv2
import astropy.io.fits
# import matplotlib.pyplot as plt


class Analysis:

    def __init__(self, scheduler, name, cadence, outputDir, maxIter):
        self.scheduler = scheduler
        self.name = name
        if cadence is None or cadence <= 0:
            self.cadence = None
        self.cadence = cadence
        self.outputDir = os.path.abspath(outputDir)
        self.count = 0
        self.maxIter = maxIter
        self.t0 = time.time()

    def run(self, archive):
        if self.maxIter is not None and self.count >= self.maxIter:
            return

        t = time.time()
        self.t = t
        print("Running {0:s}: t = {1:f}, archive = {2:s}"
              "outputDir = {3:s}".format(self.name, t, str(archive),
                                         self.outputDir))
        self.count += 1

        self.reschedule(archive)

    def reschedule(self, *args, **kwargs):

        handle = None

        if self.cadence is not None or self.cadence is not 'once':

            t = time.time()
            i0 = int((t - self.t0) / self.cadence) + 1
            newTime = self.t0 + i0 * self.cadence
            handle = self.scheduler.enterabs(newTime, 1, self.run,
                                             args, kwargs)

        return handle


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
