#!/usr/bin/env python
import os
import sys
prj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, prj_root)

import argparse
import ConfigParser
from gi.repository import Ufo
from upiv.ufo_extension import TaskGraph, PluginManager
from upiv.ddict import DotDict

#{{{ read_parameters
def read_parameters():
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', nargs='?', default='SampleC')
    parser.add_argument('-p', '--profiling', action='store_true', default=False)
    args = parser.parse_args(sys.argv[1:])

    # config file
    config_file = os.path.join(prj_root, 'config', 'hough_%s.cfg' % args.dataset)
    cf_parser = ConfigParser.ConfigParser()

    # parse configuration file
    if cf_parser.read(config_file) != []:
        print "Configuration: ", config_file
        parms = {k: eval(v) for k,v in cf_parser.items('parms')}
        config = {k: eval(v) for k,v in cf_parser.items('config')}
    else:
        print "Unable to open configuration file", config_file
        sys.exit(-1)

    # overwrite config/parms with command line arguments
    if args.profiling:
        config['profiling'] = args.profiling

    return DotDict(parms), DotDict(config)
#}}}
#{{{ load_filters
def load_filters(parms):
    filters = DotDict({})
    scale = parms.scale
    parms.ring_number = (parms.ring_end - parms.ring_start) / parms.ring_step

    in_path = os.path.abspath(parms.in_path)

    out_imag = parms.get('output_img') or 'otuput/res.tif'
    out_imag = os.path.join(prj_root, out_imag)

    out_ring = parms.get('output_ring') or 'output/res.txt'
    out_ring = os.path.join(prj_root, out_ring)

    filters['write'] = {
        'property': {
            'filename': out_imag
        }
    }
    filters['ring_writer'] = {
        'property': {
            'filename': out_ring
        }
    }
    filters['read'] = {
        'property': {
            'path': in_path,
            'number': parms.number
        }
    }
    filters['crop'] = {
        'property': {
            'x': parms.xshift,
            'y': parms.yshift,
            'width': 1024,
            'height':1024
        }
    }
    filters['contrast'] = {
        'name': 'piv_contrast',
        'property': {
            'c1': parms.contrast_c1,
            'c2': parms.contrast_c2,
            'gamma': parms.contrast_gamma
        }
    }
    filters['rescale'] = {
        'property': { 'factor': 1.0/scale }
    }
    filters['input_fft'] = {
        'name': 'fft',
        'property': { 'dimensions' : 2 }
    }
    filters['ring_fft'] = {
        'name': 'fft',
        'property': { 'dimensions' : 2 }
    }
    filters['ring_stack'] = {
        'name': 'stack',
        'property': {'number': parms.ring_number}
    }
    filters['bc_image'] = {
        'name': 'broadcast'
    }
    filters['ring_loop'] = {
        'name': 'loop',
        'property': {'count': parms.number}
    }
    filters['ring_convolution'] = {
        'name': 'complex_mult'
    }
    filters['ring_slice'] = {
        'name': 'slice'
    }
    filters['ring_pattern'] = {
        'property': {
            'start': parms.ring_start/scale,
            'end': parms.ring_end/scale,
            'step': parms.ring_step/scale,
            'thickness': parms.ring_thickness/scale,
            'method': parms.ring_method,
            'width': parms.width/scale,
            'height': parms.height/scale
        }
    }
    filters['ifft'] = {
        'property': { 'dimensions': 2 }
    }
    filters['likelihood'] = {
        'name': 'hough-likelihood',
        'property': {
            'masksize': parms.likelihoodmask,
            'maskinnersize': parms.likelihoodmaskinner,
            'threshold': parms.thld_likely
        }
    }
    filters['candidate'] = {
        'name': 'candidate-filter',
        'property': {
            'ring_start': parms.ring_start,
            'ring_step': parms.ring_step,
            'ring_end': parms.ring_end,
            'scale': parms.scale
        }
    }
    filters['azimu'] = {
        'name': 'azimuthal-test',
        'property': {
            'thread': parms.threads,
            'azimu_thld': parms.thld_azimu,
            'likelihood_thld': parms.thld_likely,
        }
    }

    return filters
#}}}

def main():
    parms, config = read_parameters()
    filters = load_filters(parms)

    pm = PluginManager()
    g = TaskGraph()

    for k,v in filters.iteritems():
        name = v.get('name') or k
        prop = v.get('property') or {}
        if name is 'broadcast':
            g.tasks[k] = Ufo.CopyTask() 
        else:
            g.tasks[k] = pm.get_task(name)
            g.tasks[k].set_properties(**prop)

    b1 = g.branch('read', 'crop', 'contrast', 'bc_image', 'rescale', 'input_fft')
    b2 = g.branch('ring_pattern', 'ring_stack', 'ring_fft', 'ring_loop')
    b3 = g.branch('bc_image')
    b4 = g.branch('ring_convolution', 'ifft', 'likelihood', 'candidate')
    b5 = g.branch('azimu', 'ring_writer')

    g.merge_branch(b1, b2, b4)
    g.merge_branch(b3, b4, b5)

    sched = Ufo.FixedScheduler()
    sched.set_properties(enable_tracing=False)
    sched.run(g)


if __name__ == '__main__':
    main()
