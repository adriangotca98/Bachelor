import extract_OK_records
import random
import os

def choose():
    chosenSubjects=[]
    healthySubjects = extract_OK_records.computeSubjects()
    while len(chosenSubjects)<10:
        idx = random.randint(0,len(healthySubjects.items())-1)
        chosenSubjects.append(os.path.join(list(healthySubjects.keys())[idx],list(healthySubjects.items())[idx][1]))
        healthySubjects.pop(list(healthySubjects.items())[idx][0])
    return chosenSubjects
