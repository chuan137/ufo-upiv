from gi.repository import Ufo
from .taskgraph import TaskGraph
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
        out_file = './data/res.tif'
        )

    def __init__(self, parms={}):
        self.pm = Ufo.PluginManager()
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
        ring_start = parms.ring_start
        ring_end = parms.ring_end
        ring_step = parms.ring_step
        ring_thickness = parms.ring_thickness
        
        ring_count = (ring_end - ring_start) / ring_step + 1

        if not self.tasks.get('read'):
            self.tasks.read = pm.get_task('read')
        self.tasks.read.props.path = parms.img_path
        self.tasks.read.props.number = parms.number_of_images
        self.tasks.read.props.start = parms.start

        if not self.tasks.get('write'):
            self.tasks.write = pm.get_task('write')
        self.tasks.write.props.filename = parms.out_file

        if not self.tasks.get('cutroi'):
            self.tasks.cutroi = pm.get_task('cut-roi')
        self.tasks.cutroi.props.x = parms.xshift
        self.tasks.cutroi.props.y = parms.yshift
        self.tasks.cutroi.props.width = 1024
        self.tasks.cutroi.props.height = 1024

        if not self.tasks.get('rescale'):
            self.tasks.rescale = pm.get_task('rescale')
        self.tasks.rescale.props.factor = 1.0/scale

        if not self.tasks.get('denoise'):
            self.tasks.denoise = pm.get_task('denoise')
        self.tasks.denoise.props.matrix_size = int(14/scale)

        if not self.tasks.get('contrast'):
            self.tasks.contrast = pm.get_task('contrast')
        self.tasks.contrast.props.remove_high = 0

        if not self.tasks.get('gen_ring_patterns'):
            self.tasks.gen_ring_patterns = pm.get_task('ring_pattern')
        self.tasks.gen_ring_patterns.props.ring_start = ring_start
        self.tasks.gen_ring_patterns.props.ring_end   = ring_end
        self.tasks.gen_ring_patterns.props.ring_step  = ring_step
        self.tasks.gen_ring_patterns.props.ring_thickness = ring_thickness
        self.tasks.gen_ring_patterns.props.width  = 1024 / scale
        self.tasks.gen_ring_patterns.props.height = 1024 / scale

        if not self.tasks.get('ring_pattern_loop'):
            self.tasks.ring_pattern_loop = pm.get_task('buffer')
        self.tasks.ring_pattern_loop.props.dup_count = parms.number_of_images 
        self.tasks.ring_pattern_loop.props.loop = 1 

        if not self.tasks.get('hessian_kernel'):
            self.tasks.hessian_kernel = pm.get_task('hessian_kernel')
        self.tasks.hessian_kernel.props.sigma = 2. / scale
        self.tasks.hessian_kernel.props.width = 1024 / scale
        self.tasks.hessian_kernel.props.height = 1024 / scale

        if not self.tasks.get('hessian_kernel_loop'):
            self.tasks.hessian_kernel_loop = pm.get_task('buffer')
        self.tasks.hessian_kernel_loop.props.dup_count = parms.number_of_images
        self.tasks.hessian_kernel_loop.props.loop = 1 

        if not self.tasks.get('hough_convolve'):
            self.tasks.hough_convolve = pm.get_task('fftconvolution')
        if not self.tasks.get('hessian_convolve'):
            self.tasks.hessian_convolve = pm.get_task('fftconvolution')
        if not self.tasks.get('hessian_analysis'):
            self.tasks.hessian_analysis = pm.get_task('hessian_analysis')
        
        if not self.tasks.get('hessian_stack'):
            self.tasks.hessian_stack = pm.get_task('stack')
        self.tasks.hessian_stack.props.number = ring_count

        if not self.tasks.get('blob_test'):
            self.tasks.blob_test = pm.get_task('blob_test')
        self.tasks.blob_test.props.max_detection = 100
        self.tasks.blob_test.props.ring_start = ring_start
        self.tasks.blob_test.props.ring_step = ring_step
        self.tasks.blob_test.props.ring_end = ring_end

        if not self.tasks.get('ring_writer'):
            self.tasks.ring_writer = pm.get_task('ring_writer')

        if not self.tasks.get('broadcast_contrast'):
            self.tasks.broadcast_contrast = Ufo.CopyTask()

        if not self.tasks.get('broadcast_hough_convolve'):
            self.tasks.broadcast_hough_convolve = Ufo.CopyTask()

        if not self.tasks.get('null'):
            self.tasks.null = pm.get_task('null')
        if not self.tasks.get('monitor'):
            self.tasks.monitor = pm.get_task('monitor')


    def setup_graph(self):
        branch1 = ['read', 'cutroi', 'rescale', 'contrast', 'broadcast_contrast']
        branch2 = ['gen_ring_patterns', 'ring_pattern_loop']
        branch3 = ['hessian_kernel', 'hessian_kernel_loop']
        branch4 = ['hessian_convolve', 'hessian_analysis', 'hessian_stack', 'blob_test', 'ring_writer']
#branch4 = [hessian_convolve, hessian_analysis, hessian_stack, blob_test, monitor,ring_writer]
#branch4 = [hessian_convolve, hessian_analysis, monitor, write]
#branch1 = [read, cutroi, rescale, denoise, contrast, broadcast_contrast]
#branch4 = [hessian_convolve, hessian_analysis, hessian_stack, blob_test, monitor, null]

        branch1 = [self.tasks.get(n) for n in branch1]
        branch2 = [self.tasks.get(n) for n in branch2]
        branch3 = [self.tasks.get(n) for n in branch3]
        branch4 = [self.tasks.get(n) for n in branch4]
        hough_convolve = self.tasks.hough_convolve

        self.graph.connect_branch(branch1)
        self.graph.connect_branch(branch2)
        self.graph.connect_branch(branch3)
        self.graph.connect_branch(branch4)
        self.graph.merge_branch(branch1, branch2, hough_convolve)
        self.graph.merge_branch(hough_convolve, branch3, branch4)
         

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

       



