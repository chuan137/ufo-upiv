from gi.repository import Ufo
from ufo_extension import PluginManager, TaskGraph
from ufojob import UfoJob
from ddict import DotDict
from utils import LogMixin
import os

default_parms = dict(
        in_path     = './data/input/input-stack.tif',
        out_file    = './data/res.tif',
        number      = 1,        # input image
        start       = 0,        # first image
        scale       = 2,        # downsize scale
        ring_method = 0,
        ring_start  = 6,        # ring sizes
        ring_end    = 40,
        ring_step   = 2,
        ring_thickness = 6,
        xshift      = 0,
        yshift      = 0,
        maxima_sigma = 3.0, 
        blob_alpha  = 1.0,
        likelihoodmask = 11,
        likelihoodmaskinner = 6,
        width       = 1024,
        height      = 1024 )

class PivJob(UfoJob):
    def __init__(self, parms={}):
        super(PivJob, self).__init__(profiling=False, schedfixed=True, deviceCPU=False)

        self.parms = DotDict(default_parms)
        self.parms.update(parms)
        self.parms.ring_number = \
            (self.parms.ring_end - self.parms.ring_start) / self.parms.ring_step + 1
        self.setup_basic_tasks()

    def setup_basic_tasks(self):
        p  = self.parms

        self.add_task('read', path=p.in_path, number=p.number, start=int(p.start))
        if p.out_file.endswith(('.txt')):
            self.add_task('ring_writer', filename=p.out_file)
        else:
            self.add_task('write', filename=p.out_file)
            self.add_task('ring_writer', filename='res.txt')
        self.add_task('m1', 'monitor')
        self.add_task('m2', 'monitor')
        self.add_task('m3', 'monitor')
        self.add_task('m4', 'monitor')
        self.add_task('m5', 'monitor')
        self.add_task('m6', 'monitor')
        self.add_task('m7', 'monitor')
        self.add_task('null')

        sc = self.parms.scale

        self.add_task('hessian_kernel', sigma=2.0/sc, width=1024/sc, height=1024/sc)
        self.add_task('hessian_fft', 'fft', dimensions=2)
        self.add_task('hessian_loop', 'loop', count=p.number*p.ring_number)
        self.add_task('hessian_convolution', 'complex_mult')
        self.add_task('hessian_analysis')
        self.add_copy_task('hessian_broadcast') 

        self.add_task('local_maxima', sigma=p.maxima_sigma)
        self.add_task('label_cluster', 'label-cluster')
        self.add_task('combine_test', 'combine-test')
        self.add_task('blob_test', alpha=p.blob_alpha)
        self.add_task('sum')

        self.add_task('stack1', 'stack', number=p.ring_number)
        self.add_task('stack2', 'stack', number=p.ring_number)
        self.add_task('stack3', 'stack', number=p.ring_number)
        self.add_task('unstack1', 'slice')
        self.add_task('unstack2', 'slice')

    def setup_tasks(self):
        pass

    def setup_graph(self, flag=0):
        if flag == 0:
            b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'bc_contrast', 'input_fft')
            b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
            b3 = self.branch('bc_contrast')
            b4 = self.branch('ring_convolution', 'ifft', 'likelihood', 'cand')
            b5 = self.branch('azimu', 'ring_writer')
            self.graph.merge_branch(b1, b2, b4)
            self.graph.merge_branch(b3, b4, b5)
        elif flag == 1:
            b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'bc_contrast', 'input_fft')
            b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
            b3 = self.branch('ring_convolution', 'ifft', 'likelihood', 'cand', 'ring_writer')
            self.graph.merge_branch(b1, b2, b3)
        elif flag == 2:
            b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'input_fft')#, 'm1')
            b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')#, 'm2')
            b3 = self.branch('ring_convolution', 'ifft', 'write')
            self.graph.merge_branch(b1, b2, b3)
        elif flag == 3:
            b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'input_fft')
            b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
            b3 = self.branch('ring_convolution', 'ring_slice')
            self.graph.merge_branch(b1, b2, b3)

            b4 = self.branch('hessian_kernel', 'hessian_fft', 'hessian_loop')
            b5 = self.branch('hessian_convolution', 'ifft', 'hessian_analysis', 'write')
            self.graph.merge_branch(b3, b4, b5)
        elif flag == 4:
            b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'input_fft')
            b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
            b3 = self.branch('ring_convolution', 'ring_slice')
            self.graph.merge_branch(b1, b2, b3)

            b4 = self.branch('hessian_kernel', 'hessian_fft', 'hessian_loop')
            b5 = self.branch('hessian_convolution', 'ifft', 'hessian_analysis', 
                             'hessian_broadcast', 'stack1', 'unstack1')
            self.graph.merge_branch(b3, b4, b5)

            b6 = self.branch('hessian_broadcast', 'local_maxima', 'label_cluster', 
                             'stack2', 'combine_test', 'unstack2')
            b7 = self.branch('blob_test', 'stack3', 'sum', 'write')
            self.graph.merge_branch(b5, b6, b7)

    def run(self, flag=0):
        self.setup_tasks()
        self.setup_graph(flag)
        #self.log_tasks()
        runtime = self.run_t()
        self.logger.info('')
        self.logger.info('Program finished in %s seconds' % runtime )

    def log_tasks(self):
        scale = self.tasks.rescale.props.factor
        fmt_f = "%16s.%-16s= %8.3f"
        fmt_i = "%16s.%-16s= %8i"
        self.logger.info( 'input:  ' + self.tasks.read.props.path)
        self.logger.info( 'output: ' + self.tasks.write.props.filename)
        self.logger.info( '')
        self.logger.info( fmt_i % ('Ring', 'start', self.tasks.ring_pattern.props.start/scale))
        self.logger.info( fmt_i % ('Ring', 'end', self.tasks.ring_pattern.props.end/scale))
        self.logger.info( fmt_i % ('Ring', 'step', self.tasks.ring_pattern.props.step/scale))
        self.logger.info( fmt_f % ('Contrast', 'low_cut', self.tasks.contrast.props.c1))
        self.logger.info( fmt_f % ('Contrast', 'high_cut', self.tasks.contrast.props.c2))
        self.logger.info( fmt_f % ('Contrast', 'shift', self.tasks.contrast.props.c3))
        self.logger.info( fmt_f % ('Contrast', 'width', self.tasks.contrast.props.c4))
        self.logger.info( fmt_f % ('Contrast', 'gamma', self.tasks.contrast.props.gamma))
        self.logger.info( fmt_f % ('LocalMax', 'threshold', self.tasks.local_maxima.props.sigma))
        self.logger.info( fmt_f % ('BlobTest', 'alpha', self.tasks.blob_test.props.alpha))
