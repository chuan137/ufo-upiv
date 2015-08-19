#!/usr/bin/env python

from gi.repository import Ufo

manager = Ufo.PluginManager()
graph = Ufo.TaskGraph()
scheduler = Ufo.Scheduler()

reader = manager.get_task('read')
writer = manager.get_task('write')
#contrast = manager.get_task('rescale')
contrast = manager.get_task('denoise')
monitor = manager.get_task('monitor')

reader.set_properties(path='./data/sampleB')
writer.set_properties(filename='res.tif')

graph.connect_nodes(reader, contrast)
graph.connect_nodes(contrast, monitor)
graph.connect_nodes(monitor, writer)
scheduler.run(graph)
