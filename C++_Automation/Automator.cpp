/* 
	To use .lib file, go to Project > References... > Configuration Properties > Linker > 
   > General > Additional Library directories | add the directory the .lib is in.

   Then go to Project > References... > Configuration Properties > Linker > Input > Additional dependencies |
   add the name of the .lib file ("<name>.lib")
*/

/* 
	Image taking proccess is currently under a second, compare efficiency of GUI verses our technique
*/

/* TODO:
			- Allow users to input date format using strptime()
			- Make a Makefile to make building project with other compilers
*/


#include "stdafx.h"
#include <cstdio>
#include <direct.h>
#include "fitsio.h"
#include "getopt.h"
#include <iostream>
#include "longnam.h"
#include <sstream>
#include "Shlwapi.h"
#include <string>
#include <time.h>
#include "SXUSB.h"
#include <Windows.h>

/* for camera */
#define NUMBER_OF_CAMERAS 1
#define PIXEL_WIDTH 1392
#define PIXEL_HEIGHT 1040

/* for hdus */
#define OBJECT "allsky"
#define ORIGIN ""
#define TELESCOP ""
#define INSTRUME "Starlight Xpress Oculus"
#define OBSERVER "UMD Observatory"

/* path info */
#ifdef MAX_PATH
	#define MAX_FILE_LEN MAX_PATH
#else
	#define MAX_FILE_LEN 1024
#endif

bool dirExists(const char *);
bool my_mkdir(char *);
bool unix_mkdir(const char *);
bool windows_mkdir(const char *);
int numDigits(int);
int takeStandardImage(HANDLE handle, int camIndex, USHORT *pixelArray, struct Params * params);
int writeImage(HANDLE handle, int camIndex, USHORT *pixelArray, char *, struct Params * params);
int writeMultipleImages(HANDLE handle, int camIndex, USHORT *pixelArray, struct Params * params);
std::string getDate();
std::string getTime();
std::string numberToString(int number);
void correctDir(char dir[]);
void printError(int, const char *);
void setDate(fitsfile *, int);

struct Params        /* structure used to store parameter information */
{
	bool overwrite;					/* -f */
	bool verbose;					/* -v */
	char dirName[MAX_PATH];			/* -d <string> */
	char observatory[MAX_PATH];		/* -o <string> */
	char templateName[MAX_PATH];	/* -t <string> */
	float exposure;					/* -e <float>  NOTE: in seconds */
	float sleepTime;				/* -s <float> Sleep time in between taking images */
	int dateOption;					/* -u <int> */	
	int initialIndex;				/* -i <int> */
	int numImages;					/* -n <int> */

	Params():	
				overwrite(false),
				verbose(false),
				exposure(1.0),
				sleepTime(0.0),
				dateOption(0),
				initialIndex(0),
				numImages(1){}
};

/* declare these out here so that memory is stored in the heap */
USHORT pixels[PIXEL_WIDTH * PIXEL_HEIGHT];
	
/* constants */
short const BITPIX = USHORT_IMG;
short const NAXIS = 2;
short const NAXIS1 = PIXEL_HEIGHT;
short const NAXIS2 = PIXEL_WIDTH;
const long	NAXES[2] = {PIXEL_WIDTH, PIXEL_HEIGHT};


int main(int argc, char **argv)
{


	/* local variables */
	HANDLE handles[NUMBER_OF_CAMERAS];
	t_sxccd_params cam_params[NUMBER_OF_CAMERAS];
	long firmwareVersions[NUMBER_OF_CAMERAS];
	int openVal, cameraModels[NUMBER_OF_CAMERAS];
	struct Params *params = new Params();
	/* default values for strings in params */
	strcpy(params->dirName, "test_data\\");
	strcpy(params->templateName, "IMG%05d.fits");
	strcpy(params->observatory, "defaultObs");

	/* parse command line arguments */
	int c;
	while ((c = getopt(argc, argv, "o:e:n:d:t:s:i:ufv")) != -1)
    switch (c){
	case 'o':
		strcpy(params->observatory, optarg);
		break;
	case 'e':
		params->exposure = strtol(optarg, NULL, 10);
		break;
	case 'n':
		params->numImages = strtol(optarg, NULL, 10);
		break;
	case 'd':
		strcpy(params->dirName, optarg);
		break;
	case 't':
		strcpy(params->templateName, optarg);
		break;
	case 's':
		params->sleepTime = strtol(optarg, NULL, 10);
		break;
	case 'u':
		params->dateOption = strtol(optarg, NULL, 10);
		break;
	case 'i':
		params->initialIndex = strtol(optarg, NULL, 10);
		break;
	case 'f':
		params->overwrite = true;
		break;
	case 'v':
		params->verbose = true;
		break;
	default:
		break;
      }

	

	/* open the connected cameras */
	openVal = sxOpen(handles);
	if (params->verbose){
		printf("Opened Cameras: %d\n", openVal);
	}

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
		if (params->verbose){
			printf("Camera %d:\n", i);
			printf("\tCamera Firmware Version: %d\n", (firmwareVersions[i] = sxGetFirmwareVersion(handles[i])));
			printf("\tCamera Model: %d\n", (cameraModels[i] = sxGetCameraModel(handles[i])));
		}
		sxGetCameraParams(handles[i], i, cam_params);
	}

	/* Taking images */
	writeMultipleImages(handles[0], 0, pixels, params);

	return 0;
}

/** 
	Takes an image with a connected camera. The camera exposes for the given time and then reads the image into pixels
	@param exposure - this is measured in milliseconds
	@return - 1 if the image was taken correctly, 0 if the image had an error. Will attempt to print error message.
*/

int takeStandardImage(HANDLE handle, int camIndex, USHORT *pixelArray, struct Params *params){
	try{
		int bytesRead;
		/* clear pixels on the camera and expose them to take the image */
		sxClearPixels(handle, 0x00, camIndex);
		sxExposePixels(handle, 0x8B, camIndex, 0, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 1, 1, (ULONG) (params->exposure * 1000));
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
int writeMultipleImages(HANDLE handle, int camIndex, USHORT *pixelArray, struct Params * params){
	
	int imagesTaken = 0;
	char newPath[MAX_PATH];
	if (params->verbose){
		printf("Attempting to write %d images\n", params->numImages);
	}

	for (int i = 0; i < params->numImages; i++){
		try{
			/* <templateName>.fits */
			sprintf_s(newPath, MAX_PATH - 1, params->templateName, imagesTaken + params->initialIndex);
			writeImage(handle, camIndex, pixelArray, newPath, params);
		}
		catch(int e){
			printf("CAUGHT ERROR %d while taking multiple images, stopped after %d images\n", e, imagesTaken);
			return imagesTaken;
		}
		imagesTaken++;
		Sleep(params->sleepTime);
	}

	if (params->verbose){
		printf("Succeeded writing %d images\n", imagesTaken); 
	}

	return imagesTaken;


}

/** 
	writes image to given pixelArray to path (NOTE: path does not include extension, that is added by the function).
	@return - 0 if failed, 1 if successfully wrote image.
*/
int writeImage(HANDLE handle, int camIndex, USHORT *pixelArray, char * filename, struct Params * params){

	takeStandardImage(handle, 0, pixels, params);

	/* set up a fits file with proper hdu to write to a file */
	fitsfile *file;
	int status = 0;
	char newPath[MAX_PATH], finalPath[MAX_PATH];

	printf("*Before my_mkdir(): %s\n", params->dirName);

	my_mkdir(params->dirName);
	strcpy(newPath, params->dirName);
	strcat(newPath, filename);

	printf("*After strcat(): %s\n", params->dirName);

	/* if overwrite flag is true add an '!' to the front so that fitsio overwrites files of
		of the same name */
	if (params->overwrite == true){
		strcpy(finalPath, "!");
		strcat(finalPath, newPath);
	}
	else{
		strcpy(finalPath, newPath);
	}
	
	if (params->verbose){
		printf("Writing %s\n", finalPath);
	}
	if (fits_create_file(&file, finalPath, &status)){
		/*fits_report_error(stdout, status);*/
		printError(status, "writeImage, while creating file");
	}
	/* basic header information (BITPIX, NAXIS, NAXES, etc) is taken care of through this function as well) */
	if (fits_create_img(file, BITPIX, NAXIS, (long *) NAXES, &status)){
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
	if (fits_write_key(file, TSTRING, "OBSERVER", (void *) params->observatory, "", &status)){
		printError(status, "writeImage, while writing OBSERVER");
	}
	if (fits_write_key(file, TFLOAT, "EXPTIME", (void *) &(params->exposure), "", &status)){
		printError(status, "writeImage, while writing EXPTIME");
	}

	/* find the current date and time and write it to a keyword(s) */
	setDate(file, params->dateOption);

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

/**
	returns the time in the format HH:MM:DD as a string in UTC time
*/
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
	std::string h = std::string(2 - numDigits(hours), '0').append(numberToString(hours));
	std::string m = std::string(2 - numDigits(minutes), '0').append(numberToString(minutes));
	std::string s = std::string(2 - numDigits(seconds), '0').append(numberToString(seconds));
	std::string time = h + ":" + m + ":" + s;
	//@TODO check if seconds could contain the fractional seconds as well
	return time;
}

/**
	returns the data in the format YYYY-MM-DD as a string in UTC time
*/
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
	std::string y = numberToString(year);
	std::string m = std::string(2 - numDigits(month), '0').append(numberToString(month));
	std::string d = std::string(2 - numDigits(day), '0').append(numberToString(day));
	std::string date = y + "-" + m + "-" + d;
	return date;
}


/**
	converts an int into a string
*/
std::string numberToString(int Number)
{
	std::stringstream ss;
	ss << Number;
	return ss.str();
}

/**
	Sets the date of the fits file in the HDU and the time (in universal time)
	@param option	0: format is	DATE-OBS: <YYYY>-<MM>-<DD>
									TIME-OBS: <HH>:<MM>:<SS>
					1: format is	DATE-OBS: <YYYY>-<MM>-<DD>T<HH>:<MM>:<SS>
*/
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

/**
	Checks if the directory exists, if it does not, creates it
	NOTE: will add a \ to the end of dir if it does not end in one
	@return true if it creates it or it already exists
			false if it could not create the directory
*/
bool windows_mkdir(char * dir){
	correctDir(dir); // correct the directory if it doesnt end in a slash
	unsigned int i = 0;
	/* the logic here is that _mkdir cannot create two new directories inside of each other at the same time
	   (first create \firstDir\ then /firstDir/secondDir/ rather than at the same time)
	   so we copy the original directory over to a temporary and everytime it meets a \ create that directory
	   then once at the end of the string, make that directory too even if it didn't end in a back slash
	 */
	char temp[MAX_PATH]; 
	while (i < strlen(dir)){
		/* copy the current character */
		temp[i] = dir[i];
		/* if its a backslash, create the directory if it doesn't already exist */
		if (dir[i] == '\\'){
			temp[i + 1] = 0;
			if (!dirExists(temp)){
				if (_mkdir(temp) == -1){
					printf("Could not make directory %s :", *dir);
					perror(""); //perror is an empty string since our error note is from the printf above
					printf("\n");
					return false;
				}
			}
		}
		i++;
	}
	return true;
}

bool unix_mkdir(const char * dir){
	printf("unix_mkdir() NOT YET IMPLEMENTED!\n");
	return false;
}

/**
	Calling this function will simply call the corresponding mkdir function for Windows or Unix
*/
bool my_mkdir(char * dir){
#ifdef OS_WINDOWS
	return windows_mkdir(dir);
#else
	return unix_mkdir(dir);
#endif
}

/**
	Checks whether a directory exists
	@return true if it exists
			false if it does not exists
*/
bool dirExists(const char * dirName_in)
{
  DWORD ftyp = GetFileAttributesA(dirName_in);
  if (ftyp == INVALID_FILE_ATTRIBUTES)
    return false;  //something is wrong with your path!

  if (ftyp & FILE_ATTRIBUTE_DIRECTORY)
    return true;   // this is a directory!

  return false;    // this is not a directory!
}


/** 
	checks if the directory ends in a backslash for Windows or forward slash for other machines 
	if it does not, then it will add a backslash/forward slash so it can be created successfully.
*/
void correctDir(char dir[]){
#ifdef OS_WINDOWS
	if (dir[strlen(dir) - 1] != '\\'){
		/* must store strlen(dir) into an int here because once you make dir[len] = \, dir[len] is no longer
		   the terminating character and thus if the array had characters after the terminating character
		   the code will not work as intended */
		int len = strlen(dir);
		dir[len] = '\\';
		dir[len + 1] = 0;
	}
#else
	if (dir[strlen(dir) - 1] != '/'){
		dir[strlen(dir)] = '/';
		dir[strlen(dir) + 1] = 0;
	}
#endif
}