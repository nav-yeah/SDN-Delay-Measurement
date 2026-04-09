# SDN Network Delay Measurement Tool

## Problem Statement
Measure and analyze network latency between hosts in a Software Defined Network (SDN)  
using Mininet and POX controller. The tool demonstrates how an SDN controller can  
observe, log, and compare delay across different network paths.

---

## Objectives
- Use ping for delay measurement between hosts  
- Record RTT (Round Trip Time) values  
- Compare delay across different paths (same switch vs cross-switch)  
- Analyze delay variations using controller logs  

---

## Network Topology
```
h1 (10.0.0.1) ─┐         ┌─ h3 (10.0.0.3)
               s1 ───── s2
h2 (10.0.0.2) ─┘         └─ h4 (10.0.0.4) [BLOCKED]
```

- 4 hosts, 2 switches  
- h1, h2 connect to s1 (same switch = shorter path)  
- h3, h4 connect to s2 (cross-switch = longer path)  
- POX controller manages flow rules via OpenFlow  

---

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
git clone https://github.com/nav-yeah/SDN-Delay-Measurement.git
cd SDN-Delay-Measurement
cp delay_monitor.py ~/pox/pox/ext/
```

---

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

---

## Test Scenarios

### Scenario 1 — Normal Forwarding and Delay Measurement
```bash
mininet> h1 ping -c 10 h2
mininet> h1 ping -c 10 h3
mininet> sh ovs-ofctl dump-flows s1
mininet> sh ovs-ofctl dump-flows s2
```

**Expected:**  
h1 to h2 shows lower RTT (same switch).  
h1 to h3 shows higher RTT (cross-switch).

---

### Scenario 2 — Blocked Host (Firewall Rule)
```bash
mininet> h1 ping -c 4 h4
```

**Expected:**  
100% packet loss. Controller drops all traffic destined to h4.

---

### Throughput Test
```bash
mininet> h3 iperf -s &
mininet> h1 iperf -c h3
```

**Expected:**  
Bandwidth measurement between h1 and h3 via cross-switch path.

---

### Regression Validation
```bash
mininet> h1 ping -c 3 h2
mininet> h1 ping -c 3 h2
mininet> h1 ping -c 3 h2
```

**Expected:**  
Consistent RTT values across all three runs, proving repeatability.

---

## Proof of Execution

### 1. POX Controller Started
<img width="1919" height="939" alt="Screenshot 2026-04-09 103034" src="https://github.com/user-attachments/assets/1fde6e3c-fd1d-4ee9-b7a8-a867f0d442aa" />

---

### 2. Mininet Topology Started
<img width="1912" height="963" alt="Screenshot 2026-04-09 103112" src="https://github.com/user-attachments/assets/f333ea3f-dd3a-41a4-8d2e-54af3d1e32b5" />

---

## Ping Results

### 3. Scenario 1a — h1 to h2 (same switch, lower RTT)
<img width="961" height="502" alt="Screenshot 2026-04-09 103342" src="https://github.com/user-attachments/assets/49ba8401-5adf-4106-90ef-54b5535501e0" />

---

### 4. Scenario 1b — h1 to h3 (cross-switch, higher RTT)
<img width="996" height="488" alt="Screenshot 2026-04-09 103434" src="https://github.com/user-attachments/assets/a9f8b2ed-7e2f-4177-b693-ff0674da2565" />

---

## Controller Logs

### 5. POX Delay and Forward Logs
<img width="1574" height="1001" alt="Screenshot 2026-04-09 103543" src="https://github.com/user-attachments/assets/ac78c54c-d820-4053-aa8b-545283ee20b4" />

---

## Flow Tables

### 6. Flow Tables — Switch s1 and s2
<img width="1516" height="175" alt="Screenshot 2026-04-09 103631" src="https://github.com/user-attachments/assets/5231874a-f560-4bb4-b82e-a5dc6cecd6a6" />

---

## Scenario 2 — Blocked Host

### 7. h1 ping h4 — 100% Packet Loss
<img width="972" height="226" alt="Screenshot 2026-04-09 103716" src="https://github.com/user-attachments/assets/7efa33c1-aae6-454d-89c9-404bb0956016" />
<img width="1463" height="320" alt="Screenshot 2026-04-09 103802" src="https://github.com/user-attachments/assets/4036be0e-c05d-43b5-b00f-f71a545e8b6e" />

---

## Throughput

### 8. iperf Bandwidth Measurement h1 to h3
<img width="1364" height="318" alt="Screenshot 2026-04-09 103912" src="https://github.com/user-attachments/assets/ac0bf15a-9c85-4431-a08c-ddcf5911a000" />

---

## SDN Concepts Demonstrated
- **Controller-Switch Interaction:** POX handles packet_in events from both switches  
- **Flow Rule Design:** Match on MAC/IP, action = forward or drop  
- **Learning Switch:** Controller learns MAC-to-port mapping dynamically  
- **Firewall:** High-priority drop rule for blocked host (h4)  
- **Delay Measurement:** Inter-packet gap logged per source MAC per switch  
- **Path Comparison:** Same-switch path vs cross-switch path RTT comparison  

---

## References
1. Mininet Documentation: http://mininet.org  
2. POX Controller: https://github.com/noxrepo/pox  
3. OpenFlow Specification v1.0: https://opennetworking.org  
4. Lantz, B., Heller, B., McKeown, N. (2010). A network in a laptop. ACM HotNets-IX.
