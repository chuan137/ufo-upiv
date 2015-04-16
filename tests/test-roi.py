#!/usr/bin/env python
import sys, getopt
from gi.repository import Ufo
import numpy as np
import tifffile

pm = Ufo.PluginManager()
img_reader = pm.get_task('read')
cutroi = pm.get_task('cut-roi')
write = pm.get_task('write')

# Settings
img_path = 'inputs/input1.tif'
out_path = 'res.tif'
argv = sys.argv[1:]
xpos = 0
ypos = 0
width = 1024
height = 1024
try:
    opts, args = getopt.getopt(argv, "i:o:x:y:w:h:", ["ifile=", "ofile="])
except getopt.GetoptError:
    print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-i", "--ifile"):
        img_path = arg
    elif opt in ("-o", "--ofile"):
        out_path = arg
    elif opt in ("-x"):
        xpos = int(arg)
    elif opt in ("-y"):
        ypos = int(arg)
    elif opt in ("-h"):
        height = int(arg)
    elif opt in ("-w"):
        width = int(arg)
print 'Input image is ', img_path
print 'Output path is ', out_path

img_reader.set_properties(path=img_path)
write.set_properties(filename=out_path)
cutroi.set_properties(x=xpos, y=ypos, width=1024, height=1024)

###
### code start here
###

# set up graph
g = Ufo.TaskGraph()
g.connect_nodes(img_reader, cutroi)
g.connect_nodes(cutroi, write)

# run scheduler 
sched = Ufo.Scheduler()
sched.run(g)

