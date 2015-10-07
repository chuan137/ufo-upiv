#!/usr/bin/env python
import numpy as np
from scipy.optimize import curve_fit

class Fit (object):
    def __init__(self,method='gaussian'):
        self.method = method
        self._x = None
        self._y = None
        self._f = None
        self._dim = 0
    def func(self,*v):
        return self._f(*v)
    def fit(self,*val,**kwargs):
        try:
            self.y=kwargs['y']
            if self.x:
                self.x=arange(len(y))
        except:
            pass
        try:
            self.x=kwargs['x']
        except:
            pass
        v0 = val
        best_val,covar = curve_fit(self._f,self.x,self.y, p0=v0)
        self._val = best_val
        self._covar = covar
        return np.array(zip(best_val, np.diag(covar)))

    @property
    def dim(self):
        return self._dim
    @dim.setter
    def dim(self, n):
        self._dim = n

    @property
    def f(self):
        return _f
    @f.setter
    def f(self, func):
        self._f = func

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, data):
        self._x = data
    
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, data):
        self._y = data

    @property
    def bestval(self):
        return _val
    @property
    def cover(self):
        return _covar

def gaussian(x,a,b,c):
    return a * np.exp(-(x-b)**2/2./c**2)
def constant(x,a):
    return a

def main():
    xdata = np.array([0.0,1.0,2.0,3.0,4.0,5.0])
    ydata = np.array([0.1,0.9,2.2,2.8,3.9,5.1])
    def func(x,a,b,c):
        return a + b*x + c*x*x;
    fit = Fit()
    fit.f = func
    fit.x = xdata
    fit.y = ydata
    print fit.dofit(1,2,3)

if __name__ == '__main__':
    main()
