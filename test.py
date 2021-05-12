import time
from geopy.distance import geodesic
import pandas as pd
import json

a = "01/17/2014 07:58:09"
print(time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(time.mktime(time.strptime("01/17/2014 07:58:11","%m/%d/%Y %H:%M:%S"))-time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(geodesic((36.048029,24.879575),(36.063658,24.885866)).m)

stay_data = pd.read_json("dataset/stay_periods.json")
for stayEvent in stay_data["stay_periods"]:
    for stay_period in stayEvent:
        # print(stay_period["stay_begin"])
        pass
    print(stayEvent)
