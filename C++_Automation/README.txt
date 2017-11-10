Other necessary files: fitsio.h and cfitsio.lib which can both be 
found at http://heasarc.gsfc.nasa.gov/fitsio/fitsio.html

This code currently can take images from an Oculus All-Sky camera and save that image into a FIT file.

int takeStandardImage(HANDLE handle, int camIndex, ULONG exposure, USHORT *pixelArray)
	Prepares the camera to take an image with least amount of specifications.
	Then reads image data into an array of unsighned shorts, array is expected to be sufficient in length.

Before adding more functionality, we must add the ability to dynamically allocate memory for taking many images
in a row named IMAGExxxxx.FIT and eventually the ability for the camera to concurrently take images and save the data
into arrays while also writing the data out to fits files. 

Currently that's the only extended function as a part of Automator.cpp. The next functionality to be written will
include taking images of a certain exposure until a given time with a predetermined naming convention, 
taking images with an adapting exposure until a given time, taking images until it is a certain brightness.

After this functionality is written I would like to include availability in user specified naming conventions.                                