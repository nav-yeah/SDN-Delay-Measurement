"""
Network Delay Measurement Controller - POX
- Learning switch (packet_in handling)
- Flow rule installation with match+action
- Delay logging between packet arrivals
- Handles 2 test scenarios: normal forwarding and blocked host
"""

from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, ipv4, icmp
from pox.lib.addresses import IPAddr
import time

log = core.getLogger()

# --- SCENARIO 2: Block this host (Firewall rule) ---
BLOCKED_IP = IPAddr("10.0.0.4")

class DelayMonitor(object):
    """
    One instance per switch.
    Implements learning switch + delay measurement + optional blocking.
    """

    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}
        self.packet_timestamps = {}  # track inter-packet gaps per src MAC

        # Listen for packets from this switch
        connection.addListeners(self)
        log.info("Switch %s connected", dpid_to_str(connection.dpid))

        # Install table-miss rule: send unknown packets to controller
        self._install_table_miss()

    def _install_table_miss(self):
        """Send all unmatched packets to controller (priority 0)."""
        msg = of.ofp_flow_mod()
        msg.priority = 0
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        self.connection.send(msg)

    def _block_host(self, blocked_ip):
        """Install a DROP rule for a specific IP (Scenario 2 - Firewall)."""
        msg = of.ofp_flow_mod()
        msg.priority = 100  # higher priority than forwarding rules
        msg.match.dl_type = 0x0800  # IPv4
        msg.match.nw_dst = blocked_ip
        # No actions = DROP
        self.connection.send(msg)
        log.info("BLOCKED: traffic to %s will be dropped", blocked_ip)

    def _forward(self, packet, packet_in, out_port):
        """Install a flow rule and send the current packet."""
        # Install flow rule
        msg = of.ofp_flow_mod()
        msg.priority = 10
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.match = of.ofp_match.from_packet(packet, packet_in.in_port)
        msg.actions.append(of.ofp_action_output(port=out_port))
        msg.data = packet_in
        self.connection.send(msg)

    def _flood(self, packet_in):
        """Flood packet to all ports."""
        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.data = packet_in
        self.connection.send(msg)

    def _measure_delay(self, src_mac):
        """Log inter-packet arrival gap as a delay indicator."""
        now = time.time()
        key = str(src_mac)
        if key in self.packet_timestamps:
            gap = (now - self.packet_timestamps[key]) * 1000
            log.info("DELAY | switch=%s src=%s gap=%.3f ms",
                     dpid_to_str(self.connection.dpid), src_mac, gap)
        self.packet_timestamps[key] = now

    def _handle_PacketIn(self, event):
        """Main packet_in handler - core SDN logic."""
        packet = event.parsed
        if not packet.parsed:
            return

        src_mac = packet.src
        dst_mac = packet.dst
        in_port = event.port

        # Measure delay
        self._measure_delay(src_mac)

        # Learn MAC -> port mapping
        self.mac_to_port[src_mac] = in_port

        # --- SCENARIO 2: Block BLOCKED_IP ---
        ip_pkt = packet.find('ipv4')
        if ip_pkt and ip_pkt.dstip == BLOCKED_IP:
            log.info("FIREWALL: dropping packet destined to %s", BLOCKED_IP)
            return  # drop silently

        # Decide output port
        if dst_mac in self.mac_to_port:
            out_port = self.mac_to_port[dst_mac]
            log.info("FORWARD | switch=%s %s -> %s port %s",
                     dpid_to_str(self.connection.dpid),
                     src_mac, dst_mac, out_port)
            self._forward(packet, event.ofp, out_port)
        else:
            log.info("FLOOD   | switch=%s dst=%s unknown",
                     dpid_to_str(self.connection.dpid), dst_mac)
            self._flood(event.ofp)


class DelayMonitorLauncher(object):
    """Launches DelayMonitor for each switch that connects."""

    def __init__(self):
        core.openflow.addListeners(self)
        log.info("Delay Monitor Controller started")
        log.info("Scenario 1: Normal forwarding with delay measurement")
        log.info("Scenario 2: Traffic to %s will be BLOCKED", BLOCKED_IP)

    def _handle_ConnectionUp(self, event):
        DelayMonitor(event.connection)


def launch():
    core.registerNew(DelayMonitorLauncher)
