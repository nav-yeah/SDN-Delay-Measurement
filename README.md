# SDN Network Delay Measurement Tool

## Problem Statement
Measure and analyze network latency between hosts in a Software Defined Network (SDN) 
using Mininet and POX controller. The tool demonstrates how an SDN controller can 
observe, log, and compare delay across different network paths.

## Objectives
- Use ping for delay measurement between hosts
- Record RTT (Round Trip Time) values
- Compare delay across different paths (same switch vs cross-switch)
- Analyze delay variations using controller logs

## Network Topology
h1 (10.0.0.1) ─┐         ┌─ h3 (10.0.0.3)
s1 ─────s2
h2 (10.0.0.2) ─┘         └─ h4 (10.0.0.4) [BLOCKED]

- 4 hosts, 2 switches
- h1, h2 connect to s1 (same switch = shorter path)
- h3, h4 connect to s2 (cross-switch = longer path)
- POX controller manages flow rules via OpenFlow

## Setup & Installation

### Requirements
- Ubuntu 20.04/22.04 or WSL2
- Python 3.10
- Mininet
- POX controller

### Install Mininet
```bash
sudo apt update
sudo apt install mininet -y
sudo service openvswitch-switch start
```

### Install POX
```bash
cd ~
git clone https://github.com/noxrepo/pox.git
```

### Clone this repo
```bash
git clone https://github.com/nav-yeah/sdn-delay-measurement.git
cd sdn-delay-measurement
cp delay_monitor.py ~/pox/pox/ext/
```

## How to Run

### Terminal 1 — Start POX Controller
```bash
cd ~/pox
python3 pox.py log.level --DEBUG ext.delay_monitor
```

### Terminal 2 — Start Mininet
```bash
sudo service openvswitch-switch start
sudo python3 topology.py
```

## Test Scenarios

### Scenario 1 — Normal Forwarding & Delay Measurement

mininet> h1 ping -c 10 h2
mininet> h1 ping -c 10 h3
mininet> sh ovs-ofctl dump-flows s1
mininet> sh ovs-ofctl dump-flows s2

**Expected:** h1→h2 shows lower RTT (same switch). h1→h3 shows higher RTT (cross-switch).

### Scenario 2 — Blocked Host (Firewall Rule)
mininet> h1 ping -c 4 h4
**Expected:** 100% packet loss. Controller drops all traffic to h4.

### Throughput Test
mininet> h3 iperf -s &
mininet> h1 iperf -c h3
**Expected:** Bandwidth measurement between h1 and h3.

## Expected Output

### Ping Results
- h1 → h2 (same switch): RTT ~0.1-0.5ms
- h1 → h3 (cross-switch): RTT ~0.3-1.0ms (higher due to extra hop)
- h1 → h4 (blocked): 100% packet loss

### POX Controller Logs
INFO:delay_monitor:Delay Monitor Controller started
INFO:delay_monitor:DELAY | switch=00-00-00-00-00-01 src=xx:xx gap=0.664 ms
INFO:delay_monitor:FORWARD | switch=00-00-00-00-00-01 xx -> xx port 2
INFO:delay_monitor:FIREWALL: dropping packet destined to 10.0.0.4

### Flow Table (ovs-ofctl dump-flows s1)
Shows installed OpenFlow rules with match fields, actions, priority, and packet counts.

## SDN Concepts Demonstrated
- **Controller-Switch Interaction:** POX handles packet_in events from both switches
- **Flow Rule Design:** Match on MAC/IP, action = forward or drop
- **Learning Switch:** Controller learns MAC-to-port mapping dynamically
- **Firewall:** High-priority drop rule for blocked host
- **Delay Measurement:** Inter-packet gap logged per source MAC per switch

## References
1. Mininet Documentation: http://mininet.org
2. POX Controller: https://github.com/noxrepo/pox
3. OpenFlow Specification v1.0: https://opennetworking.org
4. Lantz, B., Heller, B., McKeown, N. (2010). A network in a laptop. ACM HotNets-IX.
