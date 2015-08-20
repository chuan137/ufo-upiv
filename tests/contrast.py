#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))

from testjob import TestJob
from utils import relpath
import logging

TestJob.inpath = relpath('../data/sampleB')
TestJob.outfile = relpath('./output/contrast.tif')
logging.basicConfig(level=logging.DEBUG,
                    filename='tests.log', filemode='w',
                    format='%(name)s %(levelname)s %(message)s')

job = TestJob('piv-contrast')

job.profiling = False
job.deviceCPU = True
job.parser.add_argument('--c1', type=float, default=-0.5)
job.parser.add_argument('--c2', type=float, default=10.0)
job.parser.add_argument('--c3', type=float, default=3.0)
job.parser.add_argument('--c4', type=float, default=1.5)

t0 = job.run()
print "Running Test:", t0, "(s)"

