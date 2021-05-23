import json
import csv
import pandas as pd
import numpy as np
import time
import math
from geopy.distance import geodesic


class Correlation:
    def __init__(self):
        self.store_position = pd.DataFrame()
        self.store = []
        self.stay_data = pd.DataFrame()

        self.cc_data = pd.DataFrame()
        self.Correlation_cc_columns = []
        self.cc_events = []
        self.Correlation_cc = pd.DataFrame()

        self.loyalty_data = pd.DataFrame()
        self.Correlation_loy_columns = pd.DataFrame()
        self.loy_events = []
        self.Correlation_loy = pd.DataFrame()

        self.sigma = 10

        self.init()

    def init(self):
        self.store_position = pd.read_csv("../dataset/store_position.csv").dropna()
        # 商店名和经纬度对应的数据，有一些缺失数据
        self.store_position = pd.read_csv("../dataset/store_position.csv").dropna()
        self.store = list(self.store_position.store)
        # print(store)

        self.stay_data = pd.read_json("../dataset/stay_periods.json")
        # print(stay_data)

        # cc卡对应的关系矩阵
        self.cc_data = pd.read_csv("../dataset/cc_data.csv")
        self.cc_data = self.cc_data.sort_values(by=["last4ccnum", "timestamp"])
        self.cc_data = self.cc_data[self.cc_data.location.isin(self.store)]
        self.Correlation_cc_columns = list(set(self.cc_data.last4ccnum))
        self.Correlation_cc_columns.sort()
        for last4ccnum in self.Correlation_cc_columns:
            self.cc_events.append(self.cc_data[self.cc_data.last4ccnum == last4ccnum])

        # print(cc_data.location)

        # loyalty卡对应的关系矩阵
        self.loyalty_data = pd.read_csv("../dataset/loyalty_data.csv")
        self.loyalty_data = self.loyalty_data.sort_values(by=["loyaltynum", "timestamp"])
        self.loyalty_data = self.loyalty_data[self.loyalty_data.location.isin(self.store)]
        self.Correlation_loy_columns = list(set(self.loyalty_data.loyaltynum))
        self.Correlation_loy_columns.sort()

        for loyaltynum in self.Correlation_loy_columns:
            self.loy_events.append(self.loyalty_data[self.loyalty_data.loyaltynum == loyaltynum])
        # print(loyalty_data.location)

        self.Correlation_cc = pd.DataFrame(index=list(self.stay_data.id), columns=self.Correlation_cc_columns)
        self.Correlation_loy = pd.DataFrame(index=list(self.stay_data.id), columns=self.Correlation_loy_columns)

    # 求时间相似度
    def timeCorr(self, stayEvent, consumeEvent):
        stay_begin = time.mktime(time.strptime(self.stayEvent["stay_begin"], "%m/%d/%Y %H:%M:%S"))
        stay_end = time.mktime(time.strptime(self.stayEvent["stay_end"], "%m/%d/%Y %H:%M:%S"))
        time_consume = time.mktime(time.strptime(consumeEvent.timestamp, "%m/%d/%Y %H:%M"))

        if time_consume >= stay_begin and time_consume <= stay_end:
            return 1
        elif time_consume < stay_begin:
            if stay_begin - time_consume > 7200:
                return 0
            else:
                return np.exp((time_consume - stay_begin) / 100)
        else:
            if stay_end - time_consume > 7200:
                return 0
            return np.exp((stay_end - time_consume) / 100)

    # gaussian求空间相似度
    def spaceCorr(self, stayEvent, consumeEvent, sigma):
        lat = self.store_position[self.store_position.store == consumeEvent.location]["lat"]
        long = self.store_position[self.store_position.store == consumeEvent.location]["long"]
        distance = geodesic((stayEvent["lat"], stayEvent["long"]), (float(lat), float(long))).km
        # print(distance)
        return np.exp(- distance ** 2 / 2 * sigma ** 2)

    # 求时空相似度
    def correlation(self, stayEvent, consumeEvent):
        return self.timeCorr(stayEvent, consumeEvent) * self.spaceCorr(stayEvent, consumeEvent, sigma)

    # 求相似度矩阵
    def AveCorrelation(self):
        id = 0
        for stayEvents in self.stay_data["stay_periods"]:
            res_row = []
            for cc_num in self.cc_events:
                count = 0
                totalCorr = 0
                for stay_period in stayEvents:

                    for consumeEvent in cc_num.iterrows():
                        totalCorr += self.correlation(stay_period, consumeEvent[1])
                        count += 1
                res_row.append(totalCorr / count)

            # print(len(res_row))
            # print(res_row)
            self.Correlation_cc.iloc[id:id + 1, :] = res_row
            id += 1

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

    def drawcorr(self):
        pass

if __name__ == '__main__':
    corr = Correlation()
    # corr.AveCorrelation()
    print(corr.store)
    print(len(corr.stay_data.id))
    print(len(corr.Correlation_cc_columns))
    print(len(corr.Correlation_loy_columns))
