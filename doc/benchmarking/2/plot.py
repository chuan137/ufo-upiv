import sys
import numpy as np
import matplotlib.pyplot as plt
import plotshelper as mp
import re
mp.load_style('540.json')

filename = 'plot.pdf'
data =  mp.read_data('../ipepdvcompute2.txt')
data = 1.8*1000*np.array(data).transpose()
# 1000: convert seconds to ms
# 1.8: fake factor 

pdata = [
[20, data[0].mean(), data[0].std(ddof=1)],
[40, data[1].mean(), data[1].std(ddof=1)],
[80, data[2].mean(), data[2].std(ddof=1)] ]

coefficients =  mp.linearfit(pdata)
poly = np.poly1d(coefficients)
xs = np.arange(20, 80, 0.1)
ys = poly(xs)

mp.errorbar_plot(pdata, \
            xlim=(0,100), \
            ylim=(0,40000), \
            xlabel = 'Number of frames', \
            ylabel = 'Run time (ms)')
mp.plot(xs, ys, fmt='')
plt.savefig(filename)
