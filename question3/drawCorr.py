import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from question3.correlation import Correlation

# Import Dataset

# df = pd.read_csv("https://github.com/selva86/datasets/raw/master/mtcars.csv")
# # Plot
#
# plt.figure(figsize=(12,10), dpi= 80)
#
# sns.heatmap(df.corr(), vmin=0, vmax=1, xticklabels=df.corr().columns, yticklabels=df.corr().columns, cmap=sns.color_palette("Reds",n_colors=10), center=0, annot=True)
# # Decorations
# plt.title('Correlogram of mtcars', fontsize=22)
# plt.xticks(fontsize=12)
# plt.yticks(fontsize=12)
#
# plt.show()

def maxminnorm(array):
    max = np.max(array)
    min = 0
    res = []
    for data in array:
        res.append(data * (1 - 0 ) / (max - min) )
    return res

# Import Dataset
corr_data = []
with open('../dataset/corr_data.txt','r') as f:
    for line in f.readlines():
        curLine = line.strip().split(',')
        floatLine = list(np.float64(curLine))
        row = [item if item > 0.98 else 0 for item in maxminnorm(floatLine)]
        corr_data.append(row)

correlation = Correlation()
for data in corr_data:
    data = maxminnorm(data)
print(corr_data)

plt.figure(figsize=(12,10), dpi= 80)

sns.heatmap(corr_data, vmin=0, vmax=1, xticklabels=correlation.Correlation_cc_columns, yticklabels=list(correlation.stay_data.id), cmap=sns.color_palette("Reds",n_colors=10))
# Decorations
plt.title('Correlation between cars and credit cards', fontsize=22)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.show()
