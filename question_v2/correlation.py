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
        self.store = []  # 所有商店名

        self.stay_data = pd.DataFrame()  # 停车数据

        self.cc_data = pd.DataFrame()  # 信用卡消费数据
        self.Correlation_cc_columns = []  # 所有卡
        self.cc_events = []  # 处理后的信用卡消费数据
        self.cc_matched_count = []  # 信用卡对应车的匹配数量
        self.cc_matched_dis = []  # 信用卡对应车的匹配距离

        self.loyalty_data = pd.DataFrame()  # 会员卡消费数据
        self.Correlation_loy_columns = pd.DataFrame()  # 所有卡
        self.loy_events = []  # 处理后的会员卡消费数据
        self.Correlation_loy = pd.DataFrame()  # 会员卡对应车的相关度

        # 高斯核函数的参数
        self.sigma1 = 30  # 30秒
        self.sigma2 = 50  # 50米

        self.outputfile_cc = 'output/corr_data_cc1.json'
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

    def timeMatched(self, stayEvent, consumeEvent):
        """求cc的消费事件时间上是否存在于car的停车事件时间段"""
        stay_begin = time.mktime(time.strptime(stayEvent["stay_begin"], "%m/%d/%Y %H:%M:%S"))
        stay_end = time.mktime(time.strptime(stayEvent["stay_end"], "%m/%d/%Y %H:%M:%S"))
        time_consume = time.mktime(time.strptime(consumeEvent.timestamp, "%m/%d/%Y %H:%M"))

        if stay_begin <= time_consume <= stay_end:
            return True
        else:
            return False

    def distance(self, stayEvent, consumeEvent):
        """求空间距离"""
        lat = self.store_position[self.store_position.store == consumeEvent.location]["lat"]
        long = self.store_position[self.store_position.store == consumeEvent.location]["long"]
        distance = geodesic((stayEvent["lat"], stayEvent["long"]), (float(lat), float(long))).m
        return distance

    def correlation_cc(self):
        """求每张credit card和每个car的相关性"""

        for cc_num in self.cc_events:
            res_row_count = []
            res_row_dis = []
            for stayEvents in self.stay_data["stay_periods"]:
                matched_count = 0
                matched_dis = 0
                for consumeEvent in cc_num.iterrows():
                    for stay_period in stayEvents:
                        if self.timeMatched(stay_period, consumeEvent[1]):
                            matched_count += 1
                            matched_dis += self.distance(stay_period,consumeEvent[1])
                            # print(self.distance(stay_period,consumeEvent[1]))
                if(matched_count != 0):
                    ave_matched_dis = matched_dis / matched_count
                else:
                    ave_matched_dis = 5000   # 若匹配数量为0，设置平均距离为5km(相当于无穷)
                res_row_count.append(matched_count)
                res_row_dis.append(ave_matched_dis)
            # print(len(res_row))
            # print(res_row)

            self.cc_matched_count.append(res_row_count)
            self.cc_matched_dis.append(res_row_dis)



    def saveData(self, outputfile):
        """
        相关数据写入文件
        np.savetxt默认的参数，数据格式是二维数组，注意！
        """
        data = {"cc_num": self.Correlation_cc_columns, "car_id": list(self.stay_data.id),
                "matched_count": self.cc_matched_count, 'matched_dis': self.cc_matched_dis}
        with open(outputfile, 'w') as f:

            json.dump(data, f)
if __name__ == '__main__':
    corr = Correlation()
    corr.correlation_cc()
    corr.saveData(corr.outputfile_cc)