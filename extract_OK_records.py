import os
import pathlib
import wfdb
from process_10_seconds_signal import ecg_10

def computeSubjects():
    subjects=dict()
    folderPath = pathlib.Path(os.getcwd())
    databasePath = os.path.join(folderPath.parent,os.listdir(folderPath.parent)[0])
    for patient in os.listdir(databasePath):
        patientPath = os.path.join(databasePath,patient)
        if os.path.isdir(patientPath)==False:
            continue
        for filename in os.listdir(patientPath):
            if filename.endswith('.hea'):
                fullPath = os.path.join(patientPath,filename)
                file=open(fullPath,mode='r')
                text=file.read()
                file.close()
                tokens=[]
                for bigger in text.split('\n'):
                    for token in bigger.split(' '):
                        tokens.append(token)
                if text.find('# Reason for admission: Healthy control')!=-1:
                    if int(tokens[3])>=120000:
                        fullPathToPatient = fullPath.rsplit('.',1)[0]
                        signal = wfdb.io.rdsamp(fullPathToPatient, sampto=10000, channels=[10])[0]
                        ecg = ecg_10(signal, 1000)
                        if len(ecg.R_points)>0:
                            subjects[patientPath]=filename.split('.')[0]
            
    return subjects