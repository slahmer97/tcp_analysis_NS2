import time
import os
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np

file_d = "trace.data"
#with open(file_d, 'r+') as f:
#    content = f.read()
#    if "event time" not in content:
#        f.seek(0, 0)
#        f.write("event time from_node to_node ptype psize flags fid src_dest_addr seq_num pid" + '\n' + content)
print("[+] checked header")
pd_data = pd.read_csv(file_d, delimiter=",", index_col=False)
print("[+] read panda frame")
#np_data = pd_data.to_numpy()
print("[+] convert to numpy arr")


def filter_file(data):
    f = open("trace.data","w")
    f.write("event,time,from_node,to_node,ptype,psize,flags,fid,src_dest_addr,seq_num,pid\n")

    for line in data :
        if line[4] == "tcp":
            f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],line[9],line[10]))
    print("[+] data_filter done!")
#filter_file(np_data)

def cal_tmp(data, filename):
    totalBits1 = 0
    clock = 0.0
    stamping_interval = 0.01
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
#display_throughput()

def check_sim_data(data):    
    d = data.groupby(["from_node","to_node"])
    d = d.get_group((12,0))
    #pid_u = grp.pid.unique()
    tmp = d.loc[d.event == 'r']
    print(tmp.describe())
    pid_s = []
    tmp_np = tmp.to_numpy()
    total = 0
    for l in tmp_np:
        if l[10] in pid_s:
            pass
        pid_s.append(l[10])
        total += int(l[5])
    
    print(tmp)
    print(len(pid_s))
    print("sum : {}".format(total))

#check_sim_data(pd_data)

def check_sim_streams(data,from_,to_):
    d = data.groupby(["from_node","to_node"])
    d = d.get_group((from_,to_))
    streams = d.fid.unique()
    streams_count = len(streams)
    f = open("sim_streams_check_{}_{}.data".format(from_,to_),"w")
    f.write("stream_id,packet_count,total_size\n")
    print("streams count : {}".format(streams_count))
    for stream_id in streams:
        tmp_data = d.loc[d.fid == stream_id]
        total_size = tmp_data.loc[tmp_data.event == 'r'].psize.sum()
        pks_count = len(tmp_data.pid.unique())
        f.write("{},{},{}\n".format(stream_id,pks_count,total_size))

def display_check_sim_stream(from_,to_):
        pd_data = pd.read_csv("sim_streams_check_{}_{}.data".format(from_,to_))
        nw_data = pd_data.sort_values(['total_size'])
        size = nw_data.total_size.size
        x1 = []
        x2 = []
        for i in range(1,size+1):
            x1.append(i)
        plt.bar(x1,nw_data.total_size,label='stream size',color='r')
        #plt.bar(x2,nw_data.packet_count,label='packets count',color='c')
        plt.xlabel("stream")
        plt.ylabel("size (Byte)")
        plt.title("streams distribution {} -> {}".format(from_,to_))
        plt.legend()
        plt.show()
#check_sim_streams(pd_data,0,14)
display_check_sim_stream(0,14)


#check_sim_data(pd_data)

