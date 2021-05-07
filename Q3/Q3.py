import json
import csv
import pandas as pd
import numpy as np
import time
import math
from geopy.distance import geodesic



stay_data = pd.read_json("../dataset/stay_periods.json")
print(stay_data)

cc_data = pd.read_csv("../dataset/cc_data.csv")
cc_data_group = cc_data.sort_values(by=["last4ccnum","timestamp"]).groupby(by="last4ccnum")
Correlation_cc_columns = []
for name,data in cc_data_group:
    print(name,data)
    Correlation_cc_columns.append(name)



loyalty_data = pd.read_csv("../dataset/loyalty_data.csv")
loyalty_data_group = loyalty_data.sort_values(by=["loyaltynum","timestamp"]).groupby(by="loyaltynum")
Correlation_loy_columns = []
for name,data in loyalty_data_group:
    print(name,data)
    Correlation_loy_columns.append(name)

sigma = 10
Correlation_cc = pd.DataFrame(index=list(stay_data.id), columns=Correlation_cc_columns)
Correlation_loy = pd.DataFrame(index=list(stay_data.id), columns=Correlation_loy_columns)
print(Correlation_cc.columns)
print(Correlation_loy.columns)

# 求时间相似度
def timeCorr(stayEvent, consumeEvent):
    stay_begin = time.mktime(time.strptime(stayEvent.stay_begin,"%m/%d/%Y %H:%M:%S"))
    stay_end = time.mktime(time.strptime(stayEvent.stay_end,"%m/%d/%Y %H:%M:%S"))
    time_consume = time.mktime(time.strptime(consumeEvent.timestamp,"%m/%d/%Y %H:%M:%S"))

    if time_consume >= stay_begin and time_consume <= stay_end:
        return 1
    elif time_consume < stay_begin:
        return math.exp(stay_begin - time_consume)
    else:
        return math.exp(stay_end - time_consume)

# gaussian求空间相似度
def spaceCorr (stayEvent, consumeEvent, sigma):
    distance = geodesic((stayEvent.lat,stayEvent.long),(consumeEvent.lat, consumeEvent.long)).m
    return math.exp(- distance**2 / 2 * sigma**2)

def correlation(stayEvent, consumeEvent):
    return timeCorr(stayEvent,consumeEvent) * spaceCorr(stayEvent, consumeEvent, sigma)

# 求相似度矩阵
def AveCorrelation_cc():
    pass