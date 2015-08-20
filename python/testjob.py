#!/usr/bin/env python
from ufojob import UfoJob
from ddict import DotDict
import argparse
import sys, os
from inspect import stack
from utils import relpath, LogMixin

default_inpath  = relpath('../data/sampleB')
default_outfile = relpath('../data/res.tif')

class TestJob(UfoJob, LogMixin):
    inpath = default_inpath
    outfile = default_outfile

    def __init__(self, filtername, **parms):
        super(TestJob, self).__init__(profiling=False, schedfixed=True, deviceCPU=False)

        self.filter = filtername
        self.filter_parms = parms

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-i', '--inpath')
        self.parser.add_argument('-o', '--outfile')
        self.parser.add_argument('-n', '--number', type=int)
        self.parser.add_argument('-p', '--profiling', action='store_true', default=None)
        self.parser.add_argument('-c', '--cpu', action='store_true', default=False)
        self.args, self.extra_args = self.parser.parse_known_args()
        self.logger.debug(self.args)
        self.logger.debug("extra arguments: %s" % self.extra_args)

    def setup_tasks(self):
        self.logger.debug("parameters for filters: %s" % self.filter_parms)
        self.add_task('read', path=self.inpath, number=self.number)
        self.add_task('write', filename=self.outfile)
        self.add_task(self.filter, **self.filter_parms)

    def setup_graph(self):
        self.branch('read', self.filter, 'write')

    def process_args(self):
        self.inpath = self.args.inpath or self.inpath
        self.outfile = self.args.outfile or self.outfile
        self.number = self.args.number or 100
        self._profiling = self.args.profiling or self._profiling
        self._deviceCPU = self.args.cpu or self._deviceCPU

        for k,v in vars(self.parser.parse_args(self.extra_args)).iteritems():
            if k not in ['inpath', 'outfile', 'number', 'profiling', 'cpu'] and v is not None:
                self.filter_parms[k] = v

    def add_argument(self, *argc, **argv):
        self.parser.add_argument(*argc, **argv)

    def run(self):
        self.process_args()
        self.setup_tasks()
        self.setup_graph()
        return self.run_t()


