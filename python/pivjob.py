from gi.repository import Ufo
from ufo_extension import PluginManager, TaskGraph
from ufojob import UfoJob
from ddict import DotDict

class PivJob(UfoJob):
    def __init__(self, parms={}):
        default = dict(
            in_path     = './data/input/input-stack.tif',
            out_file    = './data/res.tif',
            schedfixed  = True,
            number      = 1,        # input image
            start       = 0,        # first image
            scale       = 2,        # downsize scale
            ring_start  = 6,        # ring sizes
            ring_end    = 40,
            ring_step   = 2,
            ring_thickness = 6,
            xshift      = 0,
            yshift      = 0,
            maxima_sigma = 3.0, 
            blob_alpha  = 1.0 )

        default.update(parms)
        super(PivJob, self).__init__(default)

        self.parms.ring_number = \
            (self.parms.ring_end - self.parms.ring_start) / self.parms.ring_step + 1
        self.setup_tasks()

    def setup_tasks(self):
        p  = self.parms
        sc = self.parms.scale

        self.add_task('crop', x=p.xshift, y=p.yshift, width=1024, height=1024)
        self.add_task('contrast', 'piv_contrast')
        self.add_task('rescale', factor=1.0/sc)
        self.add_task('input_fft', 'fft', dimensions=2)

        self.add_task('ring_fft', 'fft', dimensions=2)
        self.add_task('ring_stack', 'stack', number=p.ring_number)
        self.add_task('ring_loop', 'loop', count=p.number)
        self.add_task('ring_convolution', 'complex_mult')
        self.add_task('ring_slice', 'slice')
        self.add_task('ring_pattern', 
                  ring_start=p.ring_start/sc, ring_end=p.ring_end/sc,
                  ring_step=p.ring_step/sc, ring_thickness=p.ring_thickness/sc,
                  width=1024/sc, height=1024/sc)

        self.add_task('hessian_kernel', sigma=2.0/sc, width=1024/sc, height=1024/sc)
        self.add_task('hessian_fft', 'fft', dimensions=2)
        self.add_task('hessian_loop', 'loop', count=p.number*p.ring_number)
        self.add_task('hessian_convolution', 'complex_mult')
        self.add_task('hessian_analysis')
        self.add_copy_task('hessian_broadcast') 

        self.add_task('ifft', dimensions=2)

        self.add_task('local_maxima', sigma=p.maxima_sigma)
        self.add_task('label_cluster', 'label-cluster')
        self.add_task('combine_test', 'combine-test')
        self.add_task('blob_test', alpha=p.blob_alpha)
        self.add_task('sum')
        self.add_task('ring_writer')
        p = self.parms
        scale = p.scale

        self.add_task('read', path=p.in_path, number=p.number, start=p.start)
        self.add_task('write', filename=p.out_file)

        self.add_task('stack1', 'stack', number=p.ring_number)
        self.add_task('stack2', 'stack', number=p.ring_number)
        self.add_task('stack3', 'stack', number=p.ring_number)
        self.add_task('unstack1', 'slice')
        self.add_task('unstack2', 'slice')

        self.add_task('m1', 'monitor')
        self.add_task('m2', 'monitor')
        self.add_task('m3', 'monitor')
        self.add_task('m4', 'monitor')
        self.add_task('m5', 'monitor')
        self.add_task('m6', 'monitor')
        self.add_task('m7', 'monitor')
        self.add_task('null')

    def setup_graph(self):
        pass



    # def setup_graph(self):
        # b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'brightness')
        # b2 = self.branch('ring_pattern', 'ring_pattern_loop')
        # b3 = self.branch('hessian_kernel', 'hessian_kernel_loop')
        # b4 = self.branch('hessian_convolve', 'hessian_analysis', 'bc_hessian', 'stack1', 'unstack1')
        # b5 = self.branch('bc_hessian', 'local_maxima', 'label_cluster', 'stack2', 'combine_test', 'unstack2')
        # b6 = self.branch('blob_test', 'stack3', 'sum', 'write')
        # hough = self.tasks.hough_convolve
        # self.graph.merge_branch(b1, b2, hough)
        # self.graph.merge_branch(hough, b3, b4)
        # self.graph.merge_branch(b4, b5, b6)


