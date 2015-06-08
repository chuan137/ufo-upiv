# -*- coding: utf-8 -*-
"""
Plot functions using matplotlib

@author: Chuan
"""
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import numpy as np
import sys
import json
import csv
from numpy import polyfit

def settings(ax, **kargs):
    for k,v in kargs.iteritems():
        method_name = 'set_' + k
        method = getattr(ax, method_name)
        if method:
            method(v)

def bar_plot_old(xpos, yheight, **kargs):
    plt.cla()
    ax = plt.gca()
    if 'xr' in kargs:
        ax.set_xlim(kargs['xr'])
    ax.bar(xpos, yheight)

def bar_plot(data, width=0.8, **kargs):
    plt.cla()
    ax = plt.gca()
    x, y = np.array(data).transpose()
    ax.bar(x, y, width, align='center')
    settings(ax, **kargs)

def errorbar_plot(data, **kargs):
    plt.cla()
    ax = plt.gca()
    x, y, yerr = np.array(data).transpose()
    ax.errorbar(x, y, yerr, fmt='o')
    settings(ax, **kargs)

def plot(data, style='bo', **kargs):
    plt.cla()
    ax = plt.gca()
    x, y = np.array(data).transpose()
    ax.plot(x, y, style)
    settings(ax, **kargs)

def plot(x, y, style='bo', **kargs):
    ax = plt.gca()
    ax.plot(x, y, style)
    settings(ax, **kargs)


def add_horizontal_span(ymin, ymax):
    ax = plt.gca()
    ax.axhspan(ymin, ymax, facecolor='0.5', alpha=0.5)

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def reset_axis():
    pylab.rcParams['figure.figsize'] = 11, 4 

def load_style(name, directory = './'):
    if sys.version_info[0] >= 3:
        s = json.load(open(directory + name))
    else:
        s = json.load(open(directory + name), object_hook=_decode_dict)
    plt.rcParams.update(s)
    np.set_printoptions(suppress=True)

def read_data(filename):
    data = []
    with open(filename, 'r') as f:
        c = csv.reader(f, delimiter=' ')
        for line in c:
            if line[0] is '#':
                continue
            data.append([float(x) for x in line if x != '']) 
    return data

def linearfit(data):
    try:
        x, y , r = np.array(data).transpose()
    except:
        x, y = np.array(data).transpose()
        r = None
    return polyfit(x, y, 1, w=r)


    
