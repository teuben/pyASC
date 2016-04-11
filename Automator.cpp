/* 

	To use .lib file, go to Project > References... > Configuration Properties > Linker > 
   > General > Additional Library directories | add the directory the .lib is in.

   Then go to Project > References... > Configuration Properties > Linker > Input > Additional dependencies |
   add the name of the .lib file ("<name>.lib")

*/

/* 

	Image taking proccess is currently under a second, compare efficiency of GUI verses our technique

	*/

#include "stdafx.h"
#include <iostream>
#include <cstdio>
#include <string>
#include <Windows.h>
#include <sstream>
#include <time.h> 
#include "getopt.h"
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
#define TEMPLATE "!IMG%05d.fits"
#define MAX_LEN 100

int takeStandardImage(HANDLE handle, int camIndex, float exposure, USHORT *pixelArray);
int writeImage(HANDLE handle, int camIndex, USHORT *pixelArray, char *);
int writeMultipleImages(HANDLE handle, int camIndex, USHORT *pixelArray);
int numDigits(int number);
std::string getDate();
std::string getTime();
std::string NumberToString(int number);
void setDate(fitsfile *, int);
void printError(int, const char *);



/* declare these out here so that memory is stored in the heap */
USHORT pixels[PIXEL_WIDTH * PIXEL_HEIGHT];
	
/* constants */
short const BITPIX = USHORT_IMG;
short const NAXIS = 2;
short const NAXIS1 = PIXEL_HEIGHT;
short const NAXIS2 = PIXEL_WIDTH;
long		NAXES[2] = {PIXEL_WIDTH, PIXEL_HEIGHT}; /* purposely missing const */


/* Command Line Arguments */
char dirname[MAX_LEN] = "test_data\\";				/* -d <string> */
char templateName[MAX_LEN] = "IMG%05d.fits";		/* -t <string> */
char observatory[MAX_LEN] = "defaultObs";					/* -o <string> */
float exposure = 1.0;						/* -e <float>  NOTE: in seconds */
float sleepTime = 0.0;						/* -s <float> Sleep time in between taking images */
int numImages = 1;							/* -n <int> */
int initialIndex = 0;						/* -i <int> */
bool overwrite = false;						/* -f */
bool verbose = true;						/* -v */ /*NOTE: NOT YET IMPLEMENTED */

int main(int argc, char **argv)
{


	/* local variables */
	HANDLE handles[NUMBER_OF_CAMERAS];
	t_sxccd_params params[NUMBER_OF_CAMERAS];
	long firmwareVersions[NUMBER_OF_CAMERAS];
	int openVal, cameraModels[NUMBER_OF_CAMERAS];

	/* parse command line arguments */
	int c;
	while ((c = getopt(argc, argv, "o:e:n:d:t:s:i:f:v:")) != -1)
    switch (c){
	case 'o':
		strcpy(observatory, optarg);
		break;
	case 'e':
		exposure = strtol(optarg, NULL, 10);
		break;
	case 'n':
		numImages = strtol(optarg, NULL, 10);
		break;
	case 'd':
		strcpy(dirname, optarg);
		break;
	case 't':
		strcpy(templateName, optarg);
		break;
	case 's':
		sleepTime = strtol(optarg, NULL, 10);
		break;
	case 'i':
		initialIndex = strtol(optarg, NULL, 10);
		break;
	case 'f':
		overwrite = true;
		break;
	case 'v':
		verbose = true;
		break;
	default:
		break;
      }

	

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
	writeMultipleImages(handles[0], 0, pixels);

	return 0;
}

/** 
	Takes an image with a connected camera. The camera exposes for the given time and then reads the image into pixels
	@param exposure - this is measured in milliseconds
	@return - 1 if the image was taken correctly, 0 if the image had an error. Will attempt to print error message.
*/

int takeStandardImage(HANDLE handle, int camIndex, float exposure, USHORT *pixelArray){
	try{
		int bytesRead;
		/* clear pixels on the camera and expose them to take the image */
		sxClearPixels(handle, 0x00, camIndex);
		sxExposePixels(handle, 0x8B, camIndex, 0, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 1, 1, (ULONG) (exposure * 1000));
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

/**
	attempts to take multiple images with the camera stored in handle with an index of camIndex. This function will expose, read, and write the images
	on its own.
	@return - number of images successfully written.
*/
int writeMultipleImages(HANDLE handle, int camIndex, USHORT *pixelArray){
	
	int imagesTaken = 0;
	char path[MAX_LEN], newPath[MAX_LEN];
	strcpy(path, dirname);
	strcat(path, templateName);
	printf("path and name: %s\n", path);
	for (int i = 0; i < numImages; i++){
		try{
			/* <templateName>.fits */
			sprintf_s(newPath, 100, path, imagesTaken + initialIndex);
			writeImage(handle, camIndex, pixelArray, newPath);
		}
		catch(int e){
			printf("CAUGHT ERROR %d while taking multiple images, stopped after %d images\n", e, imagesTaken);
			return imagesTaken;
		}
		imagesTaken++;
		Sleep(sleepTime);
	}
	return imagesTaken;


}

/** 
	writes image to given pixelArray to path (NOTE: path does not include extension, that is added by the function).
	@return - 0 if failed, 1 if successfully wrote image.
*/
int writeImage(HANDLE handle, int camIndex, USHORT *pixelArray, char * path){

	takeStandardImage(handle, 0, exposure, pixels);

	/* set up a fits file with proper hdu to write to a file */
	fitsfile *file;
	int status = 0;
	char newPath[MAX_LEN];
	/* if overwrite flag is true add an '!' to the front so that fitsio overwrites files of
		of the same name */

	/* 
		** make directory here **
	*/

	if (overwrite == true){
		strcpy(newPath, "!");
		strcat(newPath, path);
	}
	else{
		strcpy(newPath, path);
	}

	printf("file name = %s\n", newPath);
	if (fits_create_file(&file, newPath, &status)){
		/*fits_report_error(stdout, status);*/
		printError(status, "writeImage, while creating file");
	}
	/* basic header information (BITPIX, NAXIS, NAXES, etc) is taken care of through this function as well) */
	if (fits_create_img(file, BITPIX, NAXIS, NAXES, &status)){
		printError(status, "writeImage, while creating image");
	}
	/* extended header information */
	if (fits_write_key(file, TSTRING, "OBJECT", OBJECT, "", &status)){
		printError(status, "writeImage, while writing OBJECT");
	}
	if (fits_write_key(file, TSTRING, "TELESCOP", TELESCOP, "", &status)){
		printError(status, "writeImage, while writing TELESCOP");
	}
	if (fits_write_key(file, TSTRING, "ORIGIN", ORIGIN, "", &status)){
		printError(status, "writeImage, while writing ORIGIN");
	}
	if (fits_write_key(file, TSTRING, "INSTRUME", INSTRUME, "", &status)){
		printError(status, "writeImage, while writing INSTRUME");
	}
	if (fits_write_key(file, TSTRING, "OBSERVER", (void *) observatory/*.c_str()*/, "", &status)){
		printError(status, "writeImage, while writing OBSERVER");
	}
	if (fits_write_key(file, TFLOAT, "EXPTIME", (void *) &exposure, "", &status)){
		printError(status, "writeImage, while writing EXPTIME");
	}

	/* find the current date and time and write it to a keyword(s) */
	setDate(file, 1);

	/* write the image data to the file */
	if (fits_write_img(file, TUSHORT, 1, PIXEL_HEIGHT * PIXEL_WIDTH, pixels, &status)){
		fits_report_error(stderr, status);
	}
	/* close the file */
	if (fits_close_file(file, &status)){
		fits_report_error(stdout, status);
	}

	return 1;
}

/** 
	returns number of digits in an int
	*/
int numDigits(int number){
	int length = 1;
	while ( number /= 10 )
		length++;
	return length;
}


std::string getTime(){
	time_t rawtime;
	struct tm * ptm;
	time(&rawtime);
	/* pointer to time object with UTC time */
	ptm = gmtime(&rawtime);
	;
	int hours = ptm->tm_hour;
	int minutes = ptm->tm_min;
	int seconds = ptm->tm_sec;
	/* pad the hours, minutes, seconds with a zero if its only 1 digit long eg. 0-9) */
	std::string h = std::string(2 - numDigits(hours), '0').append(NumberToString(hours));
	std::string m = std::string(2 - numDigits(minutes), '0').append(NumberToString(minutes));
	std::string s = std::string(2 - numDigits(seconds), '0').append(NumberToString(seconds));
	std::string time = h + ":" + m + ":" + s;
	//@TODO check if seconds could contain the fractional seconds as well
	return time;
}

std::string getDate(){

	time_t rawtime;
	struct tm * ptm;
	time(&rawtime);
	/* pointer to time object with UTC time */
	ptm = gmtime(&rawtime);
	int year = ptm->tm_year + 1900; /* ptm->tm_year == years since 1900 */
	int month = ptm->tm_mon + 1;
	int day = ptm->tm_mday;
	/* pad the months with a zero if its only 1 digit long eg. 0-9) */
	std::string y = NumberToString(year);
	std::string m = std::string(2 - numDigits(month), '0').append(NumberToString(month));
	std::string d = std::string(2 - numDigits(day), '0').append(NumberToString(day));
	std::string date = y + "-" + m + "-" + d;
	return date;
}

std::string NumberToString(int Number)
{
	std::stringstream ss;
	ss << Number;
	return ss.str();
}

void setDate(fitsfile *file, int option){
	
	int status = 0;
	std::string date = getDate();
	std::string time = getTime();

	if (option == 0){
		if (fits_write_key(file, TSTRING, "DATE-OBS", (void *) date.c_str(), "", &status)){
			printError(status, "setDate while writing keyword DATE-OBS");
		}
		if (fits_write_key(file, TSTRING, "TIME-OBS", (void *) time.c_str(), "", &status)){
			printError(status, "setDate while writing keyword TIME-OBS");
		}
	}
	else if (option == 1){
		if (fits_write_key(file, TSTRING, "DATE-OBS", (void *) (date.append("T").append(time)).c_str(), "", &status)){
			printError(status, "setDate while writing keyword DATE-OBS, option == 1");
		}
	}
	else{
		printf("INCORRECT USE OF setDate() INVALID PARAMETER OPTION (must be 0 or 1, your input: %d)", option);
	}
}

/* Note: for proper output, include function name at beginning of message */
void printError(int status, const char * message){
	printf("(FITSIO) ERROR OCCURED IN FUNCTION %s, STATUS NUMBER: %d\n", message, status);
}