#!/usr/bin/env python
from gi.repository import Ufo
import numpy as np
import tifffile
import threading
import time

# Settings

pm = Ufo.PluginManager()

ring_pattern = pm.get_task('ring_pattern')
write = pm.get_task('write')
null = pm.get_task('null')

ring_pattern.set_properties(ring_start=4, ring_end=40, ring_step=2,
                            ring_thickness=6, width=1024, height=1024)
write.set_properties(filename='./ring_pattern/ring.tif')


###
### code start here
###


# set up graph
g = Ufo.TaskGraph()
g.connect_nodes(ring_pattern, write)

# run scheduler 
sched = Ufo.Scheduler()
sched.run(g)

