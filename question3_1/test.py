import time
from geopy.distance import geodesic
import numpy as np
import pandas as pd
import json
# from question3 import correlation

a = "01/16/2014 07:58:11"
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

# store_position = pd.read_csv("dataset/store_position.csv")
# print(store_position)
# lat = store_position[store_position.store == "Roberts and Sons"]["lat"]
# long = store_position[store_position.store == "Roberts and Sons"]["long"]
# print(lat,long)
# if pd.isnull(lat).bool() and pd.isnull(long).bool():
#     print("aaaaa")
# else:
#     print("bbbbb")


# cc_data = pd.read_csv("dataset/cc_data.csv")
# for cdata in cc_data.iterrows():
#     print(cdata[1].location)
matrix = [[1, 2, 3], [4, 5, 6]]
df = pd.DataFrame(data=matrix, index=['1','2'],columns=['a','b','c'])
# for i in df.index:
#     for j in df.columns:
#         print(df.loc[i,j])

g = lambda a: a > 3

# date = "01/06/2014 07:22:04"
# date1 = "01/06/2014 00:00:00"
# print(time.mktime(time.strptime(date, "%m/%d/%Y %H:%M:%S")))
# print(time.mktime(time.strptime(date1, "%m/%d/%Y %H:%M:%S")))

# array = [0,1,3,2,3,3]
# max = np.max(array)
# print(array.index(max))

a = ['a','b','c']
b = ['c','b','d']
c = []
# print(list(set(a).intersection(set(b))))
# print((list(set(a).union(set(b)))))
# print(1/22)
# if c:
#     print(1)
# else:
#     print(2)
cc_data = pd.read_csv("../dataset/cc_data.csv")

print(list(cc_data.timestamp))
# print(cc_data[((cc_data.last4ccnum == 7108) & (cc_data.timestamp == "01/06/2014 07:34"))])
