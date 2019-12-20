routers_america = 12
routers_europe = 12
routers_africa = 10
n = routers_america + routers_europe + routers_africa

fileTCL = open("topo.tcl", "w")

fileTCL.write("set rate 10Mb\n")
fileTCL.write("set delay 10ms\n")
fileTCL.write("set queue_type DropTail\n")
fileTCL.write("set queue_size 20\n")

fileTCL.write("\nset c_rate 10Mb\n")
fileTCL.write("set c_delay 10ms\n")
fileTCL.write("set c_queue_type DropTail\n")
fileTCL.write("set c_queue_size 20\n")

fileTCL.write("""
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
for r in c_routers:
    fileTCL.write("set %s [$ns node]\n" % r)

for i in range(1, n + 1):
    fileTCL.write("set nodes(%d) [$ns node]\n" % i)

fileTCL.write("$ns duplex-link $AmEu $EuAm $c_rate $c_delay $c_queue_type\n")
fileTCL.write("$ns queue-limit $AmEu $EuAm $c_queue_size\n")
fileTCL.write("$ns duplex-link $AmAf $AfAm $c_rate $c_delay $c_queue_type\n")
fileTCL.write("$ns queue-limit $AmAf $AfAm $c_queue_size\n")
fileTCL.write("$ns duplex-link $EuAf $AfEu $c_rate $c_delay $c_queue_type\n")
fileTCL.write("$ns queue-limit $EuAf $AfEu $c_queue_size\n")

starting_router = 1
for i in range(starting_router, routers_america + starting_router):
    for j in range(i + 1, routers_america + starting_router):
        fileTCL.write("$ns duplex-link $nodes(%d) $nodes(%d) $rate $delay $queue_type\n" % (i, j))
        fileTCL.write("$ns queue-limit $nodes(%d) $nodes(%d) $queue_size\n" % (i, j))
    if i % 2 == 0:
        fileTCL.write("$ns duplex-link $nodes(%d) $AmEu $rate $delay $queue_type\n" % i)
        fileTCL.write("$ns queue-limit $nodes(%d) $AmEu $queue_size\n" % i)
    else:
        fileTCL.write("$ns duplex-link $nodes(%d) $AmAf $rate $delay $queue_type\n" % i)
        fileTCL.write("$ns queue-limit $nodes(%d) $AmAf $queue_size\n" % i)

starting_router += routers_america
for i in range(starting_router, routers_europe + starting_router):
    mod = i % 5
    for j in range(i + 1, routers_europe + starting_router):
        if j % 5 == mod:
            fileTCL.write("$ns duplex-link $nodes(%d) $nodes(%d) $rate $delay $queue_type\n" % (i, j))
            fileTCL.write("$ns queue-limit $nodes(%d) $nodes(%d) $queue_size\n" % (i, j))
    if i % 2 == 0:
        fileTCL.write("$ns duplex-link $nodes(%d) $EuAm $rate $delay $queue_type\n" % i)
        fileTCL.write("$ns queue-limit $nodes(%d) $EuAm $queue_size\n" % i)
    else:
        fileTCL.write("$ns duplex-link $nodes(%d) $EuAf $rate $delay $queue_type\n" % i)
        fileTCL.write("$ns queue-limit $nodes(%d) $EuAf $queue_size\n" % i)

starting_router += routers_europe
for i in range(starting_router, routers_africa + starting_router):
    mod = i % 3
    for j in range(i + 1, routers_africa + starting_router):
        if j % 3 == mod:
            fileTCL.write("$ns duplex-link $nodes(%d) $nodes(%d) $rate $delay $queue_type\n" % (i, j))
            fileTCL.write("$ns queue-limit $nodes(%d) $nodes(%d) $queue_size\n" % (i, j))
    if i % 2 == 0:
        fileTCL.write("$ns duplex-link $nodes(%d) $AfAm $rate $delay $queue_type\n" % i)
        fileTCL.write("$ns queue-limit $nodes(%d) $AfAm $queue_size\n" % i)
    else:
        fileTCL.write("$ns duplex-link $nodes(%d) $AfEu $rate $delay $queue_type\n" % i)
        fileTCL.write("$ns queue-limit $nodes(%d) $AfEu $queue_size\n" % i)

fileTCL.write("""
$ns at 10.0 "finish"
$ns run
""")
