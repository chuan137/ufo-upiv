#!/home/chuan/.virtualenv/ufo/bin/python
import sys, getopt
from gi.repository import Ufo
import numpy as np
import tifffile

pm = Ufo.PluginManager()
cutroi = pm.get_task('cut-roi')
write = pm.get_task('write')
img_reader = pm.get_task('read')
denoise = pm.get_task('denoise')
contrast = pm.get_task('contrast')

# Settings
img_path = 'input0.tif'
out_path = 'denoise/res.tif'
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
except getopt.GetoptError:
    print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit()
    elif opt in ("-i", "--ifile"):
        img_path = arg
    elif opt in ("-o", "--ofile"):
        out_path = arg
print 'Input image is ', img_path
print 'Output path is ', out_path

img_reader.set_properties(path=img_path)
write.set_properties(filename=out_path)
denoise.set_properties(matrix_size=13)
contrast.set_properties(remove_high=True)

###
### code start here
###

# set up graph
g = Ufo.TaskGraph()
g.connect_nodes(img_reader, denoise)
g.connect_nodes(denoise, contrast)
g.connect_nodes(contrast, write)

g1 = Ufo.TaskGraph()
g1.connect_nodes(img_reader, contrast)
g1.connect_nodes(contrast, write)

g2 = Ufo.TaskGraph()
g2.connect_nodes(img_reader, denoise)
g2.connect_nodes(denoise, write)

# run scheduler 
sched = Ufo.Scheduler()
sched.run(g)

