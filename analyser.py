import time
import os
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import sys
file_d = "trace.data"
#with open(file_d, 'r+') as f:
#    content = f.read()
#    if "event time" not in content:
#        f.seek(0, 0)
#        f.write("event time from_node to_node ptype psize flags fid src_dest_addr seq_num pid" + '\n' + content)
print("[+] checked header")
#pd_data = pd.read_csv(file_d, delimiter=",", index_col=False)
print("[+] read panda frame")
#np_data = pd_data.to_numpy()
print("[+] convert to numpy arr")


def filter_file(filez="out.tr"):
    f = open("trace.data","w")
    f.write("event,time,from_node,to_node,ptype,psize,flags,fid,src_dest_addr,seq_num,pid\n")
    data = open(filez,"r")
    for l in data :
        stripped = l.strip()
        if not stripped :
            continue
        else :
            line = l.split(" ")
        if line[4] == "tcp":
            f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],line[9],line[10]))
    print("[+] data_filter done!")
#filter_file()
#sys.exit(1)
def cal_tmp(data, filename):
    totalBits1 = 0
    clock = 0.0
    stamping_interval = 0.1
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

#cal_tmp(np_data,"throughput_drr")
#sys.exit(0)
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
    ss = 0
    print("streams count : {}".format(streams_count))
    for stream_id in streams:
        tmp_data = d.loc[d.fid == stream_id]
        total_size = tmp_data.loc[tmp_data.event == 'r'].psize.sum()
        pks_count = len(tmp_data.pid.unique())
        ss += total_size
        f.write("{},{},{}\n".format(stream_id,pks_count,total_size))
    print("total data quantity : {}".format(ss))   
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
#check_sim_streams(pd_data,0,8)
#display_check_sim_stream(0,14)


#check_sim_data(pd_data)


def stream_throughaput(data_,stream_id):
    time_stamping = []
    d = data_.groupby('fid')
    pd_df = pd.DataFrame({})
    tmp = []
    totalBits1 = 0
    clock = 0.0
    stamping_interval = 0.1
    tmp_group = d.get_group(stream_id).to_numpy()
    for line in tmp_group:
        event = line[0]
        time_ = float(line[1])
        type_ = line[4]
        size = int(line[5])
        if event == 'r' : # we don't check if we have ack, we are sure that we have just tcp in our file
            totalBits1 += 8 * size
        if time_ - clock <= stamping_interval:
            pass
        else:
            th1 = float(totalBits1) / stamping_interval / (1024 * 1024)
            # print(str(clock) + "\t" + str(th1))
            time_stamping.append(clock)
            tmp.append(th1)
            clock += stamping_interval
            totalBits1 = 0
    pd_df["time"] = time_stamping
    pd_df["s_{}".format(i)] = tmp
    pd_df.to_csv("stream_{}.csv".format(stream_id),index=None,header=True)
#inner_stream_stat(pd_data,20010)

def display_queue_type_comp():
    ax = plt.gca()
    pd_cbq = pd.read_csv("throughput_cbq.csv")
    pd_red = pd.read_csv("throughput_red.csv")
    pd_drr = pd.read_csv("throughput_drr.csv")
    pd_fq = pd.read_csv("throughput_fq.csv")
    pd_dp = pd.read_csv("throughput_drop_tail.csv")
    df =pd.DataFrame({})
    df["time"] = pd_cbq.time
    df["th_cbq"] = pd_cbq.thoughput1
    df["th_red"] = pd_red.thoughput1
    df["th_drr"] = pd_drr.thoughput1
    df["th_fq"] = pd_fq.thoughput1
    df["th_dt"] = pd_dp.thoughput1


    pd_drop_tail = pd.read_csv("throughput_drop_tail.csv")
    df.plot(marker="*", kind='line', x='time', y='th_cbq', color='b', ax=ax, label='Queue=cbq')
    df.plot(marker="*", kind='line', x='time', y='th_red', color='g', ax=ax, label='Queue=red')
    df.plot(marker="*", kind='line', x='time', y='th_drr', color='r', ax=ax, label='Queue=drr')
    df.plot(marker="*", kind='line', x='time', y='th_fq', color='c', ax=ax, label='Queue=fq')
    df.plot(marker="*", kind='line', x='time', y='th_dt', color='m', ax=ax, label='Queue=DropTail')


    plt.ylabel("throughput(mbps)")
    plt.xlabel("time(s)")
    plt.title("Throughput evolution by time")
    plt.show()
    
display_queue_type_comp()
