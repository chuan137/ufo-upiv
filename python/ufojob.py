from gi.repository import Ufo
from ufo_extension import TaskGraph, PluginManager
from utils import LogMixin
from ddict import DotDict
from timeit import Timer

class UfoJob(object):
    pass

class UfoJob(UfoJob, LogMixin):
    def __init__(self, profiling=False, schedfixed=False, deviceCPU=False):
        self._profiling = profiling
        self._schedfixed = schedfixed
        self._deviceCPU = deviceCPU
        self.pm = PluginManager()
        self.graph = TaskGraph()
        self.tasks = DotDict()

    def init_scheduler(self):
        if self._deviceCPU:
            self.logger.debug('run on cpu')
            self.resource = Ufo.Resources(device_type=Ufo.DeviceType.CPU)
        else:
            self.logger.debug('run on gpu')
            self.resource = Ufo.Resources(device_type=Ufo.DeviceType.GPU)
        if self._schedfixed:
            self.logger.debug('fixed Scheduler')
            self.sched = Ufo.FixedScheduler()
        else:
            self.logger.debug('normal Scheduler')
            self.sched = Ufo.Scheduler()
        self.sched.set_resources(self.resource)
        self.sched.set_property('enable_tracing', self._profiling)

    def run_t(self, n=1):
        self.init_scheduler() 
        def timer_function():
            self.sched.run(self.graph)
        tm = Timer(timer_function)
        t = tm.timeit(n)
        # print self.sched
        # print self.resource
        return t

    @property
    def profiling(self):
        return self._profiling
    @profiling.setter
    def profiling(self, value):
        self._profiling = value

    @property
    def schedfixed(self):
        return self._schedfixed
    @schedfixed.setter
    def schedfixed(self, value):
        self._schedfixed = value

    @property
    def deviceCPU(self):
        return self._deviceCPU
    @deviceCPU.setter
    def deviceCPU(self, value):
        self._deviceCPU = value

    def branch(self, *args):
        try:
            b = [self.tasks.get(n) for n in args]
            self.graph.connect_branch(b)
        except KeyError:
            sys.exit("task %s does not exists" % n)
        return b

    def add_copy_task(self, taskname):
        task = Ufo.CopyTask()
        self.tasks[taskname] = task

    def add_task(self, taskname, plugin=None, **kargs):
        if self.tasks.get('taskname'):
            print 'Warning: %s already exists' % taskname
        if plugin is None:
            plugin = taskname
        task = self.pm.get_task(plugin, **kargs)
        self.tasks[taskname] = task


