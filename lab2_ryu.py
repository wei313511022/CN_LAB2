from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.topology.api import get_switch, get_link
from ryu.topology import event
from ryu.lib.packet import packet, ethernet, ipv4, arp
import networkx as nx
from ryu.controller import dpset



class IPBasedRouting(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(IPBasedRouting, self).__init__(*args, **kwargs)
        self.network = nx.DiGraph()  # Graph for network topology
        self.ip_to_port = {}         # IP address to port mapping
        self.datapaths = {}          # Datapaths for switches

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        # Discover network topology
        switches = get_switch(self, None)
        links = get_link(self, None)
        print(links)

        for switch in switches:
            self.network.add_node(switch.dp.id)

        for link in links:
            self.network.add_edge(link.src.dpid, link.dst.dpid, port=link.src.port)
            self.network.add_edge(link.dst.dpid, link.src.dpid, port=link.dst.port)

        self.logger.info(f"Discovered switches: {list(self.network.nodes)}")
        self.logger.info(f"Discovered links: {list(self.network.edges)}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)

        dpid = datapath.id
        self.ip_to_port.setdefault(dpid, {})

        # Handle ARP packets by learning and responding
        if arp_pkt:
            self.handle_arp(arp_pkt, datapath, in_port, parser, ofproto, msg.data)
            return

        # Handle IP packets
        if ip_pkt:
            src_ip = ip_pkt.src
            dst_ip = ip_pkt.dst

            # Learn the source IP and port
            self.ip_to_port[dpid][src_ip] = in_port

            # If destination IP is known, route the packet
            if dst_ip in self.ip_to_port[dpid]:
                out_port = self.ip_to_port[dpid][dst_ip]
            else:
                # Compute paths and install flow rules
                if src_ip in self.network.nodes and dst_ip in self.network.nodes:
                    primary_path, backup_path = self.compute_dual_paths(src_ip, dst_ip)
                    self.logger.info(f"Primary Path: {primary_path}")
                    self.logger.info(f"Backup Path: {backup_path}")
                    datapaths = {dp.id: dp for dp in self.datapaths.values()}
                    self.install_path(primary_path, parser, datapaths)
                    self.install_path(backup_path, parser, datapaths)
                    out_port = self.get_next_hop_port(primary_path, dpid)
                else:
                    out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]
            data = None if msg.buffer_id == ofproto.OFP_NO_BUFFER else msg.data
            out = parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions, data=data
            )
            datapath.send_msg(out)

    def handle_arp(self, arp_pkt, datapath, in_port, parser, ofproto, data):
        """
        Handle ARP packets by learning IP-MAC mapping and flooding.
        """
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
            in_port=in_port, actions=actions, data=data
        )
        datapath.send_msg(out)

    def compute_dual_paths(self, src, dst):
        """
        Compute two disjoint paths using NetworkX.
        """
        try:
            primary_path = nx.shortest_path(self.network, src, dst, weight='weight')
            backup_graph = self.network.copy()
            nx.utils.remove_path(backup_graph, primary_path)
            backup_path = nx.shortest_path(backup_graph, src, dst, weight='weight')
        except nx.NetworkXNoPath:
            primary_path = []
            backup_path = []
        return primary_path, backup_path

    def install_path(self, path, parser, datapaths):
        """
        Install flow rules along a given path.
        """
        for i in range(len(path) - 1):
            src_switch = path[i]
            dst_switch = path[i + 1]
            out_port = self.network[src_switch][dst_switch]['port']
            in_port = self.network[dst_switch][src_switch]['port']

            datapath = datapaths[src_switch]
            match = parser.OFPMatch(in_port=in_port)
            actions = [parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 1, match, actions)

    def get_next_hop_port(self, path, dpid):
        """
        Get the output port for the next hop along the path.
        """
        if dpid in path:
            idx = path.index(dpid)
            if idx + 1 < len(path):
                next_hop = path[idx + 1]
                return self.network[dpid][next_hop]['port']
        return None

    def add_flow(self, datapath, priority, match, actions):
        """
        Add a flow rule to the switch.
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)
