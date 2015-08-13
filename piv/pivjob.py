from gi.repository import Ufo
from .ufo_extension import PluginManager, TaskGraph
from .ufojob import UfoJob
from .ddict import DotDict

class PivJob(UfoJob):
    _default_parms = dict(
        device = 'GPU',     # GPU/CPU
        profiling = False,  # True/False
        sched = '',
        scale = 2,
        ring_start = 6,     # ring sizes
        ring_end = 40,
        ring_step = 2,
        ring_thickness = 6,
        number_of_images = 1,   # input image
        sigma_top = 9,
        sigma_bottom = -4,
        start = 0,
        xshift = 0,
        yshift = 0,
        img_path = './data/input/input-stack.tif',
        out_file = './data/res.tif',
        blob_alpha = 1.0,
        maxima_sigma = 3.0
        )

    def __init__(self, parms={}):
        super(PivJob, self).__init__(parms)
        self.setup_tasks()

    def setup_graph(self):
        b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'brightness')
        b2 = self.branch('ring_pattern', 'ring_pattern_loop')
        b3 = self.branch('hessian_kernel', 'hessian_kernel_loop')
        b4 = self.branch('hessian_convolve', 'hessian_analysis', 'bc_hessian', 'stack1', 'unstack1')
        b5 = self.branch('bc_hessian', 'local_maxima', 'label_cluster', 'stack2', 'combine_test', 'unstack2')
        b6 = self.branch('blob_test', 'stack3', 'sum', 'write')
        hough = self.tasks.hough_convolve
        self.graph.merge_branch(b1, b2, hough)
        self.graph.merge_branch(hough, b3, b4)
        self.graph.merge_branch(b4, b5, b6)

    def setup_tasks(self):
        p = self.parms
        scale = p.scale
        ring_count = (p.ring_end - p.ring_start) / p.ring_step + 1

        self.add_task('read', path=p.img_path, number=p.number_of_images, start=p.start)
        self.add_task('write', filename=p.out_file)
        self.add_task('crop', x=p.xshift, y=p.yshift, width=1024, height=1024)
        self.add_task('brightness', 'brightness-cut', low=1.0, high=3.0)
        self.add_task('rescale', factor=1.0/scale)
        self.add_task('contrast', remove_high=0)
        self.add_task('denoise', matrix_size=int(14/scale))

        self.add_task('ring_pattern', ring_start=p.ring_start, ring_end=p.ring_end,
                            ring_step=p.ring_step, ring_thickness=p.ring_thickness,
                            width=1024/scale, height=1024/scale)
        self.add_task('ring_pattern_loop', 'buffer', dup_count=p.number_of_images, loop=1)
        self.add_task('hough_convolve', 'fftconvolution')

        self.add_task('hessian_kernel', sigma=2.0/scale, width=1024/scale, height=1024/scale)
        self.add_task('hessian_kernel_loop', 'buffer', dup_count=p.number_of_images, loop=1)
        self.add_task('hessian_convolve', 'fftconvolution')
        self.add_task('hessian_analysis')
        self.add_task('hessian_stack', 'stack', number=ring_count)

        
        self.add_task('local_maxima', sigma=p.maxima_sigma)
        self.add_task('label_cluster', 'label-cluster')
        self.add_task('combine_test', 'combine-test')
        self.add_task('blob_test', alpha=p.blob_alpha)
        self.add_task('sum')
        self.add_task('ring_writer')

        self.add_task('null')
        self.add_task('log')

        self.add_task('stack1', 'stack', number=ring_count)
        self.add_task('stack2', 'stack', number=ring_count)
        self.add_task('stack3', 'stack', number=ring_count)
        self.add_task('unstack1', 'slice')
        self.add_task('unstack2', 'slice')
        self.add_task('monitor1', 'monitor')
        self.add_task('monitor2', 'monitor')

        self.add_copy_task('bc_contrast')
        self.add_copy_task('bc_hessian')
