from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.topology.api import get_switch, get_link
from ryu.topology import event
import networkx as nx

class DualPathRouting(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DualPathRouting, self).__init__(*args, **kwargs)
        self.network = nx.DiGraph()  # Use networkx for graph representation
        self.mac_to_port = {}        # MAC address to port mapping

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        # Build the network topology graph
        switches = get_switch(self, None)
        links = get_link(self, None)

        for switch in switches:
            self.network.add_node(switch.dp.id)

        for link in links:
            self.network.add_edge(link.src.dpid, link.dst.dpid, port=link.src.port)
            self.network.add_edge(link.dst.dpid, link.src.dpid, port=link.dst.port)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # Learn MAC address
        self.mac_to_port[dpid][src] = in_port

        # If destination MAC is known, route the packet
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            # Compute dual paths
            if src in self.network.nodes and dst in self.network.nodes:
                primary_path, backup_path = self.compute_dual_paths(src, dst)
                self.logger.info(f"Primary Path: {primary_path}")
                self.logger.info(f"Backup Path: {backup_path}")
                
                # Install flow rules for primary and backup paths
                self.install_path(primary_path, parser, datapath)
                self.install_path(backup_path, parser, datapath)

                # Forward the packet
                out_port = self.get_next_hop_port(primary_path, dpid)
            else:
                out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]
        data = None if msg.buffer_id == ofproto.OFP_NO_BUFFER else msg.data

        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data)
        datapath.send_msg(out)

    def compute_dual_paths(self, src, dst):
        """
        Compute two disjoint paths using NetworkX.
        """
        try:
            primary_path = nx.shortest_path(self.network, src, dst, weight='weight')
            backup_path = nx.shortest_path(self.network, src, dst, weight='weight', method='dijkstra', disjoint=True)
        except nx.NetworkXNoPath:
            primary_path = []
            backup_path = []
        return primary_path, backup_path

    def install_path(self, path, parser, datapath):
        """
        Install flow rules along the given path.
        """
        for i in range(len(path) - 1):
            src_switch = path[i]
            dst_switch = path[i + 1]
            out_port = self.network[src_switch][dst_switch]['port']

            match = parser.OFPMatch(in_port=src_switch)
            actions = [parser.OFPActionOutput(out_port)]

            # Send flow mod message
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
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)
