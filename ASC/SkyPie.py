#! /usr/bin/env python3
#
# Takes about 15" for 1400 images on laptop with a local fast disk (100% cpu)
# But 60" on the Xeon, but at 300% cpu
#
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import sys

#   plt.rcParams.update({'font.size': 10})
SMALL_SIZE = 8
MEDIUM_SIZE = 8
BIGGER_SIZE = 8


twopi = 2*np.pi

def plot1(table,ax1,ax2,fig,Qtitle,title=None,invert=True,raw=False):
    # invert:      this will place dark sky on the outside of the pie
    
    #   table of decimal hour time and median sky brightness (50,000 is very bright)
    # (t,s,ffile) = np.loadtxt(table).T
    loaded = np.genfromtxt(table, dtype=None, delimiter=' ')
    print(loaded[0],'\n\n')
    # read the first line, it has sunrise and sunset times
    fline = open(sys.argv[1]).readline().rstrip()[1:].split(' ')
    try:
        (t,s,e,m) = np.array([t[0] for t in loaded]), np.array([t[1] for t in loaded]), np.array([t[2] for t in loaded]), np.array([t[3] for t in loaded])
        print(t)
        print("Time:",t.min(),t.max())
        print("Sky: ",s.min(),s.max())
        print("Exp: ",e.min(),e.max())
        print("Moon:",m.min(),m.max())
        amp = (m.min() + m.max())/2.0     # average moon phase
    except:
        # older format with only 2 columns
        (t,s) = np.array([t[0] for t in loaded]), np.array([t[1] for t in loaded])
        print(t)
        print("Time:",t.min(),t.max())
        print("Sky: ",s.min(),s.max())
        amp = -2.0
        
    t0 = t[0]
    t1 = t[-1]
    print(t0,t1)

    # tmin is the sunrise, from t1 (6), should be near 90
    # tmax is the sunset, from t0 (18)                270
    tmin = (6-t1)*15  +  90
    tmax = (18-t0)*15 + 270

    smax = 64000
    emax = e.max()

    print(tmin,tmax)
    x = (12-t) * twopi / 24.0
    if invert:
        #    dark sky on outside of the pie
        #y = s.max()-s
        y = smax - s
        print("y",invert,y.min(),y.max())
        p = e
        print("p",invert,p.min(),p.max())
    else:
        y = s
        print("y",invert,y.min(),y.max())
        p = e
        print("p",invert,p.min,p.max)

    ax1.text(2, -0.2, 'Key:\nRed Line: Sunset\nBlue Line: Sunrise', horizontalalignment='center', transform=ax1.transAxes)

    ax1.plot(x, y)
    ax1.set_theta_zero_location('S')
    ax1.set_ylim([0,smax])
    ax1.xaxis.set_major_formatter(plt.NullFormatter())
    ax1.xaxis.set_major_formatter(plt.NullFormatter())
    ax1.yaxis.set_major_formatter(plt.NullFormatter())
    ax1.yaxis.set_major_formatter(plt.NullFormatter())

    ax2.plot(x, p)
    ax2.set_theta_zero_location('S')
    ax2.set_ylim([0,emax])
    ax2.xaxis.set_major_formatter(plt.NullFormatter())
    ax2.xaxis.set_major_formatter(plt.NullFormatter())
    ax2.yaxis.set_major_formatter(plt.NullFormatter())
    ax2.yaxis.set_major_formatter(plt.NullFormatter())

    # angles at which to draw sunrise/sunset
    # makes assumption sunrise will always be after 00:00 and before 12:00
    # and that sunset will allways be after 12:00 and before 00:00
    tset = (12-float(fline[0]))*np.pi/12
    trise = (12-float(fline[1]))*np.pi/12

    # change tmin and tmax to be in [0,360) for ease of use and shifted to 0
    # being east and 90 being north
    tmincorr = np.deg2rad(tmin-(360*((tmin)//360)))
    tmaxcorr = np.deg2rad(tmax-(360*((tmax)//360)))
    # functions to draw sunrise/sunset dashed line
    def annotatesunrise(mult1,mult2):
        ax1.annotate('',
                xy=[0,0],  # theta, radius
                xytext = [trise,smax*mult1],
                arrowprops=dict(linestyle = '--',arrowstyle = '-',color='blue'))
        ax2.annotate('',
                    xy=[0,0],  # theta, radius
                    xytext = [trise,emax*mult2],
                    #textcoords = 'polar',
                    arrowprops=dict(linestyle = '--',arrowstyle = '-',color='blue'))
    def annotatesunset(mult1,mult2):
        ax1.annotate('',
                xy=[0,0],  # theta, radius
                xytext = [tset,smax*mult1],
                arrowprops=dict(linestyle = '--',arrowstyle = '-',color='red'))
        ax2.annotate('',
                xy=[0,0],  # theta, radius
                xytext = [tset,emax*mult2],
                #textcoords = 'polar',
                arrowprops=dict(linestyle = '--',arrowstyle = '-',color='red'))

    # note: the theta values for this plot are shifted by pi/2, so if sin is
    # positive for both max and min, it is only on the right side of plot, so 
    # only annote sunrise
    if np.sin(tmaxcorr) > 0 and np.sin(tmincorr) > 0:
        annotatesunrise(1.1,1.1)
    # note: the theta values for this plot are shifted by pi/2, so if sin is
    # negative for both max and min, it is only on the left side of plot, so 
    # only annote sunrise
    elif np.sin(tmincorr) < 0 and np.sin(tmaxcorr) < 0:
        annotatesunset(1.1,1.1)
    # if they are pretty close (pi/2 close, may need adjusting),
    # just draw them a little bit smaller
    elif abs(tmaxcorr - tmincorr) < np.pi/2:
        annotatesunrise(0.6,0.6)
        annotatesunset(0.6,0.6)
    # else draw both
    else:
        annotatesunrise(1.1,1.1)
        annotatesunset(1.1,1.1)
    
    ax1.set_thetamin(tmin)
    ax1.set_thetamax(tmax)

    ax2.set_thetamin(tmin)
    ax2.set_thetamax(tmax)

    y1 = y
    p1 = p

    ya = 0.2 * y1    
    yb = 0.4 * y1   
    yc = 0.8 * y1  
    yd = 0.8 * y1   
    ye = 0.9 * y1
    ax1.fill_between(x,0, ya,facecolor='green',alpha=0.1)
    ax1.fill_between(x,ya,yb,facecolor='green',alpha=0.3)
    ax1.fill_between(x,yb,yc,facecolor='green',alpha=0.5)
    ax1.fill_between(x,yc,yd,facecolor='green',alpha=0.7)
    ax1.fill_between(x,yd,ye,facecolor='green',alpha=0.85)
    ax1.fill_between(x,ye,y ,facecolor='green',alpha=1)

    pa = 0.2 * p1    
    pb = 0.4 * p1   
    pc = 0.8 * p1  
    pd = 0.8 * p1   
    pe = 0.9 * p1
    ax2.fill_between(x,0, pa,facecolor='orange',alpha=0.1)
    ax2.fill_between(x,pa,pb,facecolor='orange',alpha=0.3)
    ax2.fill_between(x,pb,pc,facecolor='orange',alpha=0.5)
    ax2.fill_between(x,pc,pd,facecolor='orange',alpha=0.7)
    ax2.fill_between(x,pd,pe,facecolor='orange',alpha=0.85)
    ax2.fill_between(x,pe,p ,facecolor='orange',alpha=1)
    if title != None and not raw:
        ax1.text(0,smax/2,title,horizontalalignment='center')

    if Qtitle and not raw:
        plt.suptitle("%s\nLocal Time: %.3f-%.3f h" % (table,t0,t1))
        ax1.set_title("Brightness: %g-%g ADU" % (s.min(),s.max()),fontdict={'fontsize':9}, pad = -20)
        ax2.set_title("Exposure: %g-%g sec" % (e.min(),e.max()),fontdict={'fontsize':9}, pad = -20)
        
        # gets the number of the image to use. Will be a number between 0 and 32,
        # but we there is no 32.png so it is also 0.png. The range of amp is
        # -1 <= amp <= +1, so after multiplying it by 16 and adding 16 we get
        # integers 0 <= image_num <= 31.
        image_num = round(amp*16)+16
        # this occurs when you get +1.0 for moon illumination, so it is a full
        # moon. This is at 0.png
        if image_num == 32:
            image_num = 0

        # if the image_num is out of bounds, just print the error moon value,
        # which we can use to debug.
        if 0 <= image_num <= 32:
            # file names in www/webdings/moons/<0-31>.png
            # will need to change this based on where you run the code from
            # For example: running from pyASC/ASC. the path is ../www/webdings/moons/...
            moonphase_img = mpimg.imread('../www/webdings/moons/' + str(int(image_num)) + '.png')
            if moonphase_img is not None:
                # image exists, put it on the figures
                # do this by creating a new axes at the bottom of the figure and
                # put an image in there
                
                # image placement: adjust x and y for placement, adjust xlen 
                # and ylen for size/aspect ratio
                #                         x   y   xlen ylen.
                newax = fig.add_axes([0.375,0.075,0.25,0.25])
                newax.imshow(moonphase_img)
                newax.axis('off')
                # 0 and 32 == Full Moon
                # 1 - 7 == Waning Gibbous
                # 8 == First Quarter
                # 9 - 15 == Waning Screscent
                # 16 == New Moon
                # 17 - 23 == Waxing Crescent
                # 24 == Last/Third Quarter
                # 25 - 31 == Waxing Gibbous
                moon_type = ""
                if image_num == 0:
                    moon_type = "Full Moon"
                elif image_num == 16:
                    moon_type = "New Moon"
                elif image_num == 24:
                    moon_type = "First Quarter"
                elif image_num == 8:
                    moon_type = "Last/Third Quarter"
                elif 25 <= image_num <= 31:
                    moon_type = "Waxing Gibbous"
                elif 17 <= image_num <= 23:
                    moon_type = "Waxing Crescent"
                elif 1 <= image_num <= 7:
                    moon_type = "Waning Gibbous"
                elif 9 <= image_num <= 15:
                    moon_type = "Waning Crescent"
                pm = ''
                if amp > 0:
                    pm = '+'
                ax1.text(1.1, -0.455, '%s\n%s%g%%' % (moon_type,pm,round(amp*100)), horizontalalignment='center', transform=ax1.transAxes)
            # else, no file found
            else:
                pm = ''
                if amp > 0:
                    pm = '+'
                ax1.text(1.1, -0.2, 'moon file not found\nimage num: %g\n%s%g' % (image_num,pm,round(amp*100)), horizontalalignment='center', transform=ax1.transAxes)
        # this should only happen if an invalid moon illum percentage (amp) is
        # out of the range -1 <= amp <= +1
        # check SkyStats.py for the error
        else:        
            ax1.text(1.1, -0.2, 'invalid moon num\nmoon error: %g' % (amp), horizontalalignment='center', transform=ax1.transAxes)

        print('theta',tmin*3.14/180,tmax*3.14/180)
        ax1.text(3.14,              1.1*smax,   'midnight',        horizontalalignment='center',   fontdict={'fontsize':8})

        ax2.text(3.14,              1.1*emax,   'midnight',        horizontalalignment='center',   fontdict={'fontsize':8})
        


ntable = len(sys.argv[1:])
table = sys.argv[1]
png   = table + '.png'

if ntable == 1:
    Qtitle = True
else:
    Qtitle = False

Qraw = False    # set to true if you don't want any labeling around the plot, just the pie

if ntable > 1:
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


nx = int(np.sqrt(ntable))
ny = ntable // nx

print(nx,ny)

# ax1 is will be the brightness/green graph. ax2 will be the exposure/orange graph
fig, (ax1,ax2) = plt.subplots(1,2,subplot_kw=dict(projection='polar'))

plt.subplots_adjust(hspace = .001,wspace=0.2, left=0.01, right=0.99, bottom=0.15, top=0.99)
#      left  = 0.125  # the left side of the subplots of the figure
#      right = 0.9    # the right side of the subplots of the figure
#      bottom = 0.1   # the bottom of the subplots of the figure
#      top = 0.9      # the top of the subplots of the figure
#      wspace = 0.2   # the amount of width reserved for blank space between subplots
#      hspace = 0.2   # the amount of height reserved for white space between subplots

if Qtitle:
    plot1(table,ax1,ax2,fig,True,raw=Qraw)
else:    
    k = 1
    for i in range(nx):
        for j in range(ny):
            plot1(sys.argv[k],ax1[j][i],ax2[j][i],False,sys.argv[k])
            k = k+1

plt.savefig(png)

print("Written ",png)

# convert input.png -crop 400x400+128+64 -resize 40x40^   input.thumb.png