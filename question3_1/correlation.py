import json
import csv
import pandas as pd
import numpy as np
import time
import math
from geopy.distance import geodesic


class Correlation:
    def __init__(self):
        self.store_position = pd.DataFrame()  # 商店坐标
        self.store = []                       # 所有商店名

        self.stay_data = pd.DataFrame()       # 停车数据

        self.cc_data = pd.DataFrame()       # 信用卡消费数据
        self.Correlation_cc_columns = []    # 所有卡
        self.cc_events = []                 # 处理后的信用卡消费数据
        self.Correlation_cc = pd.DataFrame()    # 信用卡对应车的相关度

        self.loyalty_data = pd.DataFrame()              # 会员卡消费数据
        self.Correlation_loy_columns = pd.DataFrame()   # 所有卡
        self.loy_events = []                            # 处理后的会员卡消费数据
        self.Correlation_loy = pd.DataFrame()           # 会员卡对应车的相关度

        # 高斯核函数的参数
        self.sigma1 = 30            # 30秒
        self.sigma2 = 50            # 50米

        self.outputfile_cc = 'output/corr_data_cc.txt'
        self.outputfile_loy = 'output/corr_data_loy.txt'

        self.init()

    def init(self):
        """初始化各项数据"""
        # 商店名和经纬度对应的数据，有一些缺失数据
        self.store_position = pd.read_csv("../dataset/store_position.csv").dropna()
        self.store = list(self.store_position.store)
        # print(store)

        self.stay_data = pd.read_json("../dataset/stay_periods_1.0.json")
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


    def timeCorr1(self, stayEvent, consumeEvent, sigma):
        """求cc的时间相似度"""
        stay_begin = time.mktime(time.strptime(stayEvent["stay_begin"], "%m/%d/%Y %H:%M:%S"))
        stay_end = time.mktime(time.strptime(stayEvent["stay_end"], "%m/%d/%Y %H:%M:%S"))
        time_consume = time.mktime(time.strptime(consumeEvent.timestamp, "%m/%d/%Y %H:%M"))

        if time_consume >= stay_begin and time_consume <= stay_end:
            return 1
        elif time_consume < stay_begin:
            if stay_begin - time_consume > 3600:
                return 0
            else:
                return np.exp(- (time_consume - stay_begin) ** 2 / (2 * sigma **2))
        else:
            if stay_end - time_consume > 3600:
                return 0
            return np.exp(- (time_consume - stay_end) ** 2 / (2 * sigma **2))

    def timeCorr2(self, stayEvent, consumeEvent):
        """求loyalty card 的时间相似度"""
        stay_time = stayEvent["stay_begin"][:10]
        time_consume = consumeEvent.timestamp

        if stay_time == time_consume:
            return 1
        else:
            return 0


    def spaceCorr(self, stayEvent, consumeEvent, sigma):
        """gaussian求空间相似度"""
        lat = self.store_position[self.store_position.store == consumeEvent.location]["lat"]
        long = self.store_position[self.store_position.store == consumeEvent.location]["long"]
        distance = geodesic((stayEvent["lat"], stayEvent["long"]), (float(lat), float(long))).m
        # print(distance)
        return np.exp(- distance ** 2 / (2 * sigma ** 2))


    def correlation(self, stayEvent, consumeEvent, card):
        """求时空相似度"""
        if card == 'cc':
            return self.timeCorr1(stayEvent, consumeEvent, self.sigma1)
        else:                 # loyalty card
            return self.timeCorr2(stayEvent, consumeEvent) * self.spaceCorr(stayEvent, consumeEvent, self.sigma2)


    def AveCorrelation_cc(self):
        """求cc相似度矩阵"""
        id = 0
        for stayEvents in self.stay_data["stay_periods"]:
            res_row = []
            for cc_num in self.cc_events:
                count = 0
                totalCorr = 0
                for stay_period in stayEvents:

                    for consumeEvent in cc_num.iterrows():
                        totalCorr += self.correlation(stay_period, consumeEvent[1], 'cc')
                        # totalCorr += self.timeCorr(stay_period, consumeEvent[1], self.sigma1)
                        # totalCorr += self.spaceCorr(stay_period, consumeEvent[1], self.sigma2)
                        count += 1
                res_row.append(totalCorr / count)

            print(len(res_row))
            print(res_row)
            self.Correlation_cc.iloc[id:id + 1, :] = res_row
            id += 1


    def saveData(self, data, outputfile):
        """
        相关数据写入文件
        np.savetxt默认的参数，数据格式是二维数组，注意！
        """
        np.savetxt(outputfile, data, delimiter=',')

if __name__ == '__main__':
    corr = Correlation()
    corr.AveCorrelation_cc()
    corr.saveData(corr.Correlation_cc, corr.outputfile_cc)
    print(corr.store)

