#!/usr/bin/env python
from gi.repository import Ufo

POSTDENOISE = False
DENOISE = False

scale            = 2
number_of_images = 100

ring_start     = 10 / scale
ring_end       = 30 / scale
ring_step      = 2  / scale
ring_count     = ( ring_end - ring_start )  / ring_step + 1
ring_thickness = 6 / scale

img_path = '/home/chuan/DATA/upiv/Image0.tif'; xshift = 0; yshfit = 200
img_path = '/home/chuan/DATA/upiv/60_Luft_frame50.tif'; xshift = 150; yshift = 0
img_path = 'input/input-stack.tif'; xshift = 150; yshift = 0
res_path = 'res/HT.tif'

pm = Ufo.PluginManager()

read = pm.get_task('read')
reduce = pm.get_task('reduce')
write = pm.get_task('write')
duplicater = pm.get_task('buffer')
cutroi = pm.get_task('cut-roi')
denoise = pm.get_task('denoise')
denoise_post_HT = pm.get_task('denoise')
contrast = pm.get_task('contrast')
contrast_post_HT = pm.get_task('contrast')
ring_pattern = pm.get_task('ring_pattern')
hough_convolve = pm.get_task('fftconvolution')
hessian_convolve = pm.get_task('fftconvolution')
hessian_kernel = pm.get_task('hessian_kernel')
hessian_kernel_loop = pm.get_task('buffer')
hessian_analysis = pm.get_task('hessian_analysis')
brighten = pm.get_task('calculate')
filter_particle = pm.get_task('filter_particle')
concatenate_result = pm.get_task('concatenate_result')
ring_pattern_loop = pm.get_task('buffer')

multi_search = pm.get_task('multi_search')
remove_circle = pm.get_task('remove_circle')
get_dup_circ = pm.get_task('get_dup_circ')
replicater = pm.get_task('buffer')
ringwriter = pm.get_task('ringwriter')

broadcast_contrast = Ufo.CopyTask()
null = pm.get_task('null')

read.set_properties(path=img_path, number=number_of_images)
cutroi.set_properties(x=xshift, y=yshift, width=1024, height=1024)
write.set_properties(filename=res_path)
denoise.set_properties(matrix_size=14/scale)
denoise_post_HT.set_properties(matrix_size=3/scale)
contrast.set_properties(remove_high=0)
contrast_post_HT.set_properties(remove_high=0)
duplicater.set_properties(dup_count=ring_count)
ring_pattern.set_properties(ring_start=ring_start, ring_end=ring_end, 
                            ring_step=ring_step, ring_thickness=ring_thickness,
                            width=1024/scale, height=1024/scale)
ring_pattern_loop.set_properties(dup_count=number_of_images, loop=1)
hessian_kernel.set_properties(sigma=2./scale, width=1024/scale, height=1024/scale)
hessian_kernel_loop.set_properties(dup_count=number_of_images, loop=1)
brighten.set_properties(expression="(exp(v*10000000)-1)")
filter_particle.set_properties(min=0.0001, threshold=0.8)
concatenate_result.set_properties(max_count=100, ring_count=ring_count)


g = Ufo.TaskGraph()

# read image and pre-processing
g.connect_nodes(read, cutroi)

if DENOISE:
    if scale == 2:
        g.connect_nodes(cutroi, reduce)
        g.connect_nodes(reduce, denoise)
        g.connect_nodes(denoise, contrast)
    else:
        g.connect_nodes(cutroi, denoise)
        g.connect_nodes(denoise, contrast)
else:
    if scale == 2:
        g.connect_nodes(cutroi, reduce)
        g.connect_nodes(reduce, contrast)
    else:
        g.connect_nodes(cutroi, contrast)
g.connect_nodes(contrast, broadcast_contrast)

# Hough transform
g.connect_nodes(ring_pattern, ring_pattern_loop)
g.connect_nodes_full(broadcast_contrast, hough_convolve, 0)
g.connect_nodes_full(ring_pattern_loop, hough_convolve, 1)

# Blob detection
if POSTDENOISE:
    g.connect_nodes(hough_convolve, denoise_post_HT)
    g.connect_nodes_full(denoise_post_HT, hessian_convolve, 0)
else:
    g.connect_nodes_full(hough_convolve, hessian_convolve, 0)
g.connect_nodes(hessian_kernel, hessian_kernel_loop)
g.connect_nodes_full(hessian_kernel_loop, hessian_convolve, 1)
g.connect_nodes(hessian_convolve, hessian_analysis)
g.connect_nodes(hessian_analysis, write)

# Blob detection again
# Post-processing
#g.connect_nodes(fft_convolve, filter_particle)
#g.connect_nodes(filter_particle, concatenate_result)
#g.connect_nodes(concatenate_result, ringwriter)
#g.connect_nodes(concatenate_result, write)

# Post-processing
#g.connect_nodes(broadcast_contrast, replicater)
#g.connect_nodes(replicater, null1)

#g.connect_nodes_full(replicater, multi_search, 0)
#g.connect_nodes_full(concatenate_result, multi_search, 1)
#g.connect_nodes(multi_search, null)
#g.connect_nodes(multi_search, remove_circle)
#g.connect_nodes(remove_circle, get_dup_circ)
#g.connect_nodes(get_dup_circ, ringwriter)

sched = Ufo.Scheduler()
#sched.set_properties(enable_tracing=True)
sched.run(g)

