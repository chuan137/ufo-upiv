#!/usr/bin/env python
import sys
import PIL
from scipy import misc
import math
import matplotlib.pyplot as plt

if (len(sys.argv) < 2):
    file_str = 'cands.txt'
    f = open(file_str,'r');
else:
    file_str = sys.argv[1];
    f = open(file_str,'r');

first = plt.imread('sampleC-0050.tif')
second = plt.imread('sampleC-0050.tif')

my_cmap = plt.cm.get_cmap('gray');

fig = plt.figure();
ax = fig.add_subplot(1, 1, 1);

old_r = 0;
cnt = 0;
color_array = ['r','g','b','k','y','c','w'];
with open(file_str) as f:
    for l in f.readlines():
        A = l.strip().split("\t");
        r = math.floor(float(A[2])); #hack
        
        if r != old_r:
            cnt += 1;
            old_r = r;
            
        
        if cnt > 6:
            cnt = 0;

        circ = plt.Circle((A[0],A[1]), radius = r, color=color_array[cnt],fill=False);
        ax.add_patch(circ)


f.close();
ax.add_patch(circ);
plt.imshow(first,cmap=my_cmap);
plt.title(file_str)
plt.show()











