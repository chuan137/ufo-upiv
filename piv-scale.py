#!/usr/bin/env python
from gi.repository import Ufo

class TaskGraph(Ufo.TaskGraph):
    def connect_branch(self, node_list):
        for i in range(len(node_list)-1):
            n0 = node_list[i]
            n1 = node_list[i+1]
            self.connect_nodes(n0, n1)
    def merge_branch(self, nlist1, nlist2, node):
        if isinstance(nlist1, list):
            n1 = nlist1[-1]
        else:
            n1 = nlist1
        if isinstance(nlist2, list):
            n2 = nlist2[-1]
        else:
            n2 = nlist2
        self.connect_nodes_full(n1, node, 0)
        self.connect_nodes_full(n2, node, 1)

POSTDENOISE = False
DENOISE = False

scale            = 2
number_of_images = 120

ring_start     = 10 / scale
ring_end       = 30 / scale
ring_step      = 2  / scale
ring_count     = ( ring_end - ring_start )  / ring_step + 1
ring_thickness = 6 / scale

img_path = '/home/chuan/DATA/upiv/Image0.tif'; xshift = 0; yshfit = 200
img_path = '/home/chuan/DATA/upiv/60_Luft_frame50.tif'; xshift = 150; yshift = 0
img_path = 'input/input-stack.tif'; xshift = 150; yshift = 0
img_path = 'input/sampleC-files/'; xshift = 150; yshift = 0
out_file = 'res/HT.tif'

# Configure Ufo Filters
pm = Ufo.PluginManager()

read = pm.get_task('read')
read.props.path = img_path
read.props.number = number_of_images

write = pm.get_task('write')
write.props.filename = out_file

cutroi = pm.get_task('cut-roi')
cutroi.props.x = xshift
cutroi.props.y = yshift
cutroi.props.width = 1024
cutroi.props.height = 1024

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

hough_convolve = pm.get_task('fftconvolution')

hessian_kernel = pm.get_task('hessian_kernel')
hessian_kernel.props.sigma = 2. / scale
hessian_kernel.props.width = 1024 / scale
hessian_kernel.props.height = 1024 / scale

hessian_kernel_loop = pm.get_task('buffer')
hessian_kernel_loop.props.dup_count = number_of_images
hessian_kernel_loop.props.loop = 1 

hessian_convolve = pm.get_task('fftconvolution')
hessian_analysis = pm.get_task('hessian_analysis')

duplicater = pm.get_task('buffer')
duplicater.props.dup_count = ring_count

reduce_scale = pm.get_task('reduce')
null = pm.get_task('null')

broadcast_contrast = Ufo.CopyTask()

# connect ufo task graph
g = TaskGraph()

## # read image and pre-processing
## g.connect_nodes(read, cutroi)

## if DENOISE:
##     if scale == 2:
##         g.connect_nodes(cutroi, reduce_scale)
##         g.connect_nodes(reduce_scale, denoise)
##         g.connect_nodes(denoise, contrast)
##     else:
##         g.connect_nodes(cutroi, denoise)
##         g.connect_nodes(denoise, contrast)
## else:
##     if scale == 2:
##         g.connect_nodes(cutroi, reduce_scale)
##         g.connect_nodes(reduce_scale, contrast)
##     else:
##         g.connect_nodes(cutroi, contrast)
## g.connect_nodes(contrast, broadcast_contrast)
## # Hough transform
## g.connect_nodes(gen_ring_patterns, ring_pattern_loop)
## g.connect_nodes_full(broadcast_contrast, hough_convolve, 0)
## g.connect_nodes_full(ring_pattern_loop, hough_convolve, 1)
##
## # Blob detection
## if POSTDENOISE:
##     g.connect_nodes(hough_convolve, denoise_post_HT)
##     g.connect_nodes_full(denoise_post_HT, hessian_convolve, 0)
## else:
##     g.connect_nodes_full(hough_convolve, hessian_convolve, 0)
## g.connect_nodes(hessian_kernel, hessian_kernel_loop)
## g.connect_nodes_full(hessian_kernel_loop, hessian_convolve, 1)
## g.connect_nodes(hessian_convolve, hessian_analysis)
## g.connect_nodes(hessian_analysis, write)


if False:
    branch1 = [read, cutroi, reduce_scale, contrast, broadcast_contrast]
    #branch1 = [read, cutroi, reduce_scale, denoise, contrast, broadcast_contrast]
    branch2 = [gen_ring_patterns, ring_pattern_loop]
    
    g.connect_branch(branch1)
    g.connect_branch(branch2)
    g.merge_branch(branch1, branch2, hough_convolve)
    
    g.connect_branch([hessian_kernel, hessian_kernel_loop])
    g.merge_branch(hough_convolve, hessian_kernel_loop, hessian_convolve)
    
    branch4 = [hessian_convolve, hessian_analysis, write]
    g.connect_branch(branch4)
else:
    blur0 = pm.get_task('blur')
    blur1 = pm.get_task('blur')
    blur2 = pm.get_task('blur')
    null = pm.get_task('null')
    branch = [read, blur0, blur1, blur2, write]
    g.connect_branch(branch)


# Run Ufo
sched = Ufo.Scheduler()
sched.props.enable_tracing = True
sched.run(g)

