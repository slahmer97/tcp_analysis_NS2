set ns [new Simulator]
set f [open out.tr w]
$ns trace-all $f
set nf [open out.nam w]
$ns namtrace-all $nf
proc finish {} {
  global ns f nf
  $ns flush-trace
  close $nf
  exit 0
}

set am_nodes_count 12
set eu_border_f [$ns node]
set eu_border_m [$ns node]
$eu_border_f color blue
$eu_border_m color blue

set af_border_m [$ns node]
set af_border_e [$ns node]
$af_border_m color green
$af_border_e color green
set am_border_f [$ns node]
set am_border_e [$ns node]
$am_border_f color red
$am_border_e color red

for {set i 1} {$i <= $am_nodes_count } {incr i} {
	set am_node($i) [$ns node]
}
for {set i 1} {$i <= $am_nodes_count } {incr i} {
	for {set j [expr $i+1] } {$j <= $am_nodes_count } {incr j} {
		$ns duplex-link $am_node($i) $am_node($j) 100Mb 20ms DropTail
	}
	set tmp  [expr $i % 2]
	if { $tmp == 0} {
	                $ns duplex-link $am_node($i) $am_border_e 100Mb 20ms DropTail
	} else {
                $ns duplex-link $am_node($i) $am_border_f 100Mb 20ms DropTail
	}

}


$ns duplex-link $eu_border_f $af_border_e 100Mb 20ms DropTail
$ns duplex-link $eu_border_m $am_border_e 100Mb 20ms DropTail

$ns duplex-link $af_border_e $eu_border_f 100Mb 20ms DropTail
$ns duplex-link $af_border_m $am_border_f 100Mb 20ms DropTail

$ns duplex-link $am_border_f $af_border_m 100Mb 20ms DropTail
$ns duplex-link $am_border_e $eu_border_m 100Mb 20ms DropTail




$ns at 10.0 "finish"

$ns run
