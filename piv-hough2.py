#!/usr/bin/env python
from python.pivjob import PivJob
import logging
logfile = '.hough.log'
logging.basicConfig(level=logging.DEBUG, filename=logfile, filemode='w', 
                    format='%(name)s %(levelname)s %(message)s')

try:
    cf = __import__(sys.argv[1])
    parms = cf.parms
    config = cf.config
except:
    from config import parms, config

j = PivJob(parms)
j.profiling = config.get('profiling') or False
j.deviceCPU = config.get('deviceCPU') or False
j.run(config.get('graph'))
