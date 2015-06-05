#!/usr/bin/env python
from gi.repository import Ufo

class TaskGraph(Ufo.TaskGraph):
    def connect_branch(self, node_list):
        for i in range(len(node_list)-1):
            n0 = node_list[i]
            n1 = node_list[i+1]
            print i, n0
            self.connect_nodes(n0, n1)
    def merge_branch(self, nlist1, nlist2, nodes):
        if isinstance(nlist1, list):
            n1 = nlist1[-1]
        else:
            n1 = nlist1
        if isinstance(nlist2, list):
            n2 = nlist2[-1]
        else:
            n2 = nlist2
        if isinstance(nodes, list):
            self.connect_nodes_full(n1, nodes[0], 0)
            self.connect_nodes_full(n2, nodes[0], 1)
            self.connect_branch(nodes)
        else:
            self.connect_nodes_full(n1, nodes, 0)
            self.connect_nodes_full(n2, nodes, 1)

class PluginManager(Ufo.PluginManager):
    def get_task(self, task, **kwargs):
        t = super(PluginManager, self).get_task(task)
        t.set_properties(**kwargs)
        return t

pm = PluginManager()
read = pm.get_task('read', path='res/HT2.tif')
local_maxima = pm.get_task('local-maxima', sigma=3)
label_cluster = pm.get_task('label-cluster')
stack = pm.get_task('stack', number=13)
monitor = pm.get_task('monitor')
combine_test = pm.get_task('combine-test')
write = pm.get_task('write', filename='res/res.tif')

g = TaskGraph()
g.connect_branch([read, local_maxima, label_cluster, stack, monitor, combine_test, write])

# Run Ufo
sched = Ufo.Scheduler()
sched.props.enable_tracing = False #True

def timer_function():
    sched.run(g)

from timeit import Timer
tm = Timer('timer_function()', 'from __main__ import timer_function')
t = tm.timeit(1)
print t, 'sec'

