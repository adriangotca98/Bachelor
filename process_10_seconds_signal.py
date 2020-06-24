from wfdb import processing
from scipy import signal
import numpy as np
import math

eps = 10**-4
class ecg_10:
    def __init__(self, sig, fs, qtc_filter=False):
        self.signal = sig
        self.filteredSignal = None
        self.fs=fs
        self.Q_points=None
        self.R_points=None
        self.S_points=None
        self.T_points=None
        self.indexes=None
        self.derivativeSignal=None
        self.__compute_R_points()
        self.__compute_Q_points()
        self.__compute_S_points()
        self.__compute_T_points()
        self.__compute_signal_derivative()
        self.__delete_extra_points()
        if qtc_filter==True:
            self.__delete_wrong_points()
        
    def __butter_lowpass(self, cutoff, nyq_freq, order=2):
        normal_cutoff = float(cutoff) / nyq_freq
        b, a = signal.butter(order, normal_cutoff, btype='lowpass')
        return b, a

    def __butter_lowpass_filter(self, cutoff_freq, order=2):
        b, a = self.__butter_lowpass(cutoff_freq, self.fs/2, order=order)
        y = signal.filtfilt(b, a, self.signal[:,0])
        return y

    def __compute_signal_derivative(self):
        if self.derivativeSignal is None:
            x = np.linspace(0,self.fs,len(self.filteredSignal))
            self.derivativeSignal = np.zeros(self.filteredSignal.shape,np.float)
            self.derivativeSignal[0:-1] = np.diff(self.filteredSignal)/np.diff(x)
            self.derivativeSignal[-1] = (self.filteredSignal[-1] - self.filteredSignal[-2])/(x[-1] - x[-2])
    
    def __compute_R_points(self):
        if self.R_points is None:
            self.R_points = processing.xqrs_detect(self.signal[:,0],self.fs,verbose=False).tolist()
            self.indexes = [i for i in range(len(self.R_points))]
            if self.filteredSignal==None:
                self.filteredSignal = self.__butter_lowpass_filter(10)
            if self.derivativeSignal==None:
                self.__compute_signal_derivative()
            for i in range(len(self.R_points)):
                while abs(self.derivativeSignal[self.R_points[i]]<=eps):
                    self.R_points[i]-=1

    def __compute_Q_points(self):
        if self.Q_points is None:
            if self.R_points is None:
                self.__compute_R_points()
            self.Q_points=[]
            for r in self.R_points:
                q = 0
                for j in range(100,1,-1):
                    if self.derivativeSignal[r-j]<=eps:
                        q = r-j
                self.Q_points.append(q)

    def __compute_S_points(self):
        if self.S_points is None:
            if self.R_points==None:
                self.__compute_R_points()
            self.S_points=[]
            for r in self.R_points:
                for i in range(1,100,1):
                    if r+i>=9999:
                        break
                    if self.derivativeSignal[r+i]>0 and self.derivativeSignal[r+i-1]<0:
                        self.S_points.append(r+i)
                        break
    
    def __compute_T_points(self):
        if self.T_points is None:
            if self.R_points is None:
                self.__compute_R_points()
            self.T_points=[]
            for r in self.R_points:
                for i in range(101,400,1):
                    if (r+i>=len(self.derivativeSignal)):
                        break
                    if self.derivativeSignal[r+i]<0 and self.derivativeSignal[r+i-1]>0:
                        self.T_points.append(r+i)
                        break

    def __delete_extra_points(self):
        len_all = min(min(min(len(self.S_points), len(self.Q_points)), len(self.R_points)),len(self.T_points))
        while len(self.S_points)!=len_all:
            self.S_points.pop(-1)
        while len(self.Q_points)!=len_all:
            self.Q_points.pop(-1)
        while len(self.R_points)!=len_all:
            self.R_points.pop(-1)
        while len(self.T_points)!=len_all:
            self.T_points.pop(-1)
        while len(self.indexes)!=len_all:
            self.indexes.pop(-1)
    
    def __delete_wrong_points(self):
        if len(self.R_points)==0:
            return
        points_to_delete=[]
        for index in range(len(self.R_points)-1):
            RR = self.R_points[index+1]-self.R_points[index]
            QT = self.T_points[index]-self.Q_points[index]
            if (QT/math.sqrt(RR/1000)>400 or QT/math.sqrt(RR/1000)<200):
                points_to_delete.append(index)
        points_to_delete.append(len(self.R_points)-1)
        offset=0
        for index in points_to_delete:
            self.R_points.pop(index-offset)
            self.S_points.pop(index-offset)
            self.T_points.pop(index-offset)
            self.Q_points.pop(index-offset)
            self.indexes.pop(index-offset)
            offset+=1
