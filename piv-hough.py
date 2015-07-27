#!/usr/bin/env python
from gi.repository import Ufo
from piv.pivjob import PivJob

parms = dict( # default parameters
    scale = 2,
    img_path = 'data/input/sampleC-0050-contrast.tif',
    out_file = 'data/res/HT.tif',
    ring_start = 6,
    ring_end = 40,
    device = 'GPU',     # CPU/GPU
    profiling = False   # True/False
    )

piv = PivJob(parms) # initialze piv job
piv.setup_graph() # setup piv graph
piv.setup_schedule()

t = piv.run_t() # Run piv with timer
print t, 'sec'
