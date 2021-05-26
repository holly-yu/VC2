import time
from geopy.distance import geodesic
import numpy as np
import pandas as pd
import json
from question3 import correlation

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

arr = [[0.0011666808772604466, 0.0004965526296126486, 0.005169046776169545, 2.571846013084293e-06, 0.0003756854160028145, 0.0025846655739753524, 0.003322958764272688, 1.341255206328965e-55, 1.1141007632855123e-07, 4.6234105393986e-19, 0.00465214209855259, 0.0005805499531781946, 0.00222079504612295, 0.0006586691467949749, 2.5547718215789787e-55, 3.1434700134515235e-05, 0.0006126262995866602, 0.004541115863321867, 2.464902319525415e-25, 0.0010883533146025621, 0.0010652304556356283, 0.00036226794502264916, 0.0008170178145052595, 0.0009204870681976074, 1.9697826644838207e-07, 0.002836214781103691, 0.0007857788658618266, 0.007004804538498362, 2.7642863727138417e-06, 0.000894004496178592, 0.0005897558765067121, 0.00982170484474079, 1.6487027460029266e-05, 0.0007525370012764728, 0.000907418447393001, 0.0042657033864757325, 8.228600293015566e-11, 0.002650036600674546, 0.0005366933915684368, 0.00048504119952099984, 0.0042310911224072946, 0.0008749193751793709, 0.005173904707527593, 0.0008750107926396851, 0.0, 4.47085068776321e-55, 3.1987539651241126e-07, 8.5300105736643e-07, 0.0007806553096190381, 0.002909071985331262, 2.464902319525415e-25, 0.0005155523449151682, 0.006202514885266061, 0.001002180250529699, 4.4708506877632065e-55]]
np.savetxt('../dataset/test.txt',arr, delimiter=',')