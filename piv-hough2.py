#!/usr/bin/env python
# useage:
#   ./piv-hough.py [config filename]
# default config file is config.py
import sys
import os
from python.pivjob import PivJob
import logging

logfile = '.hough.log'
logging.basicConfig(level=logging.DEBUG, filename=logfile, filemode='w', 
                    format='%(name)s %(levelname)s %(message)s')

try:
    cf = __import__(os.path.splitext(sys.argv[1])[0])
    parms = cf.parms
    config = cf.config
except:
    from config import parms, config

class PivJob(PivJob):
    def setup_tasks(self):
        self.setup_basic_tasks()
        p = self.parms
        sc = self.parms.scale

        self.add_task('crop', x=p.xshift, y=p.yshift, width=p.width, height=p.height)
        self.add_task('contrast', 'piv_contrast')
        self.add_task('rescale', factor=1.0/sc)
        self.add_task('input_fft', 'fft', dimensions=2)
        self.add_copy_task('bc_contrast') 

        self.add_task('ring_fft', 'fft', dimensions=2)
        self.add_task('ring_stack', 'stack', number=p.ring_number)
        self.add_task('ring_loop', 'loop', count=p.number)
        self.add_task('ring_convolution', 'complex_mult')
        self.add_task('ring_slice', 'slice')
        self.add_task('ring_pattern', 
                start=p.ring_start/sc, end=p.ring_end/sc, step=p.ring_step/sc, 
                thickness=p.ring_thickness/sc, method=p.ring_method, 
                width=p.width/sc, height=p.height/sc)

        self.add_task('ifft', dimensions=2)
        self.add_task('likelihood', 'hough-likelihood', 
                masksize=p.likelihoodmask, maskinnersize=p.likelihoodmaskinner)
        self.add_task('cand', 'candidate-sorting', 
                threshold=p.candi_threshold, ring_start=p.ring_start, 
                ring_step=p.ring_step, ring_end=p.ring_end )
        self.add_task('azimu', 'multi-search')

    def setup_graph(self, flag):
        if flag==0:
            b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'bc_contrast', 'input_fft')
            b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
            b3 = self.branch('ring_convolution', 'ifft', 'likelihood', 'cand', 'ring_writer')
            self.graph.merge_branch(b1, b2, b3)
        else:
            b1 = self.branch('read', 'crop', 'rescale', 'contrast', 'bc_contrast', 'input_fft')
            b2 = self.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
            b3 = self.branch('ring_convolution', 'ifft', 'likelihood', 'null') 
            self.graph.merge_branch(b1, b2, b3)


j = PivJob(parms)
j.profiling = config.get('profiling') or False
j.deviceCPU = config.get('deviceCPU') or False
j.run(config.get('graph'))
