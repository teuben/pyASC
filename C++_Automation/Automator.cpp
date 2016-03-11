/* 

	To use .lib file, go to Project > References... > Configuration Properties > Linker > 
   > General > Additional Library directories | add the directory the .lib is in.

   Then go to Project > References... > Configuration Properties > Linker > Input > Additional dependencies |
   add the name of the .lib file ("<name>.lib")

*/

#include "stdafx.h"
#include <iostream>
#include <stdio.h>
#include <windows.h>
#include "SXUSB.h"
#include "longnam.h"
#include "fitsio.h"

#define NUMBER_OF_CAMERAS 1
#define PIXEL_WIDTH 1392
#define PIXEL_HEIGHT 1040
#define OBJECT "allsky"
#define TELESCOP ""
#define ORIGIN ""
#define INSTRUME "Starlight Xpress Oculus"
#define OBSERVER "UMD Observatory"

int convertImageData(USHORT twoDarray[PIXEL_HEIGHT][PIXEL_WIDTH], const USHORT *oneDarray);
int takeStandardImage(HANDLE handle, int camIndex, ULONG exposure, USHORT *pixelArray);
int writeImagesUntil(HANDLE handle, int camIndex, USHORT *pixelArray, const char *path, ULONG minutes);
int writeVariableExposureImages(HANDLE handle, int camIndex, USHORT *pixelArray, const char *path);

using namespace std;

/* declare these out here so that memory is stored in the heap */
USHORT pixels[PIXEL_WIDTH * PIXEL_HEIGHT];
USHORT pixelData[PIXEL_HEIGHT][PIXEL_WIDTH];

int main()
{	
	/* constants */
	short const BITPIX = USHORT_IMG;
	short const NAXIS = 2;
	short const NAXIS1 = PIXEL_HEIGHT;
	short const NAXIS2 = PIXEL_WIDTH;
	long		NAXES[2] = {PIXEL_WIDTH, PIXEL_HEIGHT}; /* purposely missing const */

	/* local variables */
	HANDLE handles[NUMBER_OF_CAMERAS];
	t_sxccd_params params[NUMBER_OF_CAMERAS];
	long firmwareVersions[NUMBER_OF_CAMERAS];
	int openVal, cameraModels[NUMBER_OF_CAMERAS], status;
	fitsfile *file;

	/* open the connected cameras */
	openVal = sxOpen(handles);
	printf("Opened Cameras: %d\n", openVal);

	/* error check the number of cameras */
	if (openVal > NUMBER_OF_CAMERAS){
		printf("MORE CAMERAS CONNECTED (%d) THAN SPECIFIED BY CODE (%d)\nTERMINATING PROGRAM\n", openVal, NUMBER_OF_CAMERAS);
		return 0;
	}
	if (openVal < NUMBER_OF_CAMERAS){
		printf("LESS CAMERAS CONNECTED (%d) THAN SPECIFIED BY CODE (%d)\nCODE WILL RUN, MEMEORY WILL BE WASTED\n", openVal, NUMBER_OF_CAMERAS);
	}

	/* Get and display camera information */
	for (int i = 0; i < openVal; i++){
		printf("Camera %d:\n", i);
		printf("\tCamera Firmware Version: %d\n", (firmwareVersions[i] = sxGetFirmwareVersion(handles[i])));
		printf("\tCamera Model: %d\n", (cameraModels[i] = sxGetCameraModel(handles[i])));
		sxGetCameraParams(handles[i], i, params);
	}

	/* Taking an Image */
	takeStandardImage(handles[0], 0, 50, pixels);

	/* set up a fits file with proper hdu to write to a file */
	status = 0;
	/* create the file, the ! means it will overwrite any existing file with the same name */
	if (fits_create_file(&file, "!test.fit", &status)){
		fits_report_error(stdout, status);
	}
	/* basic header information (BITPIX, NAXIS, NAXES, etc) is taken care of through this function as well) */
	if (fits_create_img(file, BITPIX, NAXIS, NAXES, &status)){
		fits_report_error(stdout, status);
	}
	/* extended header information */
	if (fits_write_key(file, TSTRING, "OBJECT", OBJECT, "", &status)){
		fits_report_error(stderr, status);
	}
	/* write the image data to the file */
	if (fits_write_img(file, TUSHORT, 1, PIXEL_HEIGHT * PIXEL_WIDTH, pixels, &status)){
		fits_report_error(stderr, status);
	}
	if (fits_close_file(file, &status)){
		fits_report_error(stdout, status);
	}

	return 0;
}

/* 
	Converts a 1D, column major array of pixel data into a 2D array. The arrays must be of the size specified for this function PIXEL_HEIGHT and PIXEL_WIDTH
	@return - 1 if convert was successful, 0 if there was an error. Will attempt to print error message.
*/

int convertImageData(USHORT twoDarray[PIXEL_HEIGHT][PIXEL_WIDTH], const USHORT oneDarray[PIXEL_HEIGHT * PIXEL_WIDTH]){
	try{
		for (int h = 0; h < PIXEL_HEIGHT; h++){
			for (int w = 0; w < PIXEL_WIDTH; w++){
				twoDarray[h][w] = oneDarray[PIXEL_WIDTH * h + w];
			}
		}
		return 1;
	}
	catch(int e){
		printf("Error while converting image data to 2D array: Error number: %d\n", e);
		return 0;
	}
}

/* 
	Takes an image with a connected camera. The camera exposes for the given time and then reads the image into pixels
	@param exposure - this is measured in milliseconds
	@return - 1 if the image was taken correctly, 0 if the image had an error. Will attempt to print error message.
*/

int takeStandardImage(HANDLE handle, int camIndex, ULONG exposure, USHORT *pixelArray){
	try{
		int bytesRead;
		/* clear pixels on the camera and expose them to take the image */
		sxClearPixels(handle, 0x00, camIndex);
		sxExposePixels(handle, 0x8B, camIndex, 0, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 1, 1, exposure);
		/* read the pixels from the camera into an array */
		if ((bytesRead = sxReadPixels(handle, pixelArray, PIXEL_WIDTH * PIXEL_HEIGHT)) <= 0){
			printf("Error reading pixels\n");
			return 0;
		}
	}
	catch(int e){
		printf("Error while taking image. Error number: %d\n", e);
		return 0;
	}

	return 1;
}


