import time
from geopy.distance import geodesic
import json

a = "01/17/2014 07:58:09"
print(time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(time.mktime(time.strptime("01/17/2014 07:58:11","%m/%d/%Y %H:%M:%S"))-time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(time.mktime(time.strptime(a,"%m/%d/%Y %H:%M:%S")))
print(geodesic((36.048029,24.879575),(36.063658,24.885866)).m)

with open("test.json","r") as f:
    data = f.read()

print(type(json.loads(data)))