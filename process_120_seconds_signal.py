from wfdb import io
import numpy as np
from process_10_seconds_signal import ecg_10
import matplotlib.pyplot as plt
import math

class ecg_120:
    def __init__(self, path, plot=False, verbose=False, qtc_filter=False):
        self.path=path
        self.segments=None
        self.plot=plot
        self.verbose=verbose
        self.__setSegments(qtc_filter)
    def __setSegments(self, qtc_filter):
        if self.segments!=None:
            return self.segments
        if self.segments==None:
            self.segments=[]
        for i in range(12):
            sig, fields = io.rdsamp(self.path,channels=[10], sampfrom = 10000*i, sampto=10000*(i+1)-1)
            current_ecg = ecg_10(sig, fields['fs'], qtc_filter=qtc_filter)
            current_segment=dict()
            new_sig = current_ecg.filteredSignal
            R_points=current_ecg.R_points
            Q_points=current_ecg.Q_points
            S_points=current_ecg.S_points
            T_points=current_ecg.T_points
            indexes=current_ecg.indexes
            current_segment["Q"]=Q_points
            current_segment["R"]=R_points
            current_segment["S"]=S_points
            current_segment["T"]=T_points
            current_segment["i"]=indexes
            assert len(R_points)==len(Q_points) and len(R_points)==len(S_points) and len(R_points)==len(T_points) and len(R_points)==len(indexes)
            self.segments.append(current_segment)
            if self.verbose==True:
                print(current_segment["Q"])
                print(current_segment["R"])
                print(current_segment["S"])
                print(current_segment["T"])
            if self.plot==True and i==0:
                plt.figure(figsize=(10,10))
                plt.plot(new_sig,color='red')
                for r in R_points:
                    plt.annotate("R",xy=(r,new_sig[r]))
                for q in Q_points:
                    plt.annotate("Q",xy=(q,new_sig[q]))
                for s in S_points:
                    plt.annotate("S",xy=(s,new_sig[s]))
                for t in T_points:
                    plt.annotate("T",xy=(t,new_sig[t]))
                plt.show()