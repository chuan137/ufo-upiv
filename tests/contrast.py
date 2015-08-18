#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../piv'))
from testjob import TestJob

job = TestJob('piv-contrast', outfile='./output/contrast.tif')
job.add_argument('--c1', type=float, default=-0.5)
job.add_argument('--c2', type=float, default=10.0)
job.add_argument('--c3', type=float, default=3.0)
job.add_argument('--c4', type=float, default=1.5)
job.add_argument('--gamma', type=float, default=0.3)
t0 = job.run()

print "Running Test:", t0, "(s)"
