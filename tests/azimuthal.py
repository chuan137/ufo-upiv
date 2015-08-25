#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))
from testjob import TestJob
from utils import relpath
import logging

TestJob.inpath = './inputs/input2.tif'
TestJob.canpath = './inputs/input2_can.tif'
TestJob.outfile = './output/azimu.tif'
logging.basicConfig(level=logging.DEBUG, filename='tests.log', filemode='w',
                    format='%(name)s %(levelname)s %(message)s')

class MyTestJob(TestJob):
    def setup_tasks(self):
        p = self.filter_parms
        self.add_task('read_cad', 'read', path=self.canpath)
        self.add_task('candi', 'candidate-sorting')
        self.add_task('read_img', 'read', path=self.inpath)
        self.add_task('rescale', factor=0.5)
        self.add_task('azimu', self.filter, **self.filter_parms)
        self.add_task('write', filename='./output/azimu.tif')
        self.add_task('m1', 'monitor')
        self.add_task('m2', 'monitor')
    def setup_graph(self):
        b1 =self.branch('read_img', 'rescale', 'm1')
        b2 =self.branch('read_cad', 'candi', 'm2')
        b3 =self.branch('azimu', 'write')
        self.graph.merge_branch(b1, b2, b3)

j = MyTestJob('multi-search')
j.run()
