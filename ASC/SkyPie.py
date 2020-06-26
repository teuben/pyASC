#! /usr/bin/env python
#
import matplotlib.pyplot as plt
import numpy as np
import sys

date = ''
table = sys.argv[1]
twopi = 2*np.pi

# hours
t0 = 18.0
t1 =  6.0

t0 = 17.0
t1 =  7.0

# degrees for polar plot
tmin = (t0-12.0)*180/12.0
tmax = 360 - (12-t1)*180/12.0

#   table of time index (1...N) and median sky brightness (50,000 is very bright)
(t,s) = np.loadtxt(table).T
print("Sky: ",s.min(),s.max())
print("Time:",t.min(),t.max())

x = (12+24-t) * twopi / 24.0
#x = t * twopi / 24.0 

y = s.max()-s

print(x.min(),x.max())
print(y.min(),y.max())

fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection='polar'))

ax.plot(x, y)
ax.set_theta_zero_location('S')
ax.xaxis.set_major_formatter(plt.NullFormatter())
ax.xaxis.set_major_formatter(plt.NullFormatter())
ax.yaxis.set_major_formatter(plt.NullFormatter())
ax.yaxis.set_major_formatter(plt.NullFormatter())
ax.set_thetamin(tmin)
ax.set_thetamax(tmax)
    
ya = 0.2 * y    
yb = 0.4 * y    
yc = 0.8 * y   
yd = 0.8 * y    
ye = 0.9 * y    
ax.fill_between(x,0, ya,facecolor='green',alpha=0.1)
ax.fill_between(x,ya,yb,facecolor='green',alpha=0.3)
ax.fill_between(x,yb,yc,facecolor='green',alpha=0.5)
ax.fill_between(x,yc,yd,facecolor='green',alpha=0.7)
ax.fill_between(x,yd,ye,facecolor='green',alpha=0.85)
ax.fill_between(x,ye,y ,facecolor='green',alpha=1)


#fig1, ax1 = plt.subplots(1, 1)
#plt.plot([0,1],[0,1])

plt.text(3.14,50000,'midnight',horizontalalignment='center')
plt.text(1.1,42000,'sunrise')
plt.text(5.1,48000,'sunset')
plt.text(5.5,20000,'image a moon')

plt.title("%s sky: %g %g  %g-%g h" % (date,s.min(),s.max(),t0,t1))
plt.savefig("allsky-polar.png")
plt.show()

