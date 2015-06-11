import sys
import numpy as np
import matplotlib.pyplot as plt
import plotshelper as mp
import re

filename = 'plot.pdf'
#mp.load_style('538.json')

data = [(1, 163),\
        (2, 167)]


mp.bar_plot(data, 0.4, \
            xlim=(0,3), \
            ylim=(100,200), \
            xticks = (0, 1, 2, 3), \
            xlabel = 'Number of GPUs', \
            ylabel = 'Run time (ms)')
plt.savefig(filename)
