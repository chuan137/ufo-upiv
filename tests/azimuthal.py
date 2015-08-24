#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))
from testjob import TestJob
from utils import relpath
import logging

TestJob.inpath = './inputs/input2.tif'
TestJob.canpath = './inputs/input2_can_series.tif'
TestJob.outfile = './output/azimu.tif'
logging.basicConfig(level=logging.DEBUG, filename='tests.log', filemode='w',
                    format='%(name)s %(levelname)s %(message)s')

class MyTestJob(TestJob):
    def setup_tasks(self):
        p = self.filter_parms
        self.add_task('read_img', 'read', path=self.inpath)
        self.add_task('read_cad', 'read', path=self.canpath)
        self.add_task('rescale', factor=0.5)
        self.add_task('write', filename='./output/azimu.tif')
        self.add_task('azimu', self.filter)
        self.add_task('loop', count=p.ring_number)
        self.add_task('m1', 'monitor')
        self.add_task('m2', 'monitor')
    def setup_graph(self):
        b1 =self.branch('read_img', 'rescale', 'm1')
        b2 =self.branch('read_cad', 'm2')
        b3 =self.branch('azimu', 'write')
        self.graph.merge_branch(b1, b2, b3)

parms = dict(
    ring_start = 10,
    ring_end = 20,
    ring_step = 2,
)
parms['ring_number'] = \
    (parms['ring_end'] - parms['ring_start']) / parms['ring_step'] + 1
print parms
 
j = MyTestJob('multi-search', **parms)
j.run()
