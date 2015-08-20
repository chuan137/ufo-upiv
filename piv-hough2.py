#!/usr/bin/env python
from gi.repository import Ufo
from python.pivjob import PivJob
from python.ddict import DotDict
import logging

logging.basicConfig(level=logging.DEBUG, filename='logs/hough2.log', 
                    filemode='w', format='%(name)s %(levelname)s %(message)s')
in_path     = 'data/sampleB'
number      = 10

parms = dict(in_path=in_path, number=number, 
             out_file='data/res_small.tif',
             scale=1, ring_start=2, ring_end=10, ring_thickness=3,
             maxima_sigma=3, blob_alpha=0.8 )
j = PivJob(parms)
j.profiling = False
#j.run()

parms = dict(in_path=in_path, number=number, 
             out_file='data/res_large.tif',
             scale=2, ring_start=8, ring_end=50, ring_thickness=5,
             maxima_sigma=1.5, blob_alpha=0.2 )
j2 = PivJob(parms)
j2.profiling = False
j2.deviceCPU = False
j2.run()
