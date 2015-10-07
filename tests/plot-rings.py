#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))

from tifffile import tifffile as tif
from scipy import misc
import math
import matplotlib.pyplot as plt

try:
    first = tif.imread(sys.argv[1]);
except IndexError:
    sys.exit('no image file is appointed')
except IOError:
    sys.exit('correct path?')
except ValueError:
    sys.exit('require tif file')
except:
    sys.exit('unknown error')

try:
    file_str = sys.argv[2];
except IndexError:
    file_str = 'cands.txt'
try:
    f = open(file_str,'r');
except:
    sys.exit('fail to open candidate list %s' % file_str)
outpath=os.path.splitext(file_str)[0]+ '.png'

my_cmap = plt.cm.get_cmap('gray');

fig = plt.figure();
ax = fig.add_subplot(1, 1, 1);

old_r = 0;
cnt = 0;
color_array = ['r','g', 'b','y','c', 'w'];
with open(file_str) as f:
    for l in f.readlines():
        if l[0] == '#':
            continue
        A = l.split()

        try:
            r = float(A[2])
        except:
            continue
        
        if r != old_r:
            cnt += 1;
            old_r = r;

        if r>1024:
            continue
        
        circ = plt.Circle((A[0],A[1]), radius = r, color=color_array[cnt%len(color_array)],fill=False);
        ax.add_patch(circ)

f.close();
ax.add_patch(circ);
plt.imshow(first,cmap=my_cmap);
plt.title(file_str)
plt.savefig(outpath)

