import os
import pathlib
from os.path import dirname
from os.path import join

from astride.detect import Streak
from astride.utils.logger import Logger


def test():
    logger = Logger().getLogger()

    logger.info('Start.')
    module_path = dirname(__file__)
    file_path = '/Users/Owner/Desktop/Fits Files/Fits'
    
    directory = os.fsencode(file_path)
    print(directory)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        print(filename)
        if filename.endswith(".fits"): 
            print(os.path.join(directory, filename))
            continue
        else:
            continue

    
	#1328
    # logger.info('Reading file 1328')

    # streak = Streak(r'C:\Users\Owner\Desktop\Fits Files\Fits\IMG01328.fits')
    # streak.output_path = r'/Users/Owner/Desktop/Fits Files/Pics/IMG01328 '
    # logger.info('Detecting...')
    # streak.detect()
    # logger.info('Output')
    # streak.write_outputs()
    # streak.plot_figures()
	
	# # 1329	
    # logger.info('Reading file 1329')
    # streak = Streak(r'C:\Users\Owner\Desktop\Fits Files\Fits\IMG01329.fits')
    # streak.output_path = '/Users/Owner/Desktop/Fits Files/Pics/IMG01329 '
    # logger.info('Detecting...')
    # streak.detect()
    # logger.info('Output')
    # streak.write_outputs()
    # streak.plot_figures()
	
	# # 1330
    # logger.info('Reading file 1330')
    # streak = Streak(r'C:\Users\Owner\Desktop\Fits Files\Fits\IMG01330.fits')
    # streak.output_path = '/Users/Owner/Desktop/Fits Files/Pics/IMG01330 '
    # logger.info('Detecting...')
    # streak.detect()
    # logger.info('Output')
    # streak.write_outputs()
    # streak.plot_figures()
 

    #from astride.utils.outlier import Outlier
    #logger.info('Search by Machine Learning..')
    #Outlier(streak.raw_borders)
    #import sys
    #sys.exit()

    # logger.info('Save figures and write outputs to %s' %
                # streak.output_path)
    # streak.write_outputs()
    # streak.plot_figures()

    # logger.info('Done.')

    # logger.handlers = []


if __name__ == '__main__':
    test()