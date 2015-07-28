from gi.repository import Ufo
from .ufo_extension import PluginManager, TaskGraph
from .ddict import DotDict
from timeit import Timer

class PivJob():
    _default_parms = dict(
        device = 'GPU',     # GPU/CPU
        profiling = False,  # True/False
        scale = 2,
        ring_start = 6,     # ring sizes
        ring_end = 40,
        ring_step = 2,
        ring_thickness = 6,
        number_of_images = 1,   # input image
        start = 0,
        xshift = 0,
        yshift = 0,
        img_path = './data/input/input-stack.tif',
        out_file = './data/res.tif',
        blob_alpha = 1.0,
        maxima_sigma = 3.0
        )

    def __init__(self, parms={}):
        self.pm = PluginManager()
        self.graph = TaskGraph()
        self.sched= Ufo.Scheduler()
        self.tasks = DotDict()
        self.parms = DotDict(parms)
        # setup tasks and graph
        self.set_default_parms()
        self.setup_tasks()


    def set_default_parms(self):
        for k, v in self._default_parms.iteritems():
            if not self.parms.get(k):
                self.parms[k] = v


    def setup_tasks(self):
        parms = self.parms
        pm = self.pm

        scale = parms.scale
        ring_count = (parms.ring_end - parms.ring_start) / parms.ring_step + 1

        self.tasks.read = pm.get_task('read', 
                path = parms.img_path,
                number = parms.number_of_images,
                start = parms.start)
        self.tasks.write = pm.get_task('write', filename = parms.out_file)
        self.tasks.crop = pm.get_task('crop', 
                x = parms.xshift, y = parms.yshift, 
                width = 1024, height = 1024)
        self.tasks.brightness = pm.get_task('brightness-cut', 
                low = 1.0, 
                high = 3.0)

        self.tasks.gen_ring_patterns = pm.get_task('ring_pattern',
                ring_start = parms.ring_start,
                ring_step = parms.ring_step,
                ring_end = parms.ring_end,
                ring_thickness = parms.ring_thickness,
                width = 1024/scale, height = 1024/scale)
        self.tasks.ring_pattern_loop = pm.get_task('buffer',
                dup_count = parms.number_of_images, 
                loop = 1)
        self.tasks.hessian_kernel = pm.get_task('hessian_kernel',
                sigma = 2.0 / scale,
                width = 1024 / scale,
                height = 1024 / scale)
        self.tasks.hessian_kernel_loop = pm.get_task('buffer',
                dup_count = parms.number_of_images,
                loop = 1)

        self.tasks.rescale = pm.get_task('rescale', factor = 1.0 / scale)
        self.tasks.contrast = pm.get_task('contrast', remove_high = 0)
        self.tasks.denoise = pm.get_task('denoise', matrix_size = int(14/scale))

        self.tasks.hough_convolve     = pm.get_task('fftconvolution')
        self.tasks.hessian_convolve   = pm.get_task('fftconvolution')
        self.tasks.hessian_analysis   = pm.get_task('hessian_analysis')
        self.tasks.hessian_stack      = pm.get_task('stack', number=ring_count)

        self.tasks.local_maxima = pm.get_task('local-maxima', sigma=parms.maxima_sigma)
        self.tasks.label_cluster = pm.get_task('label-cluster')
        self.tasks.combine_test = pm.get_task('combine-test')
        self.tasks.blob_test = pm.get_task('blob_test', alpha=parms.blob_alpha)

        self.tasks.sum = pm.get_task('sum')
        self.tasks.log = pm.get_task('log')
        self.tasks.null = pm.get_task('null')

        self.tasks.stack1 = pm.get_task('stack', number=ring_count)
        self.tasks.stack2 = pm.get_task('stack', number=ring_count)
        self.tasks.stack3 = pm.get_task('stack', number=ring_count)
        self.tasks.unstack1 = pm.get_task('slice')
        self.tasks.unstack2 = pm.get_task('slice')
        self.tasks.monitor = pm.get_task('monitor')
        self.tasks.monitor1 = pm.get_task('monitor')

        self.tasks.bc_contrast = Ufo.CopyTask()
        self.tasks.bc_hessian = Ufo.CopyTask()
        self.tasks.ring_writer = pm.get_task('ring_writer')


    def setup_graph(self):
        branch1 = ['read', 'crop', 'rescale', 'contrast', 'brightness']
        branch2 = ['gen_ring_patterns', 'ring_pattern_loop']
        branch3 = ['hessian_kernel', 'hessian_kernel_loop']
        branch4 = ['hessian_convolve', 'hessian_analysis', 'bc_hessian', 'stack1', 'unstack1']
        branch5 = ['bc_hessian', 'local_maxima', 'label_cluster', 'stack2', 'combine_test', 'unstack2']
        branch6 = ['blob_test', 'stack3', 'sum', 'write']

        branch1 = [self.tasks.get(n) for n in branch1]
        branch2 = [self.tasks.get(n) for n in branch2]
        branch3 = [self.tasks.get(n) for n in branch3]
        branch4 = [self.tasks.get(n) for n in branch4]
        branch5 = [self.tasks.get(n) for n in branch5]
        branch6 = [self.tasks.get(n) for n in branch6]
        hough_convolve = self.tasks.hough_convolve

        self.graph.merge_branch(branch1, branch2, hough_convolve)
        self.graph.merge_branch(hough_convolve, branch3, branch4)
        self.graph.merge_branch(branch4, branch5, branch6)

    def setup_schedule(self):
        self.sched.props.enable_tracing = self.parms.profiling # profiling
        if self.parms.get('device') is 'CPU':
            resource = Ufo.Resources(device_type=Ufo.DeviceType.CPU)
        else:
            resource = Ufo.Resources(device_type=Ufo.DeviceType.GPU)
        self.sched.set_resources(resource)


    def run(self):
        self.setup_schedule()
        self.sched.run(self.graph)


    def run_t(self, n=1):
        def timer_function():
            self.sched.run(self.graph)

        self.setup_schedule()
        tm = Timer(timer_function)
        t = tm.timeit(n)
        return t

       



