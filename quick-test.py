#!/usr/bin/env python
from gi.repository import Ufo
from ufo_extension import TaskGraph, PluginManager

pm = PluginManager()

local_maxima = pm.get_task('local-maxima', sigma=3)
label_cluster = pm.get_task('label-cluster')
combine_test = pm.get_task('combine-test')
blob_test = pm.get_task('blob_test')
null = pm.get_task('null')

bc_read = Ufo.CopyTask()
stack = pm.get_task('stack', number=13)
stack2 = pm.get_task('stack', number=13)
unstack = pm.get_task('unstack')
unstack2 = pm.get_task('unstack')
monitor = pm.get_task('monitor')
monitor1 = pm.get_task('monitor')

graph = 0
g = TaskGraph()

if graph == 0:
    read = pm.get_task('read', path='res/HT2.tif')
    write = pm.get_task('write', filename='res/res.tif')

    if True:
        branch1 = [read, monitor, bc_read, stack2, unstack2]
        #branch2 = [bc_read, local_maxima, label_cluster, stack, combine_test, unstack, monitor]
        #branch2 = [bc_read, stack, combine_test, unstack]
        branch2 = [bc_read, stack, unstack]
        branch3 = [blob_test, write]
        g.merge_branch(branch2, branch1, branch3)
    else:
        branch2 = [read, bc_read, local_maxima, label_cluster,
                   stack, combine_test, unstack, write]
        g.connect_branch(branch2)

if graph == 1:
    read = pm.get_task('read', path='res/HT2.tif')
    write = pm.get_task('write', filename='res/cluster2.tif')
    branch1 = [read, local_maxima, label_cluster, write]
    g.connect_branch(branch1)

if graph == 2:
    read = pm.get_task('read', path='res/HT2.tif')
    write = pm.get_task('write', filename='res/combine2.tif')
    branch1 = [read, local_maxima, label_cluster, stack, combine_test, unstack, write]
    g.connect_branch(branch1)

if graph == 3:
    read = pm.get_task('read', path='res/HT2.tif')
    read1 = pm.get_task('read', path='res/combine2.tif')
    write = pm.get_task('write', filename='res/blob2.tif')
    g.merge_branch([read, stack, unstack], [read1, stack2, unstack2], [blob_test, write])

# Run Ufo
sched = Ufo.Scheduler()
sched.props.enable_tracing = False #True

def timer_function():
    sched.run(g)

from timeit import Timer
tm = Timer('timer_function()', 'from __main__ import timer_function')
t = tm.timeit(1)
print t, 'sec'

