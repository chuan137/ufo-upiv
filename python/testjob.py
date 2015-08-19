#!/usr/bin/env python
from ufojob import UfoJob
from ddict import DotDict
import argparse
import sys, os
from inspect import stack

realdir = os.path.split(os.path.realpath(__file__))[0]

class TestJob(UfoJob):
    _default_parms = dict (
            sched = 'Fixed',
            profiling = False,
            inpath = os.path.join(realdir, '../data/sampleB'),
            outfile = os.path.join(realdir, '../data/res.tif'))

    def __init__(self, filtername, parms={}, **kargs):
        if 'outfile' in kargs:
            callerpath = os.path.dirname(stack()[-1][1])
            kargs['outfile'] = os.path.relpath(os.path.join(callerpath, kargs['outfile']))
        parms.update(kargs)
        super(TestJob, self).__init__(parms)

        self.filter = filtername
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-i', '--inpath')
        self.parser.add_argument('-o', '--outfile')
        self.parser.add_argument('-n', '--number', type=int)
        self.parser.add_argument('-p', '--profiling', action='store_true', default=False)

    def setup_tasks(self):
        if self.args.number:
            self.add_task('read', path=self.args.inpath, number=self.args.number)
        else:
            self.add_task('read', path=self.args.inpath)
        self.add_task('write', filename=self.args.outfile)
        self.add_task(self.filter, **self.filterargs)

    def setup_graph(self):
        self.branch('read', self.filter, 'write')

    def parse_args(self):
        self.args = self.parser.parse_args()

        if self.args.inpath is None:
            self.args.inpath = self.parms.inpath
        if self.args.outfile is None:
            self.args.outfile = self.parms.outfile

        self.filterargs = {}
        for k,v in self.args.__dict__.iteritems():
            if k not in ['inpath', 'outfile', 'number', 'profiling'] and v is not None:
                self.filterargs[k] = v
<<<<<<< HEAD
        #print self.args
        #print self.filterargs
=======

        print self.args
        print self.filterargs
>>>>>>> 1dd2e4e... TEST ADDED

    def add_argument(self, *argc, **argv):
        self.parser.add_argument(*argc, **argv)

    def run(self):
        self.parse_args()
        self.setup_tasks()
        self.setup_graph()
        return self.run_t(self.args.profiling)


