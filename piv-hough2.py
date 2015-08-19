#!/usr/bin/env python
from gi.repository import Ufo
from python.pivjob import PivJob
from python.ddict import DotDict
import logging

fmt = logging.Formatter('%(name)s %(levelname)s %(message)s')
fmt = logging.Formatter('%(levelname)s: %(message)s')
fh = logging.FileHandler('piv-hough.log')
fh.setFormatter(fmt)

ch = logging.StreamHandler()
ch.setFormatter(fmt)

logger = logging.getLogger('PivHough')
logger.setLevel(logging.INFO)
logger.addHandler(fh)
logger.addHandler(ch)


class PivJob(PivJob):
    def add_tasks(self):
        p = self.parms
    
        self.add_task('contrast', 'piv_contrast')
        self.add_task('input_fft', 'fft', dimensions=2)

        self.add_task('ifft', dimensions=2)
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
        b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'input_fft')#, 'm1')
        b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')#, 'm2')
        b3 = self.branch('ring_convolution', 'ifft', 'write')
        self.graph.merge_branch(b1, b2, b3)

    def setup_graph_b(self):
        b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'input_fft')
        b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
        b3 = self.branch('ring_convolution', 's1')
        self.graph.merge_branch(b1, b2, b3)

        b4 = self.branch('hessian_kernel', 'hessian_fft', 'hessian_loop')
        b5 = self.branch('hessian_convolution', 'ifft', 'hessian_analysis', 'write')
        self.graph.merge_branch(b3, b4, b5)

    def setup_graph(self):
        b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'input_fft')
        b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
        b3 = self.branch('ring_convolution', 's1')
        self.graph.merge_branch(b1, b2, b3)

        b4 = self.branch('hessian_kernel', 'hessian_fft', 'hessian_loop')
        b5 = self.branch('hessian_convolution', 'ifft', 'hessian_analysis', 'hessian_broadcast', 'stack1', 'unstack1')
        self.graph.merge_branch(b3, b4, b5)

        b6 = self.branch('hessian_broadcast', 'local_maxima', 'label_cluster', 'stack2', 'combine_test', 'unstack2')
        b7 = self.branch('blob_test', 'stack3', 'sum', 'write')
        self.graph.merge_branch(b5, b6, b7)

    def run(self):
        scale = self.tasks.rescale.props.factor
        fmt_f = "%16s.%-16s= %8.3f"
        fmt_i = "%16s.%-16s= %8i"
        fmt_s = "%16s:%8s = %s"
        logger.info( 'input path\t: ' + self.tasks.read.props.path)
        logger.info( 'output filename\t: ' + self.tasks.write.props.filename)
        logger.info( '')
        logger.info( fmt_i % ('Ring', 'start', self.tasks.ring_pattern.props.ring_start/scale))
        logger.info( fmt_i % ('Ring', 'end', self.tasks.ring_pattern.props.ring_end/scale))
        logger.info( fmt_i % ('Ring', 'step', self.tasks.ring_pattern.props.ring_step/scale))
        logger.info( '')
        logger.info( fmt_f % ('Contrast', 'low_cut', self.tasks.contrast.props.c1))
        logger.info( fmt_f % ('Contrast', 'high_cut', self.tasks.contrast.props.c2))
        logger.info( fmt_f % ('Contrast', 'shift', self.tasks.contrast.props.c3))
        logger.info( fmt_f % ('Contrast', 'width', self.tasks.contrast.props.c4))
        logger.info( fmt_f % ('Contrast', 'gamma', self.tasks.contrast.props.gamma))
        logger.info( fmt_f % ('LocalMax', 'threshold', self.tasks.local_maxima.props.sigma))
        logger.info( fmt_f % ('BlobTest', 'alpha', self.tasks.blob_test.props.alpha))

        runtime = self.run_t()
        logger.info( '')
        logger.info( 'Program finished in %s seconds' % runtime )



in_path     = 'data/sampleB'
number      = 10

parms = DotDict(dict( # parameters for small rings
        in_path         = in_path,
        number          = number,
        profiling       = True,
        out_file        = 'data/res_small.tif',
        scale           = 1,
        ring_start      = 2,
        ring_end        = 10,
        ring_thickness  = 3,
        maxima_sigma    = 3,
        blob_alpha      = 0.8 ))

j = PivJob(parms)
j.add_tasks()
j.setup_graph()
#j.run()

parms.update(dict( # parameters for large rings
        out_file        = 'data/res_large.tif',
        scale           = 2,
        ring_start      = 8,
        ring_end        = 50,
        ring_thickness  = 5,
        maxima_sigma    = 1.5,
        blob_alpha       = 0.20 ))

j2 = PivJob(parms)
j2.add_tasks()
j2.setup_graph()
j2.run()

