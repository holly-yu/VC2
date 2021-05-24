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
        self.filepath = '../dataset/corr_data.txt'
        self.correlation = Correlation()

        self.car_list = list(self.correlation.stay_data.id)
        self.cc_list = self.correlation.Correlation_cc_columns

        self.resRedundance = []  # 重复数据，一张卡对应多辆车
        self.resRedunCount = 0
        self.resRedunCountByRows = []

        self.corr_data_sorted = []
        self.corr_data_diagsort = pd.DataFrame()




    # 0~1归一化（max为该行最大数据）
    def maxminnorm(self, array):
        max = np.max(array)
        min = 0
        res = []
        for data in array:
            res.append(data * (1 - 0) / (max - min))
        return res

    # 处理数据
    def process_data(self):
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
            self.corr_data[index] = [item if item >= 0.9 else 0 for item in self.maxminnorm(data)]
        print(self.corr_data)

    def draw(self, data, xlabels, ylabels):
        plt.figure(figsize=(12, 10), dpi=80)

        sns.heatmap(data, vmin=0, vmax=1, xticklabels=xlabels,
                    yticklabels=ylabels, cmap=sns.color_palette("Reds", n_colors=10),
                    linewidths=.5)
        # Decorations
        plt.title('Correlation between cars and credit cards', fontsize=22)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        plt.show()

    # 检查重复数据
    def resDetect(self):
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

    def diagSort(self):

        gt = lambda x: np.float64(x) > 0
        for i, cc in enumerate(self.corr_data):
            count = len([data for data in cc if gt(data)])
            self.resRedunCountByRows.append(count)
        print(self.resRedunCountByRows)

        car_list_sorted = []   # 排序后的车id列表
        cc_list_sorted = []    # 排序后的信用卡id列表
        car_list_rest = []
        cc_list_rest = []

        self.corr_data_sorted = [[0] * len(self.car_list) for i in self.cc_list]  # 初始化重排序后的相关矩阵

        corr_data_T = list(map(list, zip(*self.corr_data)))
        # 把所有 所在行和列只有一个元素的 行和列 排列在前边，形成对角线形状。
        countDiag = 0
        for index, count in enumerate(self.resRedunCountByRows):
            if count == 1:
                for indexi, corr in enumerate(self.corr_data[index]):
                    if corr != 0:
                        countj = len([corr_T for corr_T in corr_data_T[indexi] if gt(corr_T)])
                        if countj == 1:
                            cc_list_sorted.append(self.cc_list[index])
                            car_list_sorted.append(self.car_list[indexi])
                            self.corr_data_sorted[countDiag][countDiag] = self.corr_data[index][indexi]
                            print(countDiag, index, indexi)
                            countDiag += 1

                        else:
                            cc_list_rest.append(self.cc_list[index])
                            car_list_rest.append(self.car_list[indexi])
            else:
                cc_list_rest.append(self.cc_list[index])
        print(cc_list_sorted)
        print(car_list_sorted)

        # for index, count in enumerate(self.resRedunCountByRows):
        #     data = [0] * len(self.car_list)
        #     if count == 1:
        #         cc_list_sorted.append(self.cc_list[index])
        #         for indexj, corr in enumerate(self.corr_data[index]):
        #             if corr != 0 and index < len(self.car_list):
        #                 car_list_sorted.append(self.car_list[indexj])
        #                 data[index] = self.corr_data[indexj]
        #         self.corr_data_sorted.append(data)
        # print(len(self.corr_data_sorted[0]))
        #
        #
        # for index, count in enumerate(self.resRedunCountByRows):
        #     data = [0] * len(self.car_list)
        #     if count > 1:
        #         cc_list_sorted.append(self.cc_list[index])



        # self.corr_data_diagsort = pd.DataFrame(self.corr_data_sorted, index=cc_list_sorted, columns=car_list_sorted)





if __name__ == '__main__':
    drawcorr = DrawCorr()
    drawcorr.process_data()
    drawcorr.draw(drawcorr.corr_data, drawcorr.car_list, drawcorr.cc_list)
    drawcorr.resDetect()
    print(drawcorr.resRedundance)
    drawcorr.diagSort()
    # drawcorr.draw(drawcorr, drawcorr.corr_data_diagsort.columns, drawcorr.corr_data_diagsort.index)
