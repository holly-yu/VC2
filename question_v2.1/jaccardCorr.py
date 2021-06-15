import json
import csv
import pandas as pd
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import seaborn as sns
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
        self.corr_scaled = pd.DataFrame()  # 归一化之后的相关度数据

        self.corr_data_sorted = pd.DataFrame()  # 轴排序之后的相关度数据
        self.loy_list_sorted = []
        self.cc_list_sorted = []

        self.init()

    def init(self):
        """初始化各项数据"""

        # 对credit card数据排序并提取出每张卡的消费事件序列，并去重
        self.cc_data = pd.read_csv("../dataset/cc_data.csv")
        self.cc_data = self.cc_data.sort_values(by=["last4ccnum", "timestamp"])


        timestamp = list(self.cc_data["timestamp"])
        timestamp = [t[0:10] for t in timestamp]
        self.cc_data["timestamp"] = timestamp
        self.cc_list = list(set(self.cc_data.last4ccnum))
        self.cc_list.sort()

        self.loyalty_data = pd.read_csv("../dataset/loyalty_data.csv")
        self.loyalty_data = self.loyalty_data.sort_values(by=["loyaltynum", "timestamp"])
        self.day_list = list(set(self.loyalty_data.timestamp))
        self.day_list.sort()
        self.loy_list = list(set(self.loyalty_data.loyaltynum))
        self.loy_list.sort()

        # 对credit card的日期进行处理，只取精确到某天的数据
        for last4ccnum in self.cc_list:
            events = []
            for day in self.day_list:
                loc = list(self.cc_data[((self.cc_data["last4ccnum"] == last4ccnum) & (self.cc_data["timestamp"] == day))].location)
                events.append(loc)
            self.cc_events.append(events)

        # 对loyalty card数据排序并提取出每张卡的消费事件序列，并去重
        for loyaltynum in self.loy_list:
            events = []
            for day in self.day_list:
                loc = list(self.loyalty_data[((self.loyalty_data["loyaltynum"] == loyaltynum) & (self.loyalty_data["timestamp"] == day))].location)

                events.append(loc)
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
                corr_row.append(total / len(self.day_list))
            self.corr.append(corr_row)

    def diagSort(self):
        """对credit card和loyalty card相关度数据进行对角排序"""
        loy_list_sorted = []  # 排序后的loy id列表
        loy_diag_index = []  # 对角线上的loy 索引列表
        loy_index_rest = []

        cc_list_sorted = []  # 排序后的信用卡id列表
        cc_diag_index = []  # 对角线上的信用卡索引列表
        cc_index_rest = []  # 未对角排序信用卡索引列表

        corr_data_sorted = [[0] * len(self.loy_list) for i in self.cc_list]  # 初始化重排序后的相关矩阵

        for indexi, cc in enumerate(self.corr):
            count_max = np.max(cc)
            max_index = cc.index(count_max)

            if self.loy_list[max_index] in self.loy_list_sorted:
                cc_index_rest.append(indexi)
            else:
                cc_diag_index.append(indexi)
                self.cc_list_sorted.append(self.cc_list[indexi])
                loy_diag_index.append(max_index)
                self.loy_list_sorted.append(self.loy_list[max_index])

        loy_diag_index.extend(loy_index_rest)
        for index in loy_index_rest:
            self.loy_list_sorted.append(self.loy_list[index])

        for index, ccnum in enumerate(self.cc_list):
            if index not in cc_diag_index:
                cc_diag_index.append(index)
                self.cc_list_sorted.append(ccnum)

        print(loy_diag_index)
        print(cc_diag_index)
        print(len(cc_diag_index))
        print(len(loy_diag_index))

        for indexi, cc in enumerate(cc_diag_index):
            for indexj, loy in enumerate(loy_diag_index):
                corr_data_sorted[indexi][indexj] = self.corr_scaled.iloc[cc][loy]

        self.corr_data_sorted = pd.DataFrame(corr_data_sorted,index = self.cc_list_sorted, columns=self.loy_list_sorted)

    def normalize(self):
        maxlist = [max(corr) for corr in self.corr]
        max_corr = max(maxlist)
        corr_scale = self.corr
        for i, corrRow in enumerate(self.corr):
            for j, corr in enumerate(corrRow):
                corr_scale[i][j] = corr / max_corr
        self.corr_scaled = pd.DataFrame(corr_scale, index=self.cc_list, columns=self.loy_list)

    def draw_corr(self, data, index, column):


        plt.figure(figsize=(12, 10), dpi=80)

        sns.heatmap(data, vmin=0, vmax=1, xticklabels=index,
                    yticklabels=column, cmap=sns.color_palette("Reds", n_colors=10),
                    linewidths=.5)
        # Decorations
        plt.title('Correlation between credit cards and loyalty card', fontsize=22)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        plt.show()

if __name__ == '__main__':
    corr = Correlation()
    corr.correlation()
    corr.normalize()
    print(corr.corr_scaled)
    corr.diagSort()
    corr.draw_corr(corr.corr_data_sorted, corr.loy_list_sorted, corr.cc_list_sorted)
    # corr.draw_corr(corr.corr_scaled, corr.corr_scaled.columns, corr.corr_scaled.index)  # 画原始数据图
