// Automator.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <iostream>
#include "definitions.h"
#include <windows.h> 

using namespace std;


struct t_sxccd_params
{
    USHORT hfront_porch;
    USHORT hback_porch;
    USHORT width;
    USHORT vfront_porch;
    USHORT vback_porch;
    USHORT height;
    float  pix_width;
    float  pix_height;
    USHORT color_matrix;
    BYTE   bits_per_pixel;
    BYTE   num_serial_ports;
    BYTE   extra_caps;
    BYTE   vclk_delay;
};


typedef int (*sxOpenType)(HANDLE);
typedef ULONG (*sxGetCameraParamsType)(HANDLE, USHORT, t_sxccd_params);



int main()
{	

	BOOL freeResult, runTimeLinkSuccess = FALSE; 
	HINSTANCE dllHandle = NULL; 
	sxOpenType sxOpenPtr = NULL;
	sxGetCameraParamsType sxGetCameraParamsPtr = NULL;
	HANDLE handles[20];
	HANDLE *phandles = handles;
	int openVal; BOOL opened = false;

	dllHandle = LoadLibrary(L"SxUSB.dll");
	

	if (NULL != dllHandle){
		//Get pointer to our function using GetProcAddress:
		//change sxOpenPtr to <function name>Ptr and sxOpenType to <function name>Type and "sxOpen" to "<function name>"
		sxOpenPtr = (sxOpenType)GetProcAddress(dllHandle, "sxOpen");

		// If the function address is valid, call the function. 
		//change sxOpenPtr to <function name>Ptr
		if (runTimeLinkSuccess = (NULL != sxOpenPtr))
		{

			openVal = sxOpenPtr(handles);
			cout << "Opened Cameras: " << openVal << endl;
		}

		//Free the library:
		freeResult = FreeLibrary(dllHandle);
	}

	t_sxccd_params* cParams = new t_sxccd_params[openVal];

	//Get Camera Paramters
	//incomplete
	if (NULL != dllHandle){
		//Get pointer to our function using GetProcAddress:
		sxGetCameraParamsPtr = (sxGetCameraParamsType)GetProcAddress(dllHandle, "sxGetCameraParams");
		// If the function address is valid, call the function. 
		if (runTimeLinkSuccess = (NULL != sxOpenPtr))
		{
			for (int i = 0; i < openVal; i++){
				sxGetCameraParamsPtr(phandles[0], 0, *cParams);
			}
		}

		//Free the library:
		freeResult = FreeLibrary(dllHandle);
	}

	delete [] cParams;
	return 0;
}

