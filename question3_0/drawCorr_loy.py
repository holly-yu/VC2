import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from question3.correlation import Correlation
import math

class DrawCorr:
    def __init__(self):
        self.corr_data = []      # 原始的相关数据矩阵
        self.filepath = '../dataset/corr_data_loy.txt'
        self.correlation = Correlation()

        self.car_list = list(self.correlation.stay_data.id)
        self.loy_list = self.correlation.Correlation_loy_columns

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
        plt.title('Correlation between cars and loyalty cards', fontsize=22)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        plt.show()


    def resDetect(self):
        """检查重复数据"""
        for index, data in enumerate(self.corr_data):
            loy = {}

            car_idlist = []
            for indexj, datum in enumerate(data):
                if datum != 0:
                    car_idlist.append(list(self.correlation.stay_data.id)[indexj])
            if len(car_idlist) > 1:
                loy['loy_lastnum'] = self.correlation.Correlation_loy_columns[index]
                loy['car_idlist'] = car_idlist
                self.resRedundance.append(loy)
        self.resRedunCount = len(self.resRedundance)

        gt = lambda x: np.float64(x) > 0
        for i, loy in enumerate(self.corr_data):  # 计算每行有重复的数据
            count = len([data for data in loy if gt(data)])
            self.resRedunCountByRows.append(count)

    def diagSort(self):
        """对相关矩阵进行对角排序，尽量使一一对应的数据在左上角的对角线上"""

        gt = lambda x: np.float64(x) > 0
        car_list_sorted = []   # 排序后的车id列表
        loy_list_sorted = []    # 排序后的信用卡id列表
        car_diag_index = []     # 对角线上的车id列表
        loy_diag_index = []      # 对角线上的信用卡id列表

        # car_list_rest = []
        # loy_list_rest = []

        self.corr_data_sorted = [[0] * len(self.car_list) for i in self.loy_list]  # 初始化重排序后的相关矩阵

        corr_data_T = list(map(list, zip(*self.corr_data)))
        # 把所有 所在行和列只有一个元素的 行和列 排列在前边，形成对角线形状。
        countDiag = 0    # 在对角线上的方块个数
        for index, count in enumerate(self.resRedunCountByRows):
            if count == 1:
                for indexi, corr in enumerate(self.corr_data[index]):
                    if corr != 0:
                        countj = len([corr_T for corr_T in corr_data_T[indexi] if gt(corr_T)])
                        if countj == 1:
                            loy_list_sorted.append(self.loy_list[index])
                            car_list_sorted.append(self.car_list[indexi])
                            loy_diag_index.append(index)
                            car_diag_index.append(indexi)
                            self.corr_data_sorted[countDiag][countDiag] = self.corr_data[index][indexi]
                            countDiag += 1
            #             else:
            #                 loy_list_rest.append(self.loy_list[index])
            #                 car_list_rest.append(self.car_list[indexi])
            # else:
            #     loy_list_rest.append(self.loy_list[index])
        # print(self.corr_data_sorted)
        # print(loy_list_sorted)
        # print(car_list_sorted)


        # 首先把前 countDiag 行数据填满，并把所有列 车名加上
        countDiagj = countDiag
        for index, car_data in enumerate(self.car_list):
            if index not in car_diag_index:
                car_list_sorted.append(self.car_list[index])
                car_diag_index.append(index)
                for i in range(countDiag):
                    if self.corr_data[loy_diag_index[i]][index] != 0:
                        self.corr_data_sorted[i][countDiagj] =  self.corr_data[loy_diag_index[i]][index]
                countDiagj += 1

        # 把剩下行数据填满，并把所有行 loy_id加上
        countDiagk = countDiag
        for index, loy_data in enumerate(self.loy_list):
            if index not in loy_diag_index:
                loy_list_sorted.append(self.loy_list[index])
                loy_diag_index.append(index)
                for i in range(len(self.car_list)):
                    if self.corr_data[index][car_diag_index[i]] != 0:
                        self.corr_data_sorted[countDiagk][i] = self.corr_data[index][car_diag_index[i]]
                countDiagk += 1

        self.corr_data_diagsort = pd.DataFrame(self.corr_data_sorted, index=loy_list_sorted, columns=car_list_sorted)

    def diagSort2(self):
        car_list_sorted = []  # 排序后的车id列表
        car_diag_index = []  # 对角线上的车索引列表

        loy_list_sorted = []  # 排序后的信用卡id列表
        loy_diag_index = []  # 对角线上的信用卡索引列表
        loy_index_rest = []  # 未对角排序信用卡索引列表


        self.corr_data_sorted = [[0] * len(self.car_list) for i in self.loy_list]  # 初始化重排序后的相关矩阵


        flag = False
        for indexi, loy in enumerate(self.corr_data):
            for indexj, corr in enumerate(loy):
                if corr == 1:
                    if self.car_list[indexj] in car_list_sorted:
                        loy_index_rest.append(indexi)
                        break
                    else:
                        loy_diag_index.append(indexi)
                        loy_list_sorted.append(self.loy_list[indexi])
                        car_diag_index.append(indexj)
                        car_list_sorted.append(self.car_list[indexj])
            #     if  len(car_list_sorted) == len(self.car_list):
            #         flag = True
            #         break
            # if flag:
            #     break

        loy_diag_index.extend(loy_index_rest)
        for index in loy_index_rest:
            loy_list_sorted.append(self.loy_list[index])


        for index, carid in enumerate(self.car_list):
            if index not in car_diag_index:
                car_diag_index.append(index)
                car_list_sorted.append(carid)
        print(len(loy_diag_index))
        print(loy_diag_index)
        print(len(car_diag_index))
        print(car_diag_index)

        for indexi, loy in enumerate(loy_diag_index):
            for indexj, car in enumerate(car_diag_index):
                if self.corr_data[loy][car] != 0:
                    self.corr_data_sorted[indexi][indexj] = self.corr_data[loy][car]



        self.corr_data_diagsort = pd.DataFrame(self.corr_data_sorted, index=loy_list_sorted, columns=car_list_sorted)


if __name__ == '__main__':
    drawcorr = DrawCorr()
    drawcorr.process_data()
    drawcorr.draw(drawcorr.corr_data, drawcorr.car_list, drawcorr.loy_list)
    drawcorr.resDetect()
    # drawcorr.diagSort()
    drawcorr.diagSort2()
    drawcorr.draw(drawcorr.corr_data_diagsort, drawcorr.corr_data_diagsort.columns, drawcorr.corr_data_diagsort.index)
