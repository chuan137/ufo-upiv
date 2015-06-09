#!/usr/bin/env python
from gi.repository import Ufo
from ufo_extension import TaskGraph, PluginManager

pm = PluginManager()

g = TaskGraph()

read = pm.get_task('read', path='res/HT2.tif')
write = pm.get_task('write', filename='res/res.tif')
null = pm.get_task('null')

monitor1 = pm.get_task('monitor')
monitor2 = pm.get_task('monitor')
stack = pm.get_task('stack', number=2)
unstack = pm.get_task('slice')

g.connect_branch([read, stack, monitor1, unstack, monitor2, null])
#g.connect_branch([read, stack, monitor2, null])

# Run Ufo
sched = Ufo.FixedScheduler()
sched.props.enable_tracing = False #True

def timer_function():
    sched.run(g)

from timeit import Timer
tm = Timer('timer_function()', 'from __main__ import timer_function')
t = tm.timeit(1)
print t, 'sec'

