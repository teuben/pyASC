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
#include <conio.h>
#include <fstream>

#define NUMBER_OF_CAMERAS 1
#define PIXEL_WIDTH 1392
#define PIXEL_HEIGHT 1040
#define MAX_CHARACTERS 93
#define MAX_IMAGES 999

int writeImageData(const char *path, const USHORT *pixels);
int takeStandardImage(HANDLE handle, int camIndex, ULONG exposure, USHORT *pixelArray);
int writeMultipleImages(int images, HANDLE handle, int camIndex, ULONG exposure, USHORT *pixelArray, const char *path);
int writeVariableExposureImages(HANDLE handle, int camIndex, USHORT *pixelArray, const char *path);

using namespace std;

/* declare this out here so that its memory is stored in the heap */
USHORT pixels[PIXEL_WIDTH * PIXEL_HEIGHT];

int main()
{	
	/* local variables */
	HANDLE handles[NUMBER_OF_CAMERAS];
	t_sxccd_params params[NUMBER_OF_CAMERAS];
	long firmwareVersions[NUMBER_OF_CAMERAS];
	int openVal, cameraModels[NUMBER_OF_CAMERAS];
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
	
	/* Write the pixels to a file to be processed by python scripts */
	writeImageData("pixels.txt", pixels);

	return 0;
}

/* 
	Writes image data to a text file to be read in python and saved as a .fits file
	@return - 1 if write was successful, 0 if there was an error. Will attempt to print error message.
*/

int writeImageData(const char *path, const USHORT *pixels){
	try{
		ofstream file;
		file.open(path);
		for (int h = 0; h < PIXEL_HEIGHT; h++){
			for (int w = 0; w < PIXEL_WIDTH; w++){
				file << pixels[PIXEL_WIDTH * h + w];
				file << ", ";
			}
			file << "\n";
		}
		file.close();
		return 1;
	}
	catch(int e){
		printf("An error occured. Error number: %d\n", e);
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

		sxClearPixels(handle, 0x00, camIndex);
		sxExposePixels(handle, 0x8B, camIndex, 0, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 1, 1, exposure);
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


/*
	Writes multiple images to the same path with an incrementing counter at the end of their name, starting at 0
	NOTE: This function should not be used when taking pictures throughout the night! When taking pictures throughout the night use 
	writeVariableExposureImages() and specify when to stop or use writeImagesUntil() and specify when to stop.
	@param images - number of images to be written. Cannot exceed 999
	@param path - as of current implementation, path should not include an extension. It will be implemented later that it doesn't matter
	but for now it should not. It also cannot exceed MAX_CHARACTERS characters.
	@return - number of images written
*/
int writeMultipleImages(int images, HANDLE handle, int camIndex, ULONG exposure, USHORT *pixelArray, const char *path){
	int imagesWritten = 0;
	char newPath[100];
	try{
		while (imagesWritten < images){
			if (strlen(path) >= MAX_CHARACTERS){
				throw MAX_CHARACTERS;
			}
			if (images > MAX_IMAGES){
				throw MAX_IMAGES;
			}
			takeStandardImage(handle, camIndex, exposure, pixelArray);
			for (int i = 0; i < strlen(path); i++){
				newPath[i] = path[i];
			}
			int i = strlen(path);
			//add picture index
			newPath[i] = ((imagesWritten % 10) % 100); newPath[i + 3] = '.'; newPath[i + 4] = 't'; newPath[i + 5] = 'x'; newPath[i + 6] = 't';
			writeImageData(newPath, pixelArray);
			imagesWritten++;
		}
	}
	catch(int e){
		if (e == MAX_CHARACTERS){
			printf("Error, path of file was too long: %d, exceeded %d\n", strlen(path), MAX_CHARACTERS);
		}
		if (e == MAX_IMAGES){
			printf("Error, number of images requested to be taken is too great: %d, exceeded %d\n", images, MAX_IMAGES);
		}
		else{
			printf("Error while writing multiple images on image number %d. Error number: %d\n", imagesWritten + 1, e);
		}
		return imagesWritten;
	}
	return imagesWritten;
}