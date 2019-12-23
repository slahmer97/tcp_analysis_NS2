import time
import os
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np

file_d = "out.tr"
with open(file_d, 'r+') as f:
    content = f.read()
    if "event time" not in content:
        f.seek(0, 0)
        f.write("event time from_node to_node ptype psize flags fid src_dest_addr seq_num pid" + '\n' + content)
print("[+] checked header")
pd_data = pd.read_csv(file_d, delimiter=" ", index_col=False)
print("[+] read panda frame")
np_data = pd_data.to_numpy()
print("[+] convert to numpy arr")




def cal_tmp(data, filename):
    totalBits1 = 0
    clock = 0.0
    stamping_interval = 0.05
    file = open("{}.csv".format(filename), mode="w")
    file.write("time,thoughput1\n")
    for line in data:
        type_ = line[4]
        if type_ == "pareto":
            pass
        event = line[0]
        if event == 'r' and type_ != 'ack':
            totalBits1 += 8 * size
        time_ = float(line[1])
        size = int(line[5])
        if time_ - clock <= stamping_interval:
            pass
        else:
            th1 = float(totalBits1) / stamping_interval / (1024 * 1024)
            file.write("{},{}\n".format(clock,th1))
            clock += stamping_interval
            totalBits1 = 0

#cal_tmp(np_data,"throughput")

def display_throughput():
    ax = plt.gca()
    df = pd.read_csv("throughput.csv", delimiter=",", index_col=False)
    #print("=======Describe========")
    #print(df.describe())
    df.plot(marker="*", kind='line', x='time', y='thoughput1', color='red', ax=ax, label='All-Tcp-Streams')
    plt.ylabel("throughput(mbps)")
    plt.xlabel("time(s)")
    plt.title("Throughput evolution by time")
    plt.show()
display_throughput()
