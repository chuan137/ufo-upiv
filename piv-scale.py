#!/usr/bin/env python
from gi.repository import Ufo
from ufo_extension import TaskGraph, PluginManager

num_images     = 1
file_start     = 0
xshift, yshift = 0, 0

ring_start     = 10 
ring_end       = 30 
ring_step      = 2 
ring_thickness = 6 

scale          = 2

blob_alpha     = 1.0

CASE = 3

if CASE == 1:
    img_path = 'input/sampleC-0050-contrast.tif'; xshift = 0; yshfit = 0
    img_path = 'input/sampleC-0050.tif'; xshift = 150; yshfit = 0
    ring_start = 10 
    ring_end = 30 
    blob_alpha = 1.0
if CASE == 2:
    img_path = 'input/sampleB-0001-contrast.tif'
    ring_start = 10 
    ring_end = 60
    blob_alpha = 0.8
if CASE == 3:
    img_path = 'input/input-stack.tif'
    num_images = 4 
    xshift = 150; yshift = 0
    ring_start = 10 
    ring_end = 30 
    blob_alpha = 1.0
if CASE == 4:
    img_path = '/home/chuan/DATA/upiv/sampleC-files/'
    img_path = 'input/sampleC-files/'
    num_images = 5
    start = 50
    xshift = 150
    yshift = 0
if CASE == 5:
    img_path = '/home/chuan/DATA/upiv/Image0.tif'; xshift = 0; yshfit = 200
    img_path = '/home/chuan/DATA/upiv/60_Luft_frame50.tif'; xshift = 150; yshift = 0

ring_start = ring_start / scale
ring_step = ring_step / scale
ring_end = ring_end / scale
ring_thickness = ring_thickness / scale
ring_count = ( ring_end - ring_start )  / ring_step + 1
out_file = 'res/res%d.tif' % CASE

# Configure Ufo Filters
pm      = PluginManager()

read    = pm.get_task('read', path=img_path, number=num_images, start=file_start)
write   = pm.get_task('write', filename=out_file)
null    = pm.get_task('null')
monitor = pm.get_task('monitor')

crop    = pm.get_task('crop', x=xshift, y=yshift, width=1024, height=1024)
rescale = pm.get_task('rescale', factor=1./scale)
denoise = pm.get_task('denoise', matrix_size=int(14/scale))
contrast = pm.get_task('contrast', remove_high=0)

gen_ring_patterns   = pm.get_task('ring_pattern', 
                        ring_start=ring_start, ring_end=ring_end, 
                        ring_step=ring_step, ring_thickness=ring_thickness,
                        width=1024/scale, height=1024/scale)
ring_pattern_loop   = pm.get_task('buffer', dup_count=num_images, loop=1)

hessian_kernel      = pm.get_task('hessian_kernel', sigma=2./scale, 
                                  width=1024/scale, height=1024/scale)
hessian_kernel_loop = pm.get_task('buffer', dup_count=num_images, loop=1)

hough_convolve      = pm.get_task('fftconvolution')
hessian_convolve    = pm.get_task('fftconvolution')
hessian_analysis    = pm.get_task('hessian_analysis')
hessian_stack       = pm.get_task('stack', number=ring_count)

local_maxima = pm.get_task('local-maxima', sigma=3)
label_cluster = pm.get_task('label-cluster')
combine_test = pm.get_task('combine-test')
blob_test = pm.get_task('blob_test', alpha=blob_alpha)
null = pm.get_task('null')
stack1 = pm.get_task('stack', number=ring_count)
stack2 = pm.get_task('stack', number=ring_count)
unstack1 = pm.get_task('unstack')
unstack2 = pm.get_task('unstack')
monitor = pm.get_task('monitor')
monitor1 = pm.get_task('monitor')

ring_writer = pm.get_task('ring_writer')

bc_contrast = Ufo.CopyTask()
bc_hessian = Ufo.CopyTask()

# connect ufo task graph
g = TaskGraph()
graph = 2

if graph == 1:
    write.props.filename = 'res/HT%d.tif' % CASE
    branch1 = [read, crop, rescale, contrast, bc_contrast]
    branch2 = [gen_ring_patterns, ring_pattern_loop]
    branch3 = [hessian_kernel, hessian_kernel_loop]
    branch4 = [hessian_convolve, hessian_analysis, write]
    
    g.merge_branch(branch1, branch2, hough_convolve)
    g.merge_branch(hough_convolve, branch3, branch4)

if graph == 2:
    branch1 = [read, crop, rescale, contrast, bc_contrast]
    branch2 = [gen_ring_patterns, ring_pattern_loop]
    branch3 = [hessian_kernel, hessian_kernel_loop]
    #branch4 = [hessian_convolve, hessian_analysis, monitor, stack1, monitor1, null]
    branch4 = [hessian_convolve, hessian_analysis, bc_hessian, stack1, unstack1]
    branch5 = [bc_hessian, local_maxima, label_cluster, stack2, combine_test, unstack2]
    branch6 = [blob_test, write]

    g.merge_branch(branch1, branch2, hough_convolve)
    g.merge_branch(hough_convolve, branch3, branch4)
    g.merge_branch(branch4, branch5, branch6)

# Run Ufo
sched = Ufo.FixedScheduler()
sched.props.enable_tracing = False #True

def timer_function():
    sched.run(g)

from timeit import Timer
tm = Timer('timer_function()', 'from __main__ import timer_function')
t = tm.timeit(1)
print t, 'sec'

