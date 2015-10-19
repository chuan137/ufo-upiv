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


        if r < 10:
          #  col = '0A3D70';
            col = 'MintCream'
            col = '7400ff'
        elif r < 20:
         #   col = '147AE0';
            col = 'Azure'
            col = '4400ff'
        elif r < 30:
          #  col = '1EB850';
             col = 'LightCyan'
             col = '1400ff'
        elif r < 40:
          #  col = '28F5C0'
            col = 'PaleTurquoise'
            col = '001bff'
        elif r < 50:
         #   col = '333330'
            col = 'GreenYellow'
            col = '004bff'
        elif r < 60:
          #  col = '3D70A0'
            col = 'LightGreen'
            col = '007bff'
        elif r < 70:
           # col = '47AE10'
            col = 'PaleGreen'
            col = '00abff'
        elif r < 80:
            #col = '51EB80'
            col = 'DarkSeaGreen'
            col = '00dbff'
        elif r < 90:
            #col = '5C28F0'
            col = 'DarkKhaki'
            col = '00fff3'
        elif r < 100:
            #col = '666660'
            col = 'YellowGreen'
            col = '00ffc3'
        elif r < 110:
            #col = '70A3D0'
            col = 'SpringGreen'
            col = '00ff93'
        elif r < 120:
            #col = '7AE140'
            col = 'Lime'
            col = '00ff63'
        elif r < 130:
            #col = '851EB0'
            col = 'Aquamarine'
            col = '00ff33'
        elif r < 140:
            #col = '8F5C20'
            col = 'MediumSpringGreen'
            col = '00ff03'
        elif r < 150:
            #col = '999990'
            col = 'Turquoise'
            col = '2dff00'
        elif r < 160:
            #col = 'A3D700'
            col = 'MediumSeaGreen'
            col = '5dff00'
        elif r < 170:
            #col = 'AE1470'
            col = 'Chartreuse'
            col = '8dff00'
        elif r < 180:
            #col = 'B851E0'
            col = 'LawnGreen'
            col = 'bdff00' 
        elif r < 190:
            #col = 'C28F50'
            col = 'LimeGreen'
            col = 'edff00'
        elif r < 200:
            #col = 'CCCCC0'
            col = 'DarkSlateGray'
            col = 'ffe100'
        elif r < 210:
            #col = 'D70A30'
            col = 'SeaGreen'
            col = 'ffb100'
        elif r < 220:
            #col = 'E147A0'
            col = 'SeaGreen'
            col = 'ff8100'
        elif r < 230:
            #col = 'EB8510'
            col = 'ForestGreen'
            col = 'ff5100'
        elif r < 240:
            #col = 'F5C280'
            col = 'MediumAquaMarine'
            col = 'ff2100'
        elif r < 250:
            #col = 'FFFFF0'
            col = 'CadetBlue'
            col = 'ff000e'

#        circ = plt.Circle((2*int(A[0]),2*int(A[1])), radius = r, color=color_array[cnt%len(color_array)],fill=False);
#       circ = plt.Circle((int(A[0]),int(A[1])), radius = r, color = '#' + col,fill=False);
        circ = plt.Circle((int(A[0]),int(A[1])), radius = r, color = '#' + col,fill=False);
        ax.add_patch(circ)


f.close();
ax.add_patch(circ);
plt.imshow(first,cmap=my_cmap);
plt.title(file_str)
plt.savefig(outpath, dpi=300,bbox_inches='tight')

