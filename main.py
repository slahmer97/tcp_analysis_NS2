from tmgen.models import uniform_tm
import numpy as np
import sys
from scipy.stats import poisson as poi
import random as rand
import random
import math
from statistics import mean

simulation_duration = 10.0
out = open("tp.tcl", "w")
mean_size = 10000000


def gen_traffic_matrix(file_="traffic_matrix.data"):
    tm = uniform_tm(34, mean_size, 1).matrix
    res = []
    for i in range(len(tm)):
        line = tm[i]
        tmp = []
        for j in range(len(line)):
            if (i == j) or (i < 12 and j < 12) or (12 <= i < 24 and 12 <= j < 24) or (i >= 24 and j >= 24):
                tmp.append(0)
            else:
                tmp.append(line[j][0])
            # print ("{} ".format(line[j][0]))
        # print ("=========")
        res.append(tmp)
        tmp = []
    np.savetxt('traffic_matrix.data', res, delimiter=',', fmt='%4.3e')


# =============================

out.write("""
proc randomColor {} {format #%06x [expr {int(rand() * 0xFFFFFF)}]}
""")


def gen_traffic(traff_mat="traffic_matrix.data", burst_time=0.5, idle_time=0.5, shape=1.1, packet_size=1500):
    matrix = np.loadtxt(traff_mat, delimiter=",")
    dim = len(matrix)
    fid = 0
    for i in range(dim):
        for j in range(dim):
            print("{},{} : ".format(i, j))
            total_quantity = int(matrix[i][j])
            if total_quantity <= 0:
                continue
            from_ = i
            to_ = j
            tcp_quantity = 0.2 * total_quantity
            on_off_noise = total_quantity - tcp_quantity

            pareto_rate = 2 * (on_off_noise / simulation_duration)
            pareto_burst_time = burst_time
            pareto_idle_time = idle_time
            pareto_shape = 1.1

            out.write("set UDP_GENN_{}_{} [new Agent/UDP]\n".format(from_, to_))
            out.write("set UDP_NULL_{}_{} [new Agent/Null]\n".format(from_, to_))

            out.write("$ns attach-agent $nodes({}) $UDP_GENN_{}_{}\n".format(from_, from_, to_))
            out.write("$ns attach-agent $nodes({}) $UDP_NULL_{}_{}\n".format(to_, from_, to_))

            out.write("set TPGEN_{}_{} [new Application/Traffic/Pareto]\n".format(from_, to_))
            out.write("$TPGEN_{}_{} set idle_time_ {}s \n".format(from_, to_, pareto_idle_time))
            out.write("$TPGEN_{}_{} set burst_time_ {}s \n".format(from_, to_, pareto_burst_time))
            out.write("$TPGEN_{}_{} set shape_ {} \n".format(from_, to_, pareto_shape))
            out.write("$TPGEN_{}_{} set rate_ {} \n".format(from_, to_, pareto_rate))
            out.write("$TPGEN_{}_{} set packetSize_ {} \n".format(from_, to_, 1500))

            out.write("$TPGEN_{}_{} attach-agent $UDP_GENN_{}_{}\n".format(from_, to_, from_, to_))
            out.write("$ns connect $UDP_GENN_{}_{} $UDP_NULL_{}_{} \n".format(from_, to_, from_, to_))
            out.write("$ns at 0 {}$TPGEN_{}_{} start{}\n".format('"', from_, to_, '"'))

            streams = fstreams(tcp_quantity)
            stream_id = 0
            for s in streams:
                gen_time = rand.uniform(0.1, simulation_duration-1)
                out.write("set TCP_AGENT({}.{}.{}) [new Agent/TCP]\n".format(from_, to_, stream_id))
                out.write("$TCP_AGENT({}.{}.{}) set packetSize_ {}\n".format(from_, to_, stream_id, packet_size))
                id_ = fid*1000+stream_id
                out.write("$TCP_AGENT({}.{}.{}) set fid_ {}\n".format(from_, to_, stream_id, id_))
                out.write("set tcp_receiver({}.{}.{}) [new Agent/TCPSink]\n".format(from_, to_, stream_id))
                out.write("$ns attach-agent $nodes({}) $TCP_AGENT({}.{}.{})\n".format(from_, from_, to_, stream_id))
                out.write("$ns attach-agent $nodes({}) $tcp_receiver({}.{}.{})\n".format(to_, from_, to_, stream_id))
                out.write(
                    "$ns connect $TCP_AGENT({}.{}.{}) $tcp_receiver({}.{}.{})\n".format(from_, to_, stream_id, from_,
                                                                                        to_, stream_id))
                out.write("$ns at {} \"$TCP_AGENT({}.{}.{}) send {}\"\n".format(gen_time, from_, to_, stream_id, s))
                stream_id += 1
            fid += 1


def fstreams(total_quantity, min_size=15 * 1000):
    s = 0.0
    strms = []
    while s < total_quantity:
        u = random.random()
        k = math.log(4) / math.log(5)
        t = min_size / (u ** (1 / k))
        s += t
        strms.append(t)

    d = sum(strms) - total_quantity
    strms[-1] -= d
    return strms


gen_traffic_matrix()

# ==========================================
routers_america = 12
routers_europe = 12
routers_africa = 10
n = routers_america + routers_europe + routers_africa

out.write("set rate 500Mb\n")
out.write("set delay 20ms\n")
out.write("set queue_type DropTail\n")
out.write("set queue_size 30\n")

out.write("\nset c_rate 250Mb\n")
out.write("set c_delay 50ms\n")
out.write("set c_queue_type DropTail\n")
out.write("set c_queue_size 30\n")

out.write("""
set ns [new Simulator]
set f [open out.tr w]
$ns trace-all $f
set nf [open out.nam w]
$ns namtrace-all $nf
proc finish {} {
  global ns f nf
  $ns flush-trace
  close $f
  close $nf
  exit 0
}
""")

c_routers = ["AmEu", "AmAf", "EuAm", "EuAf", "AfAm", "AfEu"]
c_routers_col = ["blue", "blue", "green", "green", "red", "red"]
i = 0
for r in c_routers:
    out.write("set %s [$ns node]\n" % r)
    out.write("${} color {} \n".format(r, c_routers_col[i]))
    i += 1

for i in range(n):
    out.write("set nodes(%d) [$ns node]\n" % i)

out.write("$ns duplex-link $AmEu $EuAm $c_rate $c_delay $c_queue_type\n")
out.write("$ns queue-limit $AmEu $EuAm $c_queue_size\n")
out.write("$ns duplex-link $AmAf $AfAm $c_rate $c_delay $c_queue_type\n")
out.write("$ns queue-limit $AmAf $AfAm $c_queue_size\n")
out.write("$ns duplex-link $EuAf $AfEu $c_rate $c_delay $c_queue_type\n")
out.write("$ns queue-limit $EuAf $AfEu $c_queue_size\n")

starting_router = 0
for i in range(starting_router, routers_america + starting_router):
    for j in range(i + 1, routers_america + starting_router):
        out.write("$ns duplex-link $nodes(%d) $nodes(%d) $rate $delay $queue_type\n" % (i, j))
        out.write("$ns queue-limit $nodes(%d) $nodes(%d) $queue_size\n" % (i, j))
    if i % 2 == 0:
        out.write("$ns duplex-link $nodes(%d) $AmEu $rate $delay $queue_type\n" % i)
        out.write("$ns queue-limit $nodes(%d) $AmEu $queue_size\n" % i)
    else:
        out.write("$ns duplex-link $nodes(%d) $AmAf $rate $delay $queue_type\n" % i)
        out.write("$ns queue-limit $nodes(%d) $AmAf $queue_size\n" % i)

starting_router += routers_america
for i in range(starting_router, routers_europe + starting_router):
    mod = i % 5
    for j in range(i + 1, routers_europe + starting_router):
        if j % 5 == mod:
            out.write("$ns duplex-link $nodes(%d) $nodes(%d) $rate $delay $queue_type\n" % (i, j))
            out.write("$ns queue-limit $nodes(%d) $nodes(%d) $queue_size\n" % (i, j))
    if i % 2 == 0:
        out.write("$ns duplex-link $nodes(%d) $EuAm $rate $delay $queue_type\n" % i)
        out.write("$ns queue-limit $nodes(%d) $EuAm $queue_size\n" % i)
    else:
        out.write("$ns duplex-link $nodes(%d) $EuAf $rate $delay $queue_type\n" % i)
        out.write("$ns queue-limit $nodes(%d) $EuAf $queue_size\n" % i)

starting_router += routers_europe
for i in range(starting_router, routers_africa + starting_router):
    mod = i % 3
    for j in range(i + 1, routers_africa + starting_router):
        if j % 3 == mod:
            out.write("$ns duplex-link $nodes(%d) $nodes(%d) $rate $delay $queue_type\n" % (i, j))
            out.write("$ns queue-limit $nodes(%d) $nodes(%d) $queue_size\n" % (i, j))
    if i % 2 == 0:
        out.write("$ns duplex-link $nodes(%d) $AfAm $rate $delay $queue_type\n" % i)
        out.write("$ns queue-limit $nodes(%d) $AfAm $queue_size\n" % i)
    else:
        out.write("$ns duplex-link $nodes(%d) $AfEu $rate $delay $queue_type\n" % i)
        out.write("$ns queue-limit $nodes(%d) $AfEu $queue_size\n" % i)

# ======================

gen_traffic()

# =====================
out.write("""
$ns at %f "finish"
$ns run
""" % simulation_duration)

