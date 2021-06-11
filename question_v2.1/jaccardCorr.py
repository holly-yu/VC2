import json
import csv
import pandas as pd
import numpy as np
import time
import math
from geopy.distance import geodesic

class Correlation:
    def __init__(self):
        self.stay_data = pd.DataFrame()  # 停车数据
        self.car_list = []
        self.cc_list = []
        self.loy_list = []

        self.cc_data = pd.DataFrame()  # 信用卡消费数据
        self.cc_events = []  # 处理后的信用卡消费数据

        self.loyalty_data = pd.DataFrame()  # 会员卡消费数据
        self.loy_events = []  # 处理后的会员卡消费数据
        self.day_list = []   # 日期列表

        self.corr = []   # 相关度数据

        self.init()

    def init(self):
        """初始化各项数据"""

        # 对credit card数据排序并提取出每张卡的消费事件序列，并去重
        self.cc_data = pd.read_csv("../dataset/cc_data.csv")
        self.cc_data = self.cc_data.sort_values(by=["last4ccnum", "timestamp"])
        self.cc_list = list(set(self.cc_data.last4ccnum))
        self.cc_list.sort()




        # 对loyalty card数据排序并提取出每张卡的消费事件序列，并去重
        self.loyalty_data = pd.read_csv("../dataset/loyalty_data.csv")
        self.loyalty_data = self.loyalty_data.sort_values(by=["loyaltynum", "timestamp"])
        self.day_list = list(set(self.loyalty_data.timestamp))
        self.day_list.sort()
        self.loy_list = list(set(self.loyalty_data.loyaltynum))
        self.loy_list.sort()

        for last4ccnum in self.cc_list:
            events = []
            for day in self.day_list:
                if self.cc_data[self.cc_data.last4ccnum == last4ccnum ][self.cc_data.timestamp == day].location:
                    events.append(self.cc_data[self.cc_data.last4ccnum == last4ccnum ][self.cc_data.timestamp == day])
                else:
                    events.append([])
            self.cc_events.append(events)

        for loyaltynum in self.loy_list:
            events = []
            for day in self.day_list:
                if self.loyalty_data[self.loyalty_data.loyaltynum == loyaltynum ][self.loyalty_data.timestamp == day].location:
                    events.append(self.loyalty_data[self.loyalty_data.loyaltynum == loyaltynum][self.loyalty_data.timestamp == day].location)
                else:
                    events.append([])
            self.loy_events.append(events)

    def jaccard_coefficient(self, cc_consume_event, loy_consume_event):
        intersection = list(set(cc_consume_event).intersection(set(loy_consume_event)))
        union = list(set(cc_consume_event).union(set(loy_consume_event)))
        if len(union) == 0:
            return 0
        return len(intersection) / len(union)

    def correlation(self):
        for i, cc_num in enumerate(self.cc_list):
            corr_row = []
            for j, loy_num in enumerate(self.loy_list):
                total = 0
                for k, day in enumerate(self.day_list):
                    total += self.jaccard_coefficient(self.cc_events[i][k], self.loy_events[j][k])
                corr_row.append(total / day)
            self.corr.append(corr_row)


if __name__ == '__main__':
    corr = Correlation()
    print(len(corr.cc_events))
    print(len(corr.loy_events))
