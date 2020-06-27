#! /usr/bin/env python
#
# Takes about 15" for 1400 images on laptop with a local fast disk (100% cpu)
# But 60" on the Xeon, but at 300% cpu
#
import matplotlib.pyplot as plt
import numpy as np
import sys

table = sys.argv[1]
png   = table + '.png'
twopi = 2*np.pi

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

print(tmin,tmax)
x = (12-t) * twopi / 24.0
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

if False:
    # always same pie, an extra hour either side
    tmin=75
    tmax=285
print(tmin,tmax)
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



# needs tweaking
plt.text(3.14,50000,'midnight',horizontalalignment='center')
plt.text(1.1,42000,'sunrise')
plt.text(5.1,48000,'sunset')
plt.text(5.5,20000,'imagine a moon')

plt.title("%s sky: %g %g  %g-%g h" % (table,s.min(),s.max(),t0,t1))
plt.savefig(png)
plt.show()

print("Written ",png)

