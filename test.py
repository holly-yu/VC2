import time
from geopy.distance import geodesic
import numpy as np
import pandas as pd
import json

a = "01/17/2014 07:58:09"
print(time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(time.mktime(time.strptime("01/17/2014 07:58:11","%m/%d/%Y %H:%M:%S"))-time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(geodesic((36.048029,24.879575),(36.063658,24.885866)).m)

# stay_data = pd.read_json("dataset/stay_periods.json")
# for stayEvent in stay_data["stay_periods"]:
#     for stay_period in stayEvent:
#         # print(stay_period["stay_begin"])
#         pass
#     print(stayEvent)

store_position = pd.read_csv("dataset/store_position.csv")
print(store_position)
lat = store_position[store_position.store == "Roberts and Sons"]["lat"]
long = store_position[store_position.store == "Roberts and Sons"]["long"]
print(lat,long)
if pd.isnull(lat).bool() and pd.isnull(long).bool():
    print("aaaaa")
else:
    print("bbbbb")
# cc_data = pd.read_csv("dataset/cc_data.csv")
# for cdata in cc_data.iterrows():
#     print(cdata[1].location)