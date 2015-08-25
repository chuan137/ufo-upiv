#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../python'))
from testjob import TestJob
from utils import relpath
import logging

TestJob.inpath = relpath('./inputs/hough_votes.tif')
TestJob.outfile = relpath('./output/liklihood.tif')
logging.basicConfig(level=logging.DEBUG, filename='.tests.log', filemode='a',
                    format='%(name)s %(levelname)s %(message)s')

job = TestJob('hough-liklihood')
job.profiling = False
job.deviceCPU = False
job.schedfixed = True
job.parser.add_argument('-k', '--masksize', type=int, default=7)
job.parser.add_argument('-z', '--maskinnersize', type=float, default=1.5)

t0 = job.run()
print "Running Test:", t0, "(s)"

