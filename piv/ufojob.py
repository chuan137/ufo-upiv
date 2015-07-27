from gi.repository import Ufo
from taskgraph import TaskGraph
import types
import json

class UfoJob():
    def __init__(self):
       self.pluginmanager = Ufo.PluginManager()
       self.tasks = {}
       self.graph = TaskGraph()

    def graph_connect_branch(self, b):
        b = self.convert_tasks(b)
        self.graph.connect_branch(b)
        return b

    def graph_merge_branch(self, b1, b2, b3):
        b1 = self.convert_tasks(b1)
        b2 = self.convert_tasks(b2)
        b3 = self.convert_tasks(b3)
        self.graph.merge_branch(b1, b2, b3)

    def convert_tasks(self, b):
        if isinstance(b, types.ListType):
            b = [self.tasks.get(n) for n in b]
        else:
            b = self.tasks.get(n)
        return b

    def load_tasks_config(self, config_file):
        ''' parse ufo tasks and properties from json file '''
        
        self.tasks = {}  # clear tasks
        with open(config_file) as f: 
            tasks = json.loads(f.read())

        for t, p in tasks.iteritems():
            # plugin name is task name if not specified
            plugin = p.get('plugin') or t 
            task = self.pluginmanager.get_task(plugin)

            for pn, pv in p.iteritems():
                if pn != 'plugin':
                    task.set_property(pn, pv)
            self.tasks[t] = task
