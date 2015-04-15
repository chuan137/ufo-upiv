#!/home/chuan/.virtualenv/ufo/bin/python
from gi.repository import Ufo
import sys, getopt
import numpy as np
import tifffile

pm = Ufo.PluginManager()
write = pm.get_task('write')
hessian_kernel = pm.get_task('hessian-kernel')
hessian_analysis = pm.get_task('hessian_analysis')
hessian_kernel_loop = pm.get_task('buffer')
img_reader = pm.get_task('read')
ker_reader = pm.get_task('read')
fftconvolve = pm.get_task('fftconvolution')

# Settings
img_path = 'blob/input.tif'
out_path = 'blob/res.tif'
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

img_reader.set_properties(path=img_path, step=1)
write.set_properties(filename=out_path)
hessian_kernel.set_properties(sigma=2, width=1024, height=1024)
hessian_kernel_loop.set_properties(loop=1)

###
### code start here
###

# set up graph
g = Ufo.TaskGraph()

g.connect_nodes(hessian_kernel, hessian_kernel_loop)

g.connect_nodes_full(img_reader, fftconvolve, 0)
g.connect_nodes_full(hessian_kernel_loop, fftconvolve, 1)

g.connect_nodes(fftconvolve, hessian_analysis)
g.connect_nodes(hessian_analysis, write)

# run scheduler 
sched = Ufo.Scheduler()
sched.run(g)
