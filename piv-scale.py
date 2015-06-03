#!/usr/bin/env python
from gi.repository import Ufo

class TaskGraph(Ufo.TaskGraph):
    def connect_branch(self, node_list):
        for i in range(len(node_list)-1):
            n0 = node_list[i]
            n1 = node_list[i+1]
            self.connect_nodes(n0, n1)
    def merge_branch(self, nlist1, nlist2, nodes):
        if isinstance(nlist1, list):
            n1 = nlist1[-1]
        else:
            n1 = nlist1
        if isinstance(nlist2, list):
            n2 = nlist2[-1]
        else:
            n2 = nlist2
        if isinstance(nodes, list):
            self.connect_nodes_full(n1, nodes[0], 0)
            self.connect_nodes_full(n2, nodes[0], 1)
            self.connect_branch(nodes)
        else:
            self.connect_nodes_full(n1, nodes, 0)
            self.connect_nodes_full(n2, nodes, 1)

scale            = 2
number_of_images = 1
start            = 1
out_file         = 'res/HT.tif'
xshift           = 0
yshift           = 0

ring_start     = 8 / scale
ring_end       = 60 / scale
ring_step      = 2  / scale
ring_count     = ( ring_end - ring_start )  / ring_step + 1
ring_thickness = 6 / scale

CASE = 4

if CASE == 1:
    img_path = 'input/sampleC-0050.tif'; xshift = 150; yshfit = 0
    img_path = 'input/sampleC-0050-contrast.tif'; xshift = 0; yshfit = 0
    out_file = 'res/HT.tif'
if CASE == 2:
    img_path = 'input/sampleB-0001-cut.tif'; xshift = 0; yshift = 0
    img_path = 'input/sampleB-0001-contrast.tif'; xshift = 0; yshift = 0
    out_file = 'res/HT2.tif'
if CASE == 3:
    img_path = 'input/input-stack.tif'
    xshift = 150; yshift = 0
if CASE == 4:
    img_path = '/home/chuan/DATA/upiv/sampleC-files/'
    number_of_images = 10
    start = 50
    xshift = 150
    yshift = 0
if CASE == 5:
    img_path = '/home/chuan/DATA/upiv/Image0.tif'; xshift = 0; yshfit = 200
    img_path = '/home/chuan/DATA/upiv/60_Luft_frame50.tif'; xshift = 150; yshift = 0

# Configure Ufo Filters
pm = Ufo.PluginManager()

read = pm.get_task('read')
read.props.path = img_path
read.props.number = number_of_images
read.props.start = start

write = pm.get_task('write')
write.props.filename = out_file

cutroi = pm.get_task('cut-roi')
cutroi.props.x = xshift
cutroi.props.y = yshift
cutroi.props.width = 1024
cutroi.props.height = 1024

rescale = pm.get_task('rescale')
rescale.props.factor = 1.0/scale

denoise = pm.get_task('denoise')
denoise.props.matrix_size = int(14/scale)

contrast = pm.get_task('contrast')
contrast.props.remove_high = 0

gen_ring_patterns = pm.get_task('ring_pattern')
gen_ring_patterns.props.ring_start = ring_start
gen_ring_patterns.props.ring_end   = ring_end
gen_ring_patterns.props.ring_step  = ring_step
gen_ring_patterns.props.ring_thickness = ring_thickness
gen_ring_patterns.props.width  = 1024 / scale
gen_ring_patterns.props.height = 1024 / scale

ring_pattern_loop = pm.get_task('buffer')
ring_pattern_loop.props.dup_count = number_of_images 
ring_pattern_loop.props.loop = 1 

hessian_kernel = pm.get_task('hessian_kernel')
hessian_kernel.props.sigma = 2. / scale
hessian_kernel.props.width = 1024 / scale
hessian_kernel.props.height = 1024 / scale

hessian_kernel_loop = pm.get_task('buffer')
hessian_kernel_loop.props.dup_count = number_of_images
hessian_kernel_loop.props.loop = 1 

hough_convolve = pm.get_task('fftconvolution')
hessian_convolve = pm.get_task('fftconvolution')
hessian_analysis = pm.get_task('hessian_analysis')

hessian_stack = pm.get_task('stack')
hessian_stack.props.number = ring_count

blob_test = pm.get_task('blob_test')
blob_test.props.max_detection = 100
blob_test.props.ring_start = ring_start
blob_test.props.ring_step = ring_step
blob_test.props.ring_end = ring_end

ring_writer = pm.get_task('ring_writer')

broadcast_contrast = Ufo.CopyTask()
broadcast_hough_convolve = Ufo.CopyTask()

null = pm.get_task('null')
monitor = pm.get_task('monitor')

# connect ufo task graph
g = TaskGraph()

if True:
    branch1 = [read, cutroi, rescale, contrast, broadcast_contrast]
    #branch1 = [read, cutroi, rescale, denoise, contrast, broadcast_contrast]
    branch2 = [gen_ring_patterns, ring_pattern_loop]
    branch3 = [hessian_kernel, hessian_kernel_loop]
    #branch4 = [hessian_convolve, hessian_analysis, hessian_stack, blob_test, ring_writer]
    branch4 = [hessian_convolve, hessian_analysis, hessian_stack, blob_test, monitor,ring_writer]
    
    g.connect_branch(branch1)
    g.connect_branch(branch2)
    g.connect_branch(branch3)
    g.connect_branch(branch4)

    g.merge_branch(branch1, branch2, hough_convolve)
    g.merge_branch(hough_convolve, branch3, branch4)
else:
    branch1 = [read, cutroi, rescale, contrast, broadcast_contrast]
    branch2 = [gen_ring_patterns, ring_pattern_loop]
    branch3 = [hough_convolve, write]

    g.connect_branch(branch1)
    g.connect_branch(branch2)
    g.connect_branch(branch3)

    g.merge_branch(branch1, branch2, branch3)


# Run Ufo
sched = Ufo.Scheduler()
sched.props.enable_tracing = False #True

def timer_function():
    sched.run(g)

from timeit import Timer
tm = Timer('timer_function()', 'from __main__ import timer_function')
t = tm.timeit(1)
print t, 'sec'

