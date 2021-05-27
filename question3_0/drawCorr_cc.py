import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from question3_1.correlation import Correlation
import math

class DrawCorr:
    def __init__(self):
        self.corr_data = []      # 原始的相关数据矩阵
        self.filepath = '../dataset/corr_data1_cc.txt'
        self.correlation = Correlation()

        self.car_list = list(self.correlation.stay_data.id)
        self.cc_list = self.correlation.Correlation_cc_columns

        self.resRedundance = []  # 重复数据，一张卡对应多辆车
        self.resRedunCount = 0   # 重复数据的个数
        self.resRedunCountByRows = []   # 每张卡对应车的数量（list）

        self.corr_data_sorted = []     # 经过对角排序的相似度矩阵
        self.corr_data_diagsort = pd.DataFrame()     # 经过对角排序的相似度矩阵（DataFrame）


    def maxminnorm(self, array):
        """0~1归一化（max为该行最大数据）"""
        max = np.max(array)
        min = 0
        res = []
        for data in array:
            res.append(data * (1 - 0) / (max - min))
        return res

    def process_data(self):
        """处理数据"""
        # Import Dataset
        with open(self.filepath, 'r') as f:
            for line in f.readlines():
                curLine = line.strip().split(',')
                floatLine = list(np.float64(curLine))
                self.corr_data.append(floatLine)
            # 矩阵转置
            self.corr_data = list(map(list, zip(*self.corr_data)))
            # row = [item if item > 0.98 else 0 for item in maxminnorm(floatLine)]
            # corr_data.append(row)

        for index, data in enumerate(self.corr_data):
            self.corr_data[index] = [item if item >= 0.95 else 0 for item in self.maxminnorm(data)]
        print(self.corr_data)


    def draw(self, data, xlabels, ylabels):
        """画相关度矩阵"""
        plt.figure(figsize=(12, 10), dpi=80)

        sns.heatmap(data, vmin=0, vmax=1, xticklabels=xlabels,
                    yticklabels=ylabels, cmap=sns.color_palette("Reds", n_colors=10),
                    linewidths=.5)
        # Decorations
        plt.title('Correlation between cars and credit cards', fontsize=22)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        plt.show()


    def resDetect(self):
        """检查重复数据"""
        for index, data in enumerate(self.corr_data):
            cc = {}

            car_idlist = []
            for indexj, datum in enumerate(data):
                if datum != 0:
                    car_idlist.append(list(self.correlation.stay_data.id)[indexj])
            if len(car_idlist) > 1:
                cc['cc_lastnum'] = self.correlation.Correlation_cc_columns[index]
                cc['car_idlist'] = car_idlist
                self.resRedundance.append(cc)
        self.resRedunCount = len(self.resRedundance)

        gt = lambda x: np.float64(x) > 0
        for i, cc in enumerate(self.corr_data):  # 计算每行有重复的数据
            count = len([data for data in cc if gt(data)])
            self.resRedunCountByRows.append(count)

    def diagSort(self):
        """对相关矩阵进行对角排序，尽量使一一对应的数据在左上角的对角线上"""

        gt = lambda x: np.float64(x) > 0
        car_list_sorted = []   # 排序后的车id列表
        cc_list_sorted = []    # 排序后的信用卡id列表
        car_diag_index = []     # 对角线上的车id列表
        cc_diag_index = []      # 对角线上的信用卡id列表

        # car_list_rest = []
        # cc_list_rest = []

        self.corr_data_sorted = [[0] * len(self.car_list) for i in self.cc_list]  # 初始化重排序后的相关矩阵

        corr_data_T = list(map(list, zip(*self.corr_data)))
        # 把所有 所在行和列只有一个元素的 行和列 排列在前边，形成对角线形状。
        countDiag = 0    # 在对角线上的方块个数
        for index, count in enumerate(self.resRedunCountByRows):
            if count == 1:
                for indexi, corr in enumerate(self.corr_data[index]):
                    if corr != 0:
                        countj = len([corr_T for corr_T in corr_data_T[indexi] if gt(corr_T)])
                        if countj == 1:
                            cc_list_sorted.append(self.cc_list[index])
                            car_list_sorted.append(self.car_list[indexi])
                            cc_diag_index.append(index)
                            car_diag_index.append(indexi)
                            self.corr_data_sorted[countDiag][countDiag] = self.corr_data[index][indexi]
                            countDiag += 1
            #             else:
            #                 cc_list_rest.append(self.cc_list[index])
            #                 car_list_rest.append(self.car_list[indexi])
            # else:
            #     cc_list_rest.append(self.cc_list[index])
        # print(self.corr_data_sorted)
        # print(cc_list_sorted)
        # print(car_list_sorted)


        # 首先把前 countDiag 行数据填满，并把所有列 车名加上
        countDiagj = countDiag
        for index, car_data in enumerate(self.car_list):
            if index not in car_diag_index:
                car_list_sorted.append(self.car_list[index])
                car_diag_index.append(index)
                for i in range(countDiag):
                    if self.corr_data[cc_diag_index[i]][index] != 0:
                        self.corr_data_sorted[i][countDiagj] =  self.corr_data[cc_diag_index[i]][index]
                countDiagj += 1

        # 把剩下行数据填满，并把所有行 cc_id加上
        countDiagk = countDiag
        for index, cc_data in enumerate(self.cc_list):
            if index not in cc_diag_index:
                cc_list_sorted.append(self.cc_list[index])
                cc_diag_index.append(index)
                for i in range(len(self.car_list)):
                    if self.corr_data[index][car_diag_index[i]] != 0:
                        self.corr_data_sorted[countDiagk][i] = self.corr_data[index][car_diag_index[i]]
                countDiagk += 1

        self.corr_data_diagsort = pd.DataFrame(self.corr_data_sorted, index=cc_list_sorted, columns=car_list_sorted)

    def diagSort2(self):
        car_list_sorted = []  # 排序后的车id列表
        car_diag_index = []  # 对角线上的车索引列表

        cc_list_sorted = []  # 排序后的信用卡id列表
        cc_diag_index = []  # 对角线上的信用卡索引列表
        cc_index_rest = []  # 未对角排序信用卡索引列表


        self.corr_data_sorted = [[0] * len(self.car_list) for i in self.cc_list]  # 初始化重排序后的相关矩阵


        flag = False
        for indexi, cc in enumerate(self.corr_data):
            for indexj, corr in enumerate(cc):
                if corr == 1:
                    if self.car_list[indexj] in car_list_sorted:
                        cc_index_rest.append(indexi)
                        break
                    else:
                        cc_diag_index.append(indexi)
                        cc_list_sorted.append(self.cc_list[indexi])
                        car_diag_index.append(indexj)
                        car_list_sorted.append(self.car_list[indexj])
            #     if  len(car_list_sorted) == len(self.car_list):
            #         flag = True
            #         break
            # if flag:
            #     break

        cc_diag_index.extend(cc_index_rest)
        for index in cc_index_rest:
            cc_list_sorted.append(self.cc_list[index])


        for index, carid in enumerate(self.car_list):
            if index not in car_diag_index:
                car_diag_index.append(index)
                car_list_sorted.append(carid)
        print(len(cc_diag_index))
        print(cc_diag_index)
        print(len(car_diag_index))
        print(car_diag_index)

        for indexi, cc in enumerate(cc_diag_index):
            for indexj, car in enumerate(car_diag_index):
                if self.corr_data[cc][car] != 0:
                    self.corr_data_sorted[indexi][indexj] = self.corr_data[cc][car]



        self.corr_data_diagsort = pd.DataFrame(self.corr_data_sorted, index=cc_list_sorted, columns=car_list_sorted)


if __name__ == '__main__':
    drawcorr = DrawCorr()
    drawcorr.process_data()
    drawcorr.draw(drawcorr.corr_data, drawcorr.car_list, drawcorr.cc_list)
    drawcorr.resDetect()
    # drawcorr.diagSort()
    drawcorr.diagSort2()
    drawcorr.draw(drawcorr.corr_data_diagsort, drawcorr.corr_data_diagsort.columns, drawcorr.corr_data_diagsort.index)
