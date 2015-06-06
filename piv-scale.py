#!/usr/bin/env python
from gi.repository import Ufo
from ufo_extension import TaskGraph, PluginManager

scale          = 2
num_images     = 1
start          = 0
out_file       = 'res/HT.tif'
xshift         = 0
yshift         = 0

ring_start     = 6 / scale
ring_end       = 30 / scale
ring_step      = 2  / scale
ring_thickness = 6 / scale

CASE = 2

if CASE == 1:
    img_path = 'input/sampleC-0050.tif'; xshift = 150; yshfit = 0
    img_path = 'input/sampleC-0050-contrast.tif'; xshift = 0; yshfit = 0
    ring_start = 16 / scale
    ring_end = 26 / scale
if CASE == 2:
    img_path = 'input/sampleB-0001-cut.tif'
    img_path = 'input/sampleB-0001-contrast.tif'
    out_file = 'res/HT2.tif'
if CASE == 3:
    img_path = 'input/input-stack.tif'
    xshift = 150; yshift = 0
if CASE == 4:
    img_path = '/home/chuan/DATA/upiv/sampleC-files/'
    num_images = 5
    start = 50
    xshift = 150
    yshift = 0
if CASE == 5:
    img_path = '/home/chuan/DATA/upiv/Image0.tif'; xshift = 0; yshfit = 200
    img_path = '/home/chuan/DATA/upiv/60_Luft_frame50.tif'; xshift = 150; yshift = 0

ring_count     = ( ring_end - ring_start )  / ring_step + 1

# Configure Ufo Filters
pm      = PluginManager()

read    = pm.get_task('read', path=img_path, number=num_images, start=start)
write   = pm.get_task('write', filename=out_file)
null    = pm.get_task('null')
monitor = pm.get_task('monitor')

cutroi  = pm.get_task('cut-roi', x=xshift, y=yshift, width=1024, height=1024)
rescale = pm.get_task('rescale', factor=1./scale)
denoise = pm.get_task('denoise', matrix_size=int(14/scale))
contrast = pm.get_task('contrast', remove_high=0)

gen_ring_patterns   = pm.get_task('ring_pattern', 
                        ring_start=ring_start, ring_end=ring_start, 
                        ring_step=ring_step, ring_thickness=ring_thickness,
                        width=1024/scale, height=1024/scale)
ring_pattern_loop   = pm.get_task('buffer', dup_count=num_images, loop=True)

hessian_kernel      = pm.get_task('hessian_kernel', sigma=2./scale, width=1024/scale, height=1024/scale)
hessian_kernel_loop = pm.get_task('buffer', dup_count=num_images, loop=True)

hough_convolve      = pm.get_task('fftconvolution')
hessian_convolve    = pm.get_task('fftconvolution')
hessian_analysis    = pm.get_task('hessian_analysis')
hessian_stack       = pm.get_task('stack', number=ring_count)

blob_test = pm.get_task('blob_test', max_detection=100, 
                        ring_start=ring_start, ring_step=ring_step, 
                        ring_end=ring_end)

ring_writer = pm.get_task('ring_writer')

broadcast_contrast = Ufo.CopyTask()
broadcast_hough_convolve = Ufo.CopyTask()

# connect ufo task graph
g = TaskGraph()

if True:
    branch1 = [read, cutroi, rescale, contrast, broadcast_contrast]
    branch2 = [gen_ring_patterns, ring_pattern_loop]
    branch3 = [hessian_kernel, hessian_kernel_loop]
    branch4 = [hessian_convolve, hessian_analysis, monitor, write]
    #branch1 = [read, cutroi, rescale, denoise, contrast, broadcast_contrast]
    #branch4 = [hessian_convolve, hessian_analysis, hessian_stack, blob_test, monitor, null]
    #branch4 = [hessian_convolve, hessian_analysis, hessian_stack, blob_test, ring_writer]
    #branch4 = [hessian_convolve, hessian_analysis, hessian_stack, blob_test, monitor,ring_writer]
    
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

