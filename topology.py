#!/usr/bin/env python3
"""
Network Delay Measurement - Mininet Topology
4 hosts, 2 switches, linear arrangement to allow path comparison
"""

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.link import TCLink

class DelayTopo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')

        # h1, h2 connect to s1
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        # h3, h4 connect to s2
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        # s1 <-> s2 (inter-switch link)
        self.addLink(s1, s2)

if __name__ == '__main__':
    setLogLevel('info')
    topo = DelayTopo()
    net = Mininet(topo=topo,
                  controller=RemoteController,
                  link=TCLink)
    net.start()
    info('*** Topology started\n')
    info('*** Hosts: h1=10.0.0.1, h2=10.0.0.2, h3=10.0.0.3, h4=10.0.0.4\n')
    net.interact()
    net.stop()
