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
        self.car_list = []
        self.cc_list = []
        self.loy_list = []

        self.cc_data = pd.DataFrame()  # 信用卡消费数据
        self.Correlation_cc_columns = []  # 所有卡
        self.cc_events = []  # 处理后的信用卡消费数据
        self.cc_matched_count = []  # 信用卡对应车的匹配数量
        self.cc_matched_dis = []  # 信用卡对应车的匹配距离
        self.cc_matched_count_sorted = []
        self.cc_matched_dis_sorted = []

        self.loyalty_data = pd.DataFrame()  # 会员卡消费数据
        self.Correlation_loy_columns = pd.DataFrame()  # 所有卡
        self.loy_events = []  # 处理后的会员卡消费数据
        self.loy_matched_count = []
        self.loy_matched_dis = []
        self.loy_matched_count_sorted = []
        self.loy_matched_dis_sorted = []


        self.cc_list_sorted = []
        self.loy_list_sorted = []
        self.car_list_sorted = []


        # self.outputfile_cc = 'output/corr_data_cc1.json'
        self.outputfile_cc = 'output3/corr_data_cc_sorted_1500.json'
        self.outputfile_loy = 'output2/corr_data_loy_sorted_1500.json'

        self.init()

    def init(self):
        """初始化各项数据"""
        # 商店名和经纬度对应的数据，有一些缺失数据
        self.store_position = pd.read_csv("../dataset/store_position.csv").dropna()
        self.store = list(self.store_position.store)
        # print(store)

        self.stay_data = pd.read_json("../dataset/stay_periods_1.0.json")
        self.car_list = list(self.stay_data.id)
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
        self.cc_list = self.Correlation_cc_columns
        self.loy_list = self.Correlation_loy_columns

    def timeMatched(self, stayEvent, consumeEvent):
        """求cc的消费事件时间上是否存在于car的停车事件时间段"""
        stay_begin = time.mktime(time.strptime(stayEvent["stay_begin"], "%m/%d/%Y %H:%M:%S"))
        stay_end = time.mktime(time.strptime(stayEvent["stay_end"], "%m/%d/%Y %H:%M:%S"))
        time_consume = time.mktime(time.strptime(consumeEvent.timestamp, "%m/%d/%Y %H:%M"))

        if stay_begin <= time_consume <= stay_end:
            return True
        else:
            return False

    def timeMatched_loy(self, stayEvent, consumeEvent):
        """求loyalty_card的消费事件时间上是否存在于car的停车事件时间段"""
        stay_begin = time.mktime(time.strptime(stayEvent["stay_begin"][:10], "%m/%d/%Y"))
        stay_end = time.mktime(time.strptime(stayEvent["stay_end"][:10], "%m/%d/%Y"))
        time_consume = time.mktime(time.strptime(consumeEvent.timestamp, "%m/%d/%Y"))

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
                        if self.timeMatched(stay_period, consumeEvent[1]) and self.distance(stay_period,consumeEvent[1]) <= 1500:  # 时间上匹配且空间上距离 <= 3000m
                            matched_count += 1
                            matched_dis += self.distance(stay_period,consumeEvent[1])
                            # print(self.distance(stay_period,consumeEvent[1]))
                if matched_count != 0:
                    ave_matched_dis = matched_dis / matched_count
                else:
                    ave_matched_dis = 1500   # 若匹配数量为0，设置平均距离为3km(相当于无穷)
                res_row_count.append(matched_count/len(cc_num))
                res_row_dis.append(ave_matched_dis)
            print(res_row_count)
            # print(res_row)

            self.cc_matched_count.append(res_row_count)
            self.cc_matched_dis.append(res_row_dis)

        self.cc_matched_count = list(map(list, zip(*self.cc_matched_count)))
        self.cc_matched_dis = list(map(list, zip(*self.cc_matched_dis)))

        print(self.cc_matched_count)

        
    def correlation_loy(self):
        """求每张loyalty card和每个car的相关性"""

        for loy_num in self.loy_events:
            res_row_count = []
            res_row_dis = []
            for stayEvents in self.stay_data["stay_periods"]:
                matched_count = 0
                matched_dis = 0
                for consumeEvent in loy_num.iterrows():
                    matched_dis_list = []
                    for stay_period in stayEvents:
                        if self.timeMatched_loy(stay_period, consumeEvent[1]) and self.distance(stay_period,consumeEvent[1]) <= 800:  # 时间上匹配且空间上距离 <= 1500m
                            matched_dis_list.append(self.distance(stay_period,consumeEvent[1]))

                    if len(matched_dis_list) > 0:
                        matched_dis += np.min(matched_dis_list)
                        matched_count += 1
                if matched_count != 0 :
                    ave_matched_dis = matched_dis / matched_count
                else:
                    ave_matched_dis = 800   # 若匹配数量为0，设置平均距离为1km(相当于无穷)
                res_row_count.append(matched_count)
                res_row_dis.append(ave_matched_dis)
            print(len(res_row_count))
            print(res_row_count)

            self.loy_matched_count.append(res_row_count)
            self.loy_matched_dis.append(res_row_dis)

        self.loy_matched_count = list(map(list, zip(*self.loy_matched_count)))
        self.loy_matched_dis = list(map(list, zip(*self.loy_matched_dis)))

    def diagSort_cc(self):
        """对相关矩阵进行对角排序，尽量使一一对应的数据在左上角的对角线上"""

        car_list_sorted = []  # 排序后的车id列表
        car_diag_index = []  # 对角线上的车索引列表

        cc_list_sorted = []  # 排序后的信用卡id列表
        cc_diag_index = []  # 对角线上的信用卡索引列表
        cc_index_rest = []  # 未对角排序信用卡索引列表
        car_index_rest = []

        self.cc_matched_count_sorted = [[0] * len(self.cc_list) for i in self.car_list]  # 初始化重排序后的相关矩阵
        self.cc_matched_dis_sorted = [[0] * len(self.cc_list) for i in self.car_list]  # 初始化重排序后的相关矩阵


        for indexi, car in enumerate(self.cc_matched_count):
            count_max = np.max(car)
            max_num = 0
            min_dis_list = []          # count为最大匹配数量，所对应的距离列表
            min_dis_index = []
            for indexj, count in enumerate(car):
                if count == count_max:
                    max_num += 1
                    min_dis_list.append(self.cc_matched_dis[indexi][indexj])
                    min_dis_index.append(indexj)
            if max_num == 1:
                max_index = car.index(count_max)
            else:                                   # 对于多个最大匹配数量，求最短匹配距离
                min_dis = np.min(min_dis_list)
                max_index = min_dis_index[min_dis_list.index(min_dis)]

            if self.cc_list[max_index] in self.cc_list_sorted:
                car_index_rest.append(indexi)
            else:
                cc_diag_index.append(max_index)
                self.cc_list_sorted.append(self.cc_list[max_index])
                car_diag_index.append(indexi)
                self.car_list_sorted.append(self.car_list[indexi])

        car_diag_index.extend(car_index_rest)
        for index in car_index_rest:
            self.car_list_sorted.append(self.car_list[index])


        for index, ccnum in enumerate(self.cc_list):
            if index not in cc_diag_index:
                cc_diag_index.append(index)
                self.cc_list_sorted.append(ccnum)


        print(car_diag_index)
        print(cc_diag_index)

        for indexi, car in enumerate(car_diag_index):
            for indexj, cc in enumerate(cc_diag_index):
                self.cc_matched_count_sorted[indexi][indexj] = self.cc_matched_count[car][cc]
                self.cc_matched_dis_sorted[indexi][indexj] = self.cc_matched_dis[car][cc]


    def diagSort_loy(self):
        """
        loyalty_card
        对相关矩阵进行对角排序，尽量使一一对应的数据在左上角的对角线上
        """

        car_list_sorted = []  # 排序后的车id列表
        car_diag_index = []  # 对角线上的车索引列表

        loy_list_sorted = []  # 排序后的信用卡id列表
        loy_diag_index = []  # 对角线上的信用卡索引列表
        loy_index_rest = []  # 未对角排序信用卡索引列表
        car_index_rest = []

        self.loy_matched_count_sorted = [[0] * len(self.loy_list) for i in self.car_list]  # 初始化重排序后的相关矩阵
        self.loy_matched_dis_sorted = [[0] * len(self.loy_list) for i in self.car_list]  # 初始化重排序后的相关矩阵

        for indexi, car in enumerate(self.loy_matched_count):
            count_max = np.max(car)
            max_num = 0
            min_dis_list = []  # count为最大匹配数量，所对应的距离列表
            min_dis_index = []
            for indexj, count in enumerate(car):
                if count == count_max:
                    max_num += 1
                    min_dis_list.append(self.loy_matched_dis[indexi][indexj])
                    min_dis_index.append(indexj)
            if max_num == 1:
                max_index = car.index(count_max)
            else:  # 对于多个最大匹配数量，求最短匹配距离
                min_dis = np.min(min_dis_list)
                max_index = min_dis_index[min_dis_list.index(min_dis)]

            if self.loy_list[max_index] in self.loy_list_sorted:
                car_index_rest.append(indexi)
            else:
                loy_diag_index.append(max_index)
                self.loy_list_sorted.append(self.loy_list[max_index])
                car_diag_index.append(indexi)
                self.car_list_sorted.append(self.car_list[indexi])

        car_diag_index.extend(car_index_rest)
        for index in car_index_rest:
            self.car_list_sorted.append(self.car_list[index])

        for index, loynum in enumerate(self.loy_list):
            if index not in loy_diag_index:
                loy_diag_index.append(index)
                self.loy_list_sorted.append(loynum)

        print(car_diag_index)
        print(loy_diag_index)

        for indexi, car in enumerate(car_diag_index):
            for indexj, loy in enumerate(loy_diag_index):
                self.loy_matched_count_sorted[indexi][indexj] = self.loy_matched_count[car][loy]
                self.loy_matched_dis_sorted[indexi][indexj] = self.loy_matched_dis[car][loy]

    def saveData(self, outputfile):
        """
        相关数据写入文件
        np.savetxt默认的参数，数据格式是二维数组，注意！
        """
        # data = {"cc_num": self.Correlation_cc_columns, "car_id": list(self.stay_data.id),
        #         "matched_count": self.cc_matched_count, 'matched_dis': self.cc_matched_dis}
        # with open(outputfile, 'w') as f:
        #     json.dump(data, f)

        data = {"cc_num": self.cc_list_sorted, "car_id": self.car_list_sorted,
                "matched_count": self.cc_matched_count_sorted, 'matched_dis': self.cc_matched_dis_sorted}
        with open(outputfile, 'w') as f:
            json.dump(data, f)

    def saveData_loy(self, outputfile):
        """
        相关数据写入文件
        np.savetxt默认的参数，数据格式是二维数组，注意！
        """

        data = {"loy_num": self.loy_list_sorted, "car_id": self.car_list_sorted,
                "matched_count": self.loy_matched_count_sorted, 'matched_dis': self.loy_matched_dis_sorted}
        with open(outputfile, 'w') as f:
            json.dump(data, f)


if __name__ == '__main__':
    corr = Correlation()
    # 求cc匹配数据
    corr.correlation_cc()
    corr.diagSort_cc()
    corr.saveData(corr.outputfile_cc)

    # 求loy匹配数据
    # corr.correlation_loy()
    # corr.diagSort_loy()
    # corr.saveData_loy(corr.outputfile_loy)
