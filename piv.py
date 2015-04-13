from gi.repository import Ufo

ring_start     = 10
ring_end       = 20
ring_step      = 1
ring_count     = ( ring_end - ring_start )  / ring_step + 1
ring_thickness = 6
scale          = 2
number_of_images = 1

pm = Ufo.PluginManager()

read = pm.get_task('read')
read.set_properties(path='/home/chuan/DATA/upiv/Image0.tif', number=number_of_images)

write = pm.get_task('write')
write.set_properties(filename='res/foo-%05i.tif')

denoise = pm.get_task('denoise')
denoise.set_properties(matrix_size=26)

contrast = pm.get_task('contrast')
contrast.set_properties(remove_high=0)

ring_pattern = pm.get_task('ring_pattern')
ring_pattern.set_properties(ring_start=ring_start, 
                            ring_end=ring_end, 
                            ring_step=ring_step, 
                            ring_thickness=ring_thickness,
                            width=1080, height=1280)

filter_particle = pm.get_task('filter_particle')
filter_particle.set_properties(min=0.0125, threshold=0.8)

concatenate_result = pm.get_task('concatenate_result')
concatenate_result.set_properties(max_count=100, ring_count=ring_count)

duplicater = pm.get_task('buffer')
duplicater.set_properties(dup_count=ring_count)

multi_search = pm.get_task('multi_search')
multi_search.set_properties(radii_range=6, threshold=0.01, displacement=1)

remove_circle = pm.get_task('remove_circle')
remove_circle.set_properties(threshold=4)

get_dup_circ = pm.get_task('get_dup_circ')
get_dup_circ.set_properties(threshold=8)

loop_ringfft = pm.get_task('buffer')
loop_ringfft.set_properties(loop=1, dup_count=number_of_images)

fft = pm.get_task('fft')
ringfft = pm.get_task('fft')
ringifft = pm.get_task('ifft')
fftmult = pm.get_task('fftmult')
replicater = pm.get_task('buffer')
ringwriter = pm.get_task('ringwriter')

broadcast_contrast = Ufo.CopyTask()
null = pm.get_task('null')
null1 = pm.get_task('null')

g = Ufo.TaskGraph()
g.connect_nodes(read, denoise)
g.connect_nodes(denoise, contrast)
g.connect_nodes(contrast, broadcast_contrast)

g.connect_nodes(broadcast_contrast, fft)
g.connect_nodes(fft, duplicater)
g.connect_nodes(duplicater, write)

#g.connect_nodes(ring_pattern, ringfft)
#g.connect_nodes(ringfft, loop_ringfft)
#g.connect_nodes_full(duplicater, fftmult, 0)
#g.connect_nodes_full(loop_ringfft, fftmult, 1)

#g.connect_nodes(fftmult, ringifft)
#g.connect_nodes(ringifft, filter_particle)
#g.connect_nodes(filter_particle, concatenate_result)
#g.connect_nodes(filter_particle, concatenate_result)
#g.connect_nodes(concatenate_result, null)

#g.connect_nodes(broadcast_contrast, replicater)
#g.connect_nodes(replicater, null1)

#g.connect_nodes_full(replicater, multi_search, 0)
#g.connect_nodes_full(concatenate_result, multi_search, 1)
#g.connect_nodes(multi_search, null)
#g.connect_nodes(multi_search, remove_circle)
#g.connect_nodes(remove_circle, get_dup_circ)
#g.connect_nodes(get_dup_circ, ringwriter)

sched = Ufo.Scheduler()
sched.run(g)
