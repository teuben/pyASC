import time
import shutil
import numpy as np
import cv2
import astropy.io.fits
from pathlib import Path
import matplotlib.pyplot as plt


class Action:

    def __init__(self, scheduler, name, cadence, outputDir, maxIter):
        self.scheduler = scheduler
        self.name = name
        self.cadence = parseCadence(cadence)
        if outputDir is not None:
            self.outputDir = Path(outputDir)
            if not self.outputDir.exists():
                self.outputDir.mkdir(parents=True)
        else:
            self.outputDir = None
        self.count = 0
        self.maxIter = maxIter
        self.t0 = time.time()



    def run(self, archive, *args, **kwargs):
        if self.maxIter is not None and self.count >= self.maxIter:
            return

        t = time.time()
        self.t = t
        print("Running {0:s}: t = {1:f}, archive = {2:s}"
              "outputDir = {3:s}".format(self.name, t, str(archive),
                                         str(self.outputDir)))
        
        self.kernel(archive, *args, **kwargs)

        self.count += 1

        self.reschedule(archive, *args, **kwargs)

    def reschedule(self, *args, **kwargs):

        handle = None

        if self.cadence is not None and self.cadence != 'once':

            t = time.time()
            i0 = int((t - self.t0) / self.cadence) + 1
            newTime = self.t0 + i0 * self.cadence
            handle = self.scheduler.enterabs(newTime, 1, self.run,
                                             args, kwargs)

        return handle

    def kernel(self, archive):
        return


    def _getFileList(self, archive, targetDate, inputDir=None):
       
        files = []

        if inputDir is not None:
            inpath = Path(inputDir)
            for path in sorted(inpath.iterdir()):
                if (path.exists() and path.is_file()
                        and (path.suffix == '.fits' or path.suffix == '.FIT')):
                    files.append(str(path.resolve()))
            return files

        if targetDate == 'all':
            dates = archive.getObsDates()
            for date in dates:
                files.extend(archive.getFITSByDate(date))

        elif isinstance(targetDate, list):
            for date in targetDate:
                files.extend(archive.getFITSByDate(str(date)))
        
        else:
            files.extend(archive.getFITSByDate(str(targetDate)))

        return files


    def _getFileListRAz(self, archive, targetRA, targetDate, RAtol):
       
        if targetDate == 'all':
            files = archive.getFITSByRAz(targetRA, RAtol)

        elif isinstance(targetDate, list):
            files = []
            for date in targetDate:
                fits = archive.getFITSByRAzDate(targetRA, str(date), RAtol)
                if fits is not None:
                    files.append(fits)
        
        else:
            files = [archive.getFITSByRAzDate(targetRA, str(self.targetDate),
                                              RAtol)]

        return files


class UpdateArchive(Action):

    def __init__(self, scheduler, name, cadence, maxIter, date=None,
                 label=None):

        myname = name
        if label is not None:
            myname += '-' + label

        self.date = date
        super().__init__(scheduler, myname, cadence, None, maxIter)

    def kernel(self, archive):

        if self.date is None:
            archive.update()


class MakeImage(Action):

    def __init__(self, scheduler, name, cadence, outputDir, maxIter, target,
                 label=None, overwrite=False, inputDir=None,
                 blackVal=None, whiteVal=None):

        myname = name
        if label is not None:
            myname += '-' + label
        self.label = label

        self.target = target
        self.overwrite = overwrite

        self.inputDir = inputDir
        self.blackVal = blackVal
        self.whiteVal = whiteVal

        super().__init__(scheduler, myname, cadence, outputDir, maxIter)

    def kernel(self, archive):

        files = self._getFileList(archive, self.target, self.inputDir)

        for f in files:
            self._makeImage(f)

    
    def _makeImage(self, filename):

        if self.label is None:
            name = Path(filename).stem + '-hist'
        else:
            name = Path(filename).stem + self.label

        figname = self.outputDir / (name + '.png')
        if not self.overwrite and figname.exists():
            return

        with astropy.io.fits.open(filename) as hdul:
            hdu = hdul[0]
            data = hdu.data

        fig, ax = plt.subplots(1, 1)
        ax.imshow(data, cmap=plt.cm.gist_gray,
                  vmin=self.blackVal, vmax=self.whiteVal)
        print("Saving",figname)
        fig.savefig(figname)
        plt.close(fig)


class MakeHist(Action):

    def __init__(self, scheduler, name, cadence, outputDir, maxIter, target,
                 label=None, overwrite=False, bitDepth=16, binWidth=4,
                 inputDir=None):

        myname = name
        if label is not None:
            myname += '-' + label
        self.label = label

        self.target = target
        self.inputDir = inputDir
        self.overwrite = overwrite
        self.bitDepth = bitDepth
        self.binWidth = binWidth

        super().__init__(scheduler, myname, cadence, outputDir, maxIter)

    def kernel(self, archive):

        files = self._getFileList(archive, self.target, self.inputDir)

        for f in files:
            self._makeHist(f)

    
    def _makeHist(self, filename):

        if self.label is None:
            name = Path(filename).stem + '-hist'
        else:
            name = Path(filename).stem + self.label

        figname = self.outputDir / (name + '.png')
        if not self.overwrite and figname.exists():
            return

        with astropy.io.fits.open(filename) as hdul:
            hdu = hdul[0]
            data = hdu.data.flat

        xmax = 2 ** self.bitDepth-1
        bins = np.arange(0, xmax+2, self.binWidth)

        fig, ax = plt.subplots(1, 1)
        ax.hist(data, bins, histtype='stepfilled')
        ax.set_xlim(bins[0], bins[-1])
        ax.set_ylim(0, None)
        print("Saving",figname)
        fig.savefig(figname)
        plt.close(fig)


class CopyByRA(Action):

    def __init__(self, scheduler, name, cadence, outputDir, maxIter,
                 targetRA, targetDate, RAtolerance, label=None):

        myname = name
        if label is not None:
            myname += '-' + label
        self.label = label

        self.targetDate = targetDate
        self.targetRA = targetRA
        self.RAtolerance = RAtolerance

        super().__init__(scheduler, myname, cadence, outputDir, maxIter)

    def kernel(self, archive):

        files = self._getFileListRAz(archive, self.targetRA, self.targetDate,
                                     self.RAtolerance)

        outDirStr = str(self.outputDir)

        for f in files:
            print("Copying", Path(f).name, "to", outDirStr)
            shutil.copy2(f, outDirStr)
    

def parseCadence(cadence):
    if cadence is None:
        return None

    if cadence == 'once':
        return cadence

    cadence = float(cadence)
    if cadence <= 0.0:
        return None

    return cadence


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
