#Setting Up APLpy for Use With mplot1
To get started with APLpy, you first need to install it through Canopy's built-in package manager.  The package is called **APLpy 0.9.6-1**, and can be found by searching "aplpy" in the package manager's search bar.

Before you can start using APLpy, you will need a few more things:
- PyFITS
- pywcs
- Microsoft Visual C++ Compiler for Python 2.7

PyFITS can also be installed through Canopy's package manager.  The package is called **pyfits 3.3-1** and can be found by typing "pyfits" in the package manager's search bar.

Before you can install pywcs, you must install the Microsoft Visual C++ Compiler for Python 2.7, which can be found [here](https://www.microsoft.com/en-us/download/details.aspx?id=44266).

pywcs *cannot* be found in Canopy's package manager.  To install it, launch Canopy's command prompt (if you are using Windows, this should be located in your Start menu) and then type:
>pip install pywcs

This should install pywcs as a package in Canopy.  Note that a package installed through the command line will not show up in Canopy's package manager.  As long as the command prompt confirms a successful installation, the package will be usable in Canopy.

The last step before you can start using APLpy with mplot1 is to update it and numpy through the Canopy command line.  To do this:
- Close all Canopy windows (If you do not close all Canopy windows before upgrading, you will receive an error message in the command prompt)
- Open Canopy 64-bit command prompt (or its 32-bit equivalent)
- Type:

>pip install aplpy --upgrade

APLpy and numpy will then be updated to the latest versions.  These upgrades will take a while, so do not close the command prompt or open Canopy until you have received confirmation that the upgrade is complete.
