from gi.repository import Ufo
from .ufo_extension import TaskGraph, PluginManager
from .ddict import DotDict
from timeit import Timer
import types
import json

class UfoJob(object):
    _default_parms = dict(
            profiling = False,
            device = 'GPU'
            )

    def __init__(self, parms={}):
        self.pm = PluginManager()
        self.graph = TaskGraph()
        self.sched= Ufo.Scheduler()
        self.tasks = DotDict()
        self.parms = DotDict(self._default_parms)
        self.parms.update(parms)

    def branch(self, *args):
        return [self.tasks.get(n) for n in args]

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

    def setup_schedule(self):
        self.sched.props.enable_tracing = self.parms.profiling # profiling
        if self.parms.get('device') is 'CPU':
            resource = Ufo.Resources(device_type=Ufo.DeviceType.CPU)
        else:
            resource = Ufo.Resources(device_type=Ufo.DeviceType.GPU)
        self.sched.set_resources(resource)


#def graph_connect_branch(self, b):
    #b = self.convert_tasks(b)
    #self.graph.connect_branch(b)
    #return b

#def graph_merge_branch(self, b1, b2, b3):
    #b1 = self.convert_tasks(b1)
    #b2 = self.convert_tasks(b2)
    #b3 = self.convert_tasks(b3)
    #self.graph.merge_branch(b1, b2, b3)

#def convert_tasks(self, b):
    #if isinstance(b, types.ListType):
        #b = [self.tasks.get(n) for n in b]
    #else:
        #b = self.tasks.get(n)
    #return b

#def load_tasks_config(self, config_file):
    #''' parse ufo tasks and properties from json file '''
    
    #self.tasks = {}  # clear tasks
    #with open(config_file) as f: 
        #tasks = json.loads(f.read())

    #for t, p in tasks.iteritems():
        ## plugin name is task name if not specified
        #plugin = p.get('plugin') or t 
        #task = self.pluginmanager.get_task(plugin)

        #for pn, pv in p.iteritems():
            #if pn != 'plugin':
                #task.set_property(pn, pv)
        #self.tasks[t] = task
