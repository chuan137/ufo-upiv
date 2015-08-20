#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))

from testjob import TestJob
from utils import relpath
import logging

TestJob.inpath = relpath('../data/sampleC')
TestJob.outfile = relpath('./output/denoise.tif')
logging.basicConfig(level=logging.DEBUG, filename='tests.log', filemode='w',
                    format='%(name)s %(levelname)s %(message)s')

job = TestJob('denoise')
job.profiling = False
job.deviceCPU = False

t0 = job.run()
print "Running Test:", t0, "(s)"

