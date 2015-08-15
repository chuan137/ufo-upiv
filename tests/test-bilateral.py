#!/usr/bin/env python
import sys
sys.path.append('..')

from piv.ufojob import UfoJob
from utils import parse_args

in_path, out_file = parse_args()

number   = 1
in_path  = in_path or './inputs'
out_file = out_file or './output/bilateral.tif'

print 'Input image is ', in_path
print 'Output path is ', out_file

class UfoJob(UfoJob):
    def setup_tasks(self):
        p = self.parms
        self.add_task('read', path=in_path, number = number)
        self.add_task('write', filename=out_file)
        self.add_task('bilateral')
    def setup_graph(self):
        b = self.branch('read', 'bilateral', 'write')
        self.graph.connect_branch(b)

uj = UfoJob()
uj.setup_tasks()
uj.setup_graph()

uj.run_t()
