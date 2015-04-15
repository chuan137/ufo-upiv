#!/home/chuan/.virtualenv/ufo/bin/python
from gi.repository import Ufo
import sys, getopt
import numpy as np
import tifffile

pm = Ufo.PluginManager()
cutroi = pm.get_task('cut-roi')
write = pm.get_task('write')
fft_convolve = pm.get_task('fftconvolution')
img_reader = pm.get_task('read')
ring_reader = pm.get_task('read')

# Settings
img_path = './denoise/input0-contrast.tif'
out_path = './convolve/res.tif'
ring_path = './ring_pattern/ring.tif'
#ring_path = '../tools/kernel.tif'
#ring_path = '../tools/fuzzy_kernel.tif'
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "hi:o:k:", ["ifile=", "ofile=", "kernel="])
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
    elif opt in ("-k", "--kernel"):
        ring_path = arg
print 'Input image is ', img_path
print 'Output path is ', out_path
print 'Kernel path is ', ring_path

img_reader.set_properties(path=img_path)
ring_reader.set_properties(path=ring_path)
cutroi.set_properties(x=0, y=0, width=1024, height=1024)
write.set_properties(filename='./convolve/res.tif')

###
### code start here
###

# set up graph
g = Ufo.TaskGraph()
g.connect_nodes(img_reader, cutroi)
g.connect_nodes_full(cutroi, fft_convolve, 0)
g.connect_nodes_full(ring_reader, fft_convolve, 1)
g.connect_nodes(fft_convolve, write)

# run scheduler 
sched = Ufo.Scheduler()
sched.run(g)

