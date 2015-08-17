#!/usr/bin/env python
import sys, os
relpath = os.path.dirname(__file__)
sys.path.append(os.path.join(relpath, '../piv'))

from testjob import TestJob

job = TestJob('piv-contrast')
job.add_argument('--c1', type=float)
#job.parser.add_argument('--c1', type=float)

t0 = job.run()
print "use time:\t", t0
