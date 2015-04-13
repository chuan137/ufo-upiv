#!/home/chuan/.virtualenv/ufo/bin/python
from gi.repository import Ufo

scale            = 1
number_of_images = 1

ring_start     = 10 / scale
ring_end       = 40 / scale
ring_step      = 2  / scale
ring_count     = ( ring_end - ring_start )  / ring_step + 1
ring_thickness = 6 / scale

img_path = '/home/chuan/DATA/upiv/Image0.tif'; xshift = 0; yshfit = 200
img_path = '/home/chuan/DATA/upiv/60_Luft_frame50.tif'; xshift = 150; yshift = 0
res_path = 'res/ordfilt.tif'

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
ordfilt = pm.get_task('ordfilt')
ring_pattern = pm.get_task('ring_pattern')
ring_loop = pm.get_task('buffer')

null = pm.get_task('null')

read.set_properties(path=img_path, number=number_of_images)
cutroi.set_properties(x=xshift, y=yshift, width=1024, height=1024)
write.set_properties(filename=res_path)
denoise.set_properties(matrix_size=26/scale)
contrast.set_properties(remove_high=0)
duplicater.set_properties(dup_count=ring_count)
ring_pattern.set_properties(ring_start=ring_start, ring_end=ring_end, 
                            ring_step=ring_step, ring_thickness=ring_thickness,
                            width=1024/scale, height=1024/scale)
#ring_loop.set_properties(loop=1, dup_count=ring_count)
ring_loop.set_properties(loop=1)

g = Ufo.TaskGraph()

# read image and pre-processing
g.connect_nodes(read, cutroi)
if scale == 2:
    g.connect_nodes(cutroi, reduce)
    g.connect_nodes(reduce, denoise)
else:
    g.connect_nodes(cutroi, denoise)
g.connect_nodes(denoise, contrast)

# Ordered Search Filter
g.connect_nodes(ring_pattern, ring_loop)
g.connect_nodes_full(contrast, ordfilt, 0)
g.connect_nodes_full(ring_loop, ordfilt, 1)
g.connect_nodes(ordfilt, write)

sched = Ufo.Scheduler()
sched.set_properties(enable_tracing=True)
sched.run(g)
