#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))

from tifffile import tifffile as tif
from numpy import meshgrid, sqrt,zeros,arange,log
from fitting import Fit,gaussian,constant

#==============================================================================
def crop_img(img,x,y,r):
    return img[x-r:x+r+1, y-r:y+r+1]
def azimu_hist(img,x0,y0,r0):
    h = zeros(1.5*r0)
    s = zeros(1.5*r0)
    for xi in range(x0-r0,x0+r0+1):
        for yi in range(y0-r0,y0+r0+1):
            xx = xi-x0
            yy = yi-y0
            r = sqrt(xx*xx + yy*yy)
            idx = round(r)
            h[idx] += img[xi,yi]
            s[idx] += 1
    for i in range(len(h)):
        if s[i] != 0:
            h[i] = h[i]/s[i]
    return h
def smooth(data):
    res = zeros(len(data))
    for i in range(1,len(data)-1):
        res[i] = 0.5*data[i] + 0.25*data[i-1] + 0.25*data[i+1]
    res[0] = 0.5*data[0] + 0.5*data[1]
    res[-1] = 0.5*data[-1] + 0.5*data[-2]
    return res
def test_fit_data(data):
    peak = 0
    for i in range(len(data)-1):
        if data[i] > data[i+1]:
            peak = i
            break
    if peak != len(data)/2:
        return True
    for i in range(peak, len(data)-1):
        if data[i] < data[i+1]:
            return True
    return False
def test_fit_res(a,b,c):
    for r in a,b,c:
        if r[1] > r[0]:
            return True
        if r[0] < 0:
            return True
    return False
#==============================================================================

cad_file = '../res/sampleB/candidate_1.txt'


with open(cad_file, 'r') as f:
    for line in f:
        try:
            x,y,r,_,_ = line.split()
        except:
            pass

img_file = '../res/sampleB/contrast_1.tif'
img = tif.imread(img_file).T
r1 = azimu_hist(img,732,342,100)
r2 = azimu_hist(img,594,458,100)

img_file = '../data/sampleB/001.tif'
img = tif.imread(img_file).T
r3 = azimu_hist(img,732,342,100)
r4 = azimu_hist(img,594,458,100)
r5 = azimu_hist(img,594,459,100)

num = 7

ft = Fit()
ft.f = gaussian
ft.x = arange(num)

data = r1

for i in range(len(data)-num):
    ft.y = data[i:i+num]
    try:
        if test_fit_data(ft.y):
            continue
        res = ft.fit(ft.y[2],2,1)
        if test_fit_res(*res):
            continue
        print 
        print i+num/2, ft.y 
        print res
        a = data[i+2*num:i+2*num+40].std()
        b = data[i+2*num:i+2*num+40].mean()
        snr = (res[0][0]-b)/a
        print a,b,res[0][0]
        print snr, 20*log(snr)/log(10)
    except:
        pass

