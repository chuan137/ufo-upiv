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
COL_R = ['ff000e', 'ff2100', 'ff5100',  'ff8100', 'ffb100', 'ffe100', 'edff00', 'bdff00', '8dff00','5dff00', '2dff00', '00ff03', '00ff33', '00ff63', '00ff93', '00ffc3', '00fff3', '00dbff', '00abff', '007bff', '004bff', '001bff', '1400ff', '4400ff', '7400ff'];
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


;
        circ = plt.Circle((int(A[0]),int(A[1])), radius = r, color = '#' + COL_R[int(math.floor(r/10))],fill=False);
        ax.add_patch(circ)


f.close();
ax.add_patch(circ);
plt.imshow(first,cmap=my_cmap);
plt.title(file_str)
plt.savefig(outpath, dpi=300,bbox_inches='tight')

