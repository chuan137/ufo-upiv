#!/usr/bin/env python
import sys
sys.path.append('..')

from piv.ufojob import UfoJob
from utils import parse_args

in_path, out_file = parse_args()

#number = 10
in_path = in_path or '../data/sampleB/'
out_file = out_file or './output/contrast.tif'

class UfoJob(UfoJob):
    def setup_tasks(self):
        p = self.parms
        self.add_task('read', path=in_path)#, number=number)
        self.add_task('write', filename=out_file)
        self.add_task('contrast', 'piv-contrast')
        #self.add_task('contrast')
    def setup_graph(self):
        b = self.branch('read', 'contrast', 'write')
        self.graph.connect_branch(b)

uj = UfoJob()
uj.setup_tasks()
uj.setup_graph()

t = uj.run_t()
print t
