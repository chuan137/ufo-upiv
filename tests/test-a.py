#!/home/chuan/.virtualenv/ufo/bin/python
from gi.repository import Ufo
import numpy as np
import tifffile
import threading
import time
from ufo.numpy import asarray, fromarray

pm = Ufo.PluginManager()
denoise = pm.get_task('denoise')
contrast = pm.get_task('contrast')
cutroi = pm.get_task('cut-roi')
write = pm.get_task('write')
null = pm.get_task('null')

img_fft = pm.get_task('fft')
ifft = pm.get_task('ifft')
fftmult = pm.get_task('fftmult')
ring_pattern = pm.get_task('ring_pattern')
ring_fft = pm.get_task('fft')
loop_ringfft = pm.get_task('buffer')
fft_convolve = pm.get_task('fftconvolution')

input_img_task = Ufo.InputTask()
input_ring_task = Ufo.InputTask()
output_task = Ufo.OutputTask()

# Settings
img_path = '/home/chuan/DATA/upiv/input0.tif'
cutroi.set_properties(x=0, y=100, width=1024, height=1024)
write.set_properties(filename='res_%02i.tif')
ring_pattern.set_properties(ring_start=10, ring_end=12, ring_step=2,
                            ring_thickness=4, width=1024, height=1024)
loop_ringfft.set_properties(loop=1, dup_count=1)

###
### code start here
###

img0 = tifffile.imread(img_path)
ring = tifffile.imread('./ring_00.tif')


# set up graph
g = Ufo.TaskGraph()
g.connect_nodes(input_img_task, cutroi)
g.connect_nodes(cutroi, denoise)
g.connect_nodes(denoise, contrast)
g.connect_nodes_full(contrast, fft_convolve, 0)
g.connect_nodes_full(input_ring_task, fft_convolve, 1)
g.connect_nodes(fft_convolve, write)

#g.connect_nodes(ring_pattern, output_task)

#g.connect_nodes(ring_fft, loop_ringfft)
#g.connect_nodes_full(img_fft, fftmult, 0)
#g.connect_nodes_full(ring_fft, fftmult, 1)
#g.connect_nodes(fftmult, ifft)

#g.connect_nodes(ifft, output_task)
#g.connect_nodes(ring_fft, output_task)

# run scheduler in seperate thread
def run_sched():
    global g
    sched = Ufo.FixedScheduler()
    sched.run(g)
sched_thread = threading.Thread(target=run_sched)
sched_thread.start()

time.sleep(.1)

# input task
def run_input_img_task():
    buf = fromarray(img0.astype(np.float32))
    input_img_task.release_input_buffer(buf)
    input_img_task.stop()
input_thread = threading.Thread(target=run_input_img_task)
input_thread.start()

def run_input_ring_task():
    buf = fromarray(img0.astype(np.float32))
    input_ring_task.release_input_buffer(buf)
    input_ring_task.stop()
input_ring_thread = threading.Thread(target=run_input_ring_task)
input_ring_thread.start()

# output task
res = []
def run_output_task():
    buf = output_task.get_output_buffer()
    res.append(asarray(buf).copy())
    output_task.release_output_buffer(buf)
output_thread = threading.Thread(target=run_output_task)
output_thread.start()
while len(res) == 0:
    time.sleep(0.1)

#tifffile.imsave('test1.tif', res[0])
print len(res)
#print res[0].shape

