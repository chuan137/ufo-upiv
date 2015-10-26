#!/usr/bin/env python
from gi.repository import Ufo

scale            = 2
number_of_images = 1

ring_start     = 10 / scale
ring_end       = 20 / scale
ring_step      = 2  / scale
ring_count     = ( ring_end - ring_start )  / ring_step + 1
ring_thickness = 4 / scale

#img_path = '/home/chuan/DATA/upiv/Image0.tif'; xshift = 0; yshfit = 200
#img_path = '/home/chuan/DATA/upiv/60_Luft_frame50.tif'; xshift = 150; yshift = 0
#img_path = 'data/image1.tif'; xshift=0; yshift=0
img_path = 'data/SampleC'; xshift=0; yshift=0
res_tif = './ordfilt.tif'
res_txt = './res.txt'

pm = Ufo.PluginManager()

read = pm.get_task('read')
reduce = pm.get_task('reduce')
write = pm.get_task('write')
duplicater = pm.get_task('buffer')
crop = pm.get_task('crop')
denoise = pm.get_task('denoise')
denoise_post_HT = pm.get_task('denoise')
contrast = pm.get_task('contrast')
contrast_post_HT = pm.get_task('contrast')
ordfilt = pm.get_task('ordfilt')
ring_pattern = pm.get_task('ring_pattern')
ring_loop = pm.get_task('buffer')
likelihood = pm.get_task('hough-likelihood')
ring_writer = pm.get_task('ring_writer')

null = pm.get_task('null')
mon = pm.get_task('monitor')
stack = pm.get_task('stack')

read.set_properties(path=img_path, number=number_of_images)
crop.set_properties(x=xshift, y=yshift, width=1024, height=1024)
write.set_properties(filename=res_tif)
denoise.set_properties(matrix_size=26/scale)
contrast.set_properties(remove_high=0)
duplicater.set_properties(dup_count=ring_count)
ring_pattern.set_properties(method=1, start=ring_start, end=ring_end, 
                            step=ring_step, thickness=ring_thickness,
                            width=1024/scale, height=1024/scale)
likelihood.set_properties(masksize=13, maskinnersize=7, threshold=100)
ring_writer.set_properties(filename=res_txt)
#ring_loop.set_properties(loop=1, dup_count=ring_count)
ring_loop.set_properties(loop=1)
stack.set_properties(number=ring_count)

g = Ufo.TaskGraph()

# read image and pre-processing
g.connect_nodes(read, crop)
if scale == 2:
    g.connect_nodes(crop, reduce)
    g.connect_nodes(reduce, denoise)
else:
    g.connect_nodes(crop, denoise)
g.connect_nodes(denoise, contrast)

# Ordered Search Filter
g.connect_nodes(ring_pattern, ring_loop)
g.connect_nodes_full(contrast, ordfilt, 0)
g.connect_nodes_full(ring_loop, ordfilt, 1)
g.connect_nodes(ordfilt, write)
# g.connect_nodes(ordfilt,stack)
# g.connect_nodes(stack,likelihood)
# g.connect_nodes(likelihood, ring_writer)

sched = Ufo.Scheduler()
sched.set_properties(enable_tracing=False)
sched.run(g)
