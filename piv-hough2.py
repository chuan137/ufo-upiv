#!/usr/bin/env python
from gi.repository import Ufo
from piv.pivjob import PivJob
from piv.ddict import DotDict


class PivJob(PivJob):
    def add_tasks(self):
        p = self.parms
        self.add_task('fft1', 'fft', dimensions=2)
        self.add_task('ifft', dimensions=2)
        self.add_task('stack', number=p.number)
        self.add_task('s1', 'slice')

        self.add_task('ring_fft', 'fft', dimensions=2)
        self.add_task('ring_stack', 'stack', number=p.ring_number)
        self.add_task('ring_loop', 'loop', count=p.number)
        self.add_task('ring_convolution', 'complex_mult')

        self.add_task('hessian_fft', 'fft', dimensions=2)
        self.add_task('hessian_loop', 'loop', count=p.number*p.ring_number)
        self.add_task('hessian_convolution', 'complex_mult')
        self.add_task('hessian_analysis')
        self.add_copy_task('hessian_broadcast')

        self.add_task('m1', 'monitor')
        self.add_task('m2', 'monitor')
        self.add_task('m3', 'monitor')
        self.add_task('m4', 'monitor')
        self.add_task('m5', 'monitor')
        self.add_task('m6', 'monitor')
        self.add_task('m7', 'monitor')
        self.add_task('null')

    def setup_graph_a(self):
        b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'fft1')#, 'm1')
        b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')#, 'm2')
        b3 = self.branch('ring_convolution', 'ifft', 'write')
        self.graph.merge_branch(b1, b2, b3)

    def setup_graph_b(self):
        b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'fft1')
        b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
        b3 = self.branch('ring_convolution', 's1')
        self.graph.merge_branch(b1, b2, b3)

        b4 = self.branch('hessian_kernel', 'hessian_fft', 'hessian_loop')
        b5 = self.branch('hessian_convolution', 'ifft', 'hessian_analysis', 'write')
        self.graph.merge_branch(b3, b4, b5)

    def setup_graph(self):
        b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'fft1')
        b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
        b3 = self.branch('ring_convolution', 's1')
        self.graph.merge_branch(b1, b2, b3)

        b4 = self.branch('hessian_kernel', 'hessian_fft', 'hessian_loop')
        b5 = self.branch('hessian_convolution', 'ifft', 'hessian_analysis', 'hessian_broadcast', 'stack1', 'unstack1')
        self.graph.merge_branch(b3, b4, b5)

        b6 = self.branch('hessian_broadcast', 'local_maxima', 'label_cluster', 'stack2', 'combine_test', 'unstack2')
        b7 = self.branch('blob_test', 'stack3', 'sum', 'write')
        self.graph.merge_branch(b5, b6, b7)
 

parms = dict( # default parameters
    in_path = 'data/input/sampleC-substack',
    #in_path = 'data/input/sampleB-substack',
    out_file = 'data/res_small.tif',
    number = 10,
    profiling = True,
    scale = 1,
    ring_start = 2,
    ring_end = 10,
    ring_thickness = 3,
    maxima_sigma = 3,
    blog_alpha = 0.8
    )

j = PivJob(parms)
j.add_tasks()
j.setup_graph()

parms.update(dict(
    out_file = 'data/res_large.tif',
    scale = 2,
    ring_start = 8,
    ring_end = 50,
    ring_thickness = 5,
    maxima_sigma = 2.0,
    blob_alpha = 0.2
))

j2 = PivJob(parms)
j2.add_tasks()
j2.setup_graph()

#t = j.run_t()
t2 = j2.run_t()

print t2
