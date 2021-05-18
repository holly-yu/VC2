import json
import csv
import pandas as pd
import numpy as np
import time
import math
from geopy.distance import geodesic



stay_data = pd.read_json("../dataset/stay_periods.json")
# print(stay_data)

# cc卡对应的关系矩阵
cc_data = pd.read_csv("../dataset/cc_data.csv")
cc_data = cc_data.sort_values(by=["last4ccnum","timestamp"])
Correlation_cc_columns = list(set(cc_data.last4ccnum))
Correlation_cc_columns.sort()
cc_events = []
for last4ccnum in Correlation_cc_columns:
    cc_events.append(cc_data[cc_data.last4ccnum == last4ccnum])



# loyalty卡对应的关系矩阵
loyalty_data = pd.read_csv("../dataset/loyalty_data.csv")
loyalty_data = loyalty_data.sort_values(by=["loyaltynum","timestamp"])
Correlation_loy_columns = list(set(loyalty_data.loyaltynum))
Correlation_loy_columns.sort()
loy_events = []
for loyaltynum in Correlation_loy_columns:
    loy_events.append(loyalty_data[loyalty_data.loyaltynum == loyaltynum])


sigma = 10
Correlation_cc = pd.DataFrame(index=list(stay_data.id), columns=Correlation_cc_columns)
Correlation_loy = pd.DataFrame(index=list(stay_data.id), columns=Correlation_loy_columns)
# print(Correlation_cc.index)
# print(Correlation_loy.columns)

# 商店名和经纬度对应的数据，有一些缺失数据
store_position = pd.read_csv("../dataset/store_position.csv").dropna()
print(store_position)

# 求时间相似度
def timeCorr(stayEvent, consumeEvent):
    stay_begin = time.mktime(time.strptime(stayEvent["stay_begin"],"%m/%d/%Y %H:%M:%S"))
    stay_end = time.mktime(time.strptime(stayEvent["stay_end"],"%m/%d/%Y %H:%M:%S"))
    time_consume = time.mktime(time.strptime(consumeEvent.timestamp,"%m/%d/%Y %H:%M"))

    if time_consume >= stay_begin and time_consume <= stay_end:
        return 1
    elif time_consume < stay_begin:
        return math.exp(stay_begin - time_consume)
    else:
        return math.exp(stay_end - time_consume)

# gaussian求空间相似度
def spaceCorr (stayEvent, consumeEvent, sigma):
    lat = store_position[store_position.store == consumeEvent.location]["lat"]
    long = store_position[store_position.store == consumeEvent.location]["long"]
    if pd.isnull(lat).bool() and pd.isnull(long).bool():
        return -1
    distance = geodesic((stayEvent["lat"],stayEvent["long"]),(float(lat), float(long))).m
    return math.exp(- distance**2 / 2 * sigma**2)

# 求时空相似度
def correlation(stayEvent, consumeEvent):
    if spaceCorr(stayEvent, consumeEvent, sigma) == -1:
        return -1
    return timeCorr(stayEvent,consumeEvent) * spaceCorr(stayEvent, consumeEvent, sigma)

# 求相似度矩阵
def AveCorrelation():
    for stayEvents in stay_data["stay_periods"]:
        totalCorr = 0
        consumeEventNum = 0
        for stay_period in stayEvents:
            for cc_num in cc_events:
                for consumeEvent in cc_num.iterrows():
                    if correlation(stay_period, consumeEvent[1]) != -1:
                        totalCorr += correlation(stay_period, consumeEvent[1])
                        consumeEventNum += 1
        Correlation_cc.append(totalCorr / len(stay_period) * consumeEventNum)

    # for stayEvent in stay_data["stay_periods"]:
    #     totalCorr = 0
    #     consumeEventNum = 0
    #     for stay_period in stayEvents:
    #         for loy_num in loy_events:
    #             for consumeEvent in loy_num.iterrows():
    #                 if correlation(stay_period, consumeEvent[1]) != -1:
    #                     totalCorr += correlation(stay_period, consumeEvent[1])
    #                     consumeEventNum += 1
    #     Correlation_loy.append(totalCorr / len(stayEvent) * consumeEventNum)



# AveCorrelation()
print(Correlation_cc)
