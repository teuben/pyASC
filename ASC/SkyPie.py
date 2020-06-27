#! /usr/bin/env python
#
# Takes about 15" for 1400 images on laptop with a local fast disk (100% cpu)
# But 60" on the Xeon, but at 300% cpu
#
import matplotlib.pyplot as plt
import numpy as np
import sys

#   plt.rcParams.update({'font.size': 10})
SMALL_SIZE = 8
MEDIUM_SIZE = 8
BIGGER_SIZE = 8



twopi = 2*np.pi

def plot1(table,ax,Qtitle,title=None):
    #   table of decimal hour time and median sky brightness (50,000 is very bright)
    (t,s) = np.loadtxt(table).T
    print("Sky: ",s.min(),s.max())
    print("Time:",t.min(),t.max())

    t0 = t[0]
    t1 = t[-1]
    print(t0,t1)

    # tmin is the sunrise, from t1 (6), should be near 90
    # tmax is the sunset, from t0 (18)                270
    tmin = (6-t1)*15  +  90
    tmax = (18-t0)*15 + 270

    smax = 64000
    
    print(tmin,tmax)
    x = (12-t) * twopi / 24.0
    y = s.max()-s
    y = smax-s
    
    print(x.min(),x.max())
    print(y.min(),y.max())



    ax.plot(x, y)
    ax.set_theta_zero_location('S')
    ax.set_ylim([0,smax])
    ax.xaxis.set_major_formatter(plt.NullFormatter())
    ax.xaxis.set_major_formatter(plt.NullFormatter())
    ax.yaxis.set_major_formatter(plt.NullFormatter())
    ax.yaxis.set_major_formatter(plt.NullFormatter())
    
    if False:
        # always same pie, an extra hour either side
        tmin=75
        tmax=285
    print(tmin,tmax)
    ax.set_thetamin(tmin)
    ax.set_thetamax(tmax)
    y1 = y
    if False:
        y1 = y*0 + smax
    
    ya = 0.2 * y1    
    yb = 0.4 * y1   
    yc = 0.8 * y1  
    yd = 0.8 * y1   
    ye = 0.9 * y1   
    ax.fill_between(x,0, ya,facecolor='green',alpha=0.1)
    ax.fill_between(x,ya,yb,facecolor='green',alpha=0.3)
    ax.fill_between(x,yb,yc,facecolor='green',alpha=0.5)
    ax.fill_between(x,yc,yd,facecolor='green',alpha=0.7)
    ax.fill_between(x,yd,ye,facecolor='green',alpha=0.85)
    ax.fill_between(x,ye,y ,facecolor='green',alpha=1)
    if title != None:
        ax.text(0,smax/2,title,horizontalalignment='center')
        #ax.set_title(title)

    if Qtitle:
        plt.title("%s sky: %g-%g  %.3f-%.3f h" % (table,s.min(),s.max(),t0,t1))

        # needs tweaking
        plt.text(3.14,smax*1.1,'midnight',horizontalalignment='center')
        plt.text(1.2,smax,'sunrise',horizontalalignment='left')
        plt.text(twopi-1.2,smax,'sunset',horizontalalignment='right')
        plt.text(0,smax/4,'imagine a moon',horizontalalignment='center')
        


ntable = len(sys.argv[1:])
table = sys.argv[1]
png   = table + '.png'

if ntable == 1:
    Qtitle = True
else:
    Qtitle = False


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

fig, ax = plt.subplots(ny, nx, subplot_kw=dict(projection='polar'))

if ntable > 1:
    plt.subplots_adjust(hspace = .001,wspace=0.001, left=0.01, right=0.99, bottom=0.01, top=0.99)
#      left  = 0.125  # the left side of the subplots of the figure
#      right = 0.9    # the right side of the subplots of the figure
#      bottom = 0.1   # the bottom of the subplots of the figure
#      top = 0.9      # the top of the subplots of the figure
#      wspace = 0.2   # the amount of width reserved for blank space between subplots
#      hspace = 0.2   # the amount of height reserved for white space between subplots

if Qtitle:
    plot1(table,ax,True)
else:    
    k = 1
    for i in range(nx):
        for j in range(ny):
            plot1(sys.argv[k],ax[j][i],False,sys.argv[k])
            k = k+1


plt.savefig(png)
plt.show()

print("Written ",png)

