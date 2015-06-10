import sys
import numpy as np
import matplotlib.pyplot as plt
import my_plots as mp
import re

filename = 'summary.pdf'

data = [(0.5, 92.41, 16.08), \
        (1.0, 103.55, 9.66), \
        (2.0, 112.12, 6.88)]

mp.load_style('538.json')
mp.errorbar_plot(data, xlim=(0,2.5), ylim=(50,130))
plt.savefig(filename)
