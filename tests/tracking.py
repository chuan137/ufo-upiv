#!/usr/bin/env python
import sys
import PIL
from scipy import misc
import math
import matplotlib.pyplot as plt
import array


if (len(sys.argv) < 2):
    file_str = 'cands.txt'
    file_str_2 = 'cands_2.txt'
    f = open(file_str,'r');
    f_2 = open(file_str_2,'r');
else:
    file_str = sys.argv[1];
    file_str_2 = sys.argv[2];
    f = open(file_str,'r');
    f_2 = open(file_str_2,'r');

cnt_1 = 0;
cnt_2 = 0;
cnt_3 = 0;

x_array_1 = array.array('i',[0]*400);
y_array_1 = array.array('i',[0]*400);
r_array_1 = array.array('i',[0]*400);

x_array_2 = array.array('i',[0]*400);
y_array_2 = array.array('i',[0]*400);
r_array_2 = array.array('i',[0]*400);

pos_array_1 = array.array('i',[0]*400);
pos_array_2 = array.array('i',[0]*400);

x_distance = array.array('i',[0]*400);
y_distance = array.array('i',[0]*400);
z_distance = array.array('i',[0]*400);

#read in both files
with open(file_str) as f:
    for l in f.readlines():
        x_1,y_1,r_1 = l.strip().split("\t");
        x_array_1[cnt_1] = int(x_1);
        y_array_1[cnt_1] = int(y_1);
        r_array_1[cnt_1] = int(math.floor(float(r_1)));
        cnt_1 += 1;

with open(file_str_2) as f_2:
    for l in f_2.readlines():
        x_2,y_2,r_2 = l.strip().split("\t");
        x_array_2[cnt_2] = int(x_2);
        y_array_2[cnt_2] = int(y_2);
        r_array_2[cnt_2] = int(math.floor(float(r_2)));
        cnt_2 += 1;


#looks if there are any trackable objects --> saves into two vectors,pos_array_1 (past) and pos_array_2
for i in range(0,cnt_2): #current
    for k in range(0,cnt_1): #past
        for j in range(-1,1): #x displacement
            if x_array_2[i] == (x_array_1[k] + j):
              for l in range(-1,1):
                  if y_array_2[i] == (y_array_1[k] + l):
                      for m in range(-1,1):
                          if r_array_2[i] == (r_array_1[i] + l):
                            pos_array_1[cnt_3] = k;
                            pos_array_2[cnt_3] = i;





for i in range(0,cnt_3):
    if x_array_1[pos_array_1[i]] == x_array_2[pos_array_2[i]]:
        print("Ring %d has not moved in the x direction") % (i)
    else:
        x_distance = x_array_1[pos_array_1[i]] - x_array_2[pos_array_2[i]]
        print(x_distance)



