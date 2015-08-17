#!/usr/bin/env python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../piv'))
from testjob import TestJob

job = TestJob('piv-contrast')
t0 = job.run()

print "Running Test:", t0, "(s)"
