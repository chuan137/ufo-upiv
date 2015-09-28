import pylab as plb
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp

x = ar(range(10))
y = ar([0,1,2,3,4,5,4,3,2,1])
y0 = ar([745.02502, 832.93750, 893.60297, 855.30359, 777.93054, 667.60297, 566.73865, 486.15909, 436.23810, 409.27679])
y1 = ar([792.75000, 742.15002, 750.22498, 820.35419, 871.47058, 850.30359, 774.02777, 674.44116, 564.26135, 489.44318])
y2 = ar([733.39288, 612.27502, 712.65002, 853.62500, 935.22058, 902.67859, 785.72223, 666.89703, 557.96588, 476.65909])

y1 = y1[2:]
y2 = y2[2:]
y = y1

n = len(y)                          #the number of data
x = ar(range(n))
mean = 5                   #note this correction
sigma = 2        #note this correction

def gaus(x,a,x0,sigma):
    return a*exp(-(x-x0)**2/(2*sigma**2))

popt,pcov = curve_fit(gaus,x,y,p0=[max(y),mean,sigma])

print popt

plt.plot(x,y,'b+:',label='data')
plt.plot(ar(range(len(y1))), y1)
plt.plot(ar(range(len(y2))), y2)
plt.plot(x,gaus(x,*popt),'ro:',label='fit')
plt.legend()
plt.title('Fig. 3 - Fit for Time Constant')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.show() 
