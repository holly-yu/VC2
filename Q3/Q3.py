import json
import csv
import pandas as pd

with open("../dataset/stay_points.json", "r") as f:
    stay_data = json.load(f)
print(stay_data)

cc_data = pd.read_csv("../dataset/cc_data.csv")
print(cc_data)

loyalty_data = pd.read_csv("../dataset/loyalty_data.csv")
print(loyalty_data)