# -*- coding:utf-8 -*-
#Start Command: ryu-manager ryuAddflow.py
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_3_parser

from ryu.lib.packet import ether_types
from ryu.lib.packet import in_proto as inet
 
class MyRyu(app_manager.RyuApp):
    #使用協定
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    #初始化
    def __init__(self, *args, **kwargs):
        super(MyRyu, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    #一開始Switch連上Controller時的初始設定Function
    def switch_features_handler(self, ev):
        # 接收 OpenFlow 交換器實例
        datapath = ev.msg.datapath
        self.send_port_stats_request(datapath)
 
    def send_port_stats_request(self, datapath):
        #OpenFlow 交換器使用的OF協定版本
        ofp = datapath.ofproto
        #處理OF協定的parser
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_ANY)
        #送回Switch
        datapath.send_msg(req)
 
    #對交換器的Flow Entry取得資料
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser


        #在此定義轉發規則

        '''
        #port轉發
        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(port=2)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=2)
        actions = [parser.OFPActionOutput(port=1)]
        self.add_flow(datapath, 0 ,match,actions)
        '''

        '''
        #mac轉發
        match = parser.OFPMatch(in_port=1,eth_src='00:00:00:00:00:01')
        actions = [parser.OFPActionOutput(port=2)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=2,eth_src='00:00:00:00:00:01')
        actions = [parser.OFPActionOutput(port=1)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=1,eth_src='00:00:00:00:00:02')
        actions = [parser.OFPActionOutput(port=2)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=2,eth_src='00:00:00:00:00:02')
        actions = [parser.OFPActionOutput(port=1)]
        self.add_flow(datapath, 0 ,match,actions)
        '''

        
        #ip轉發
        match = parser.OFPMatch(in_port=1,eth_type=0x806)
        actions = [parser.OFPActionOutput(port=2)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=2,eth_type=0x806)
        actions = [parser.OFPActionOutput(port=1)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=1,eth_type=0x800,ipv4_src='10.0.0.1')
        actions = [parser.OFPActionOutput(port=2)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=2,eth_type=0x800,ipv4_src='10.0.0.1')
        actions = [parser.OFPActionOutput(port=1)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=1,eth_type=0x800,ipv4_src='10.0.0.2')
        actions = [parser.OFPActionOutput(port=2)]
        self.add_flow(datapath, 0 ,match,actions)
        match = parser.OFPMatch(in_port=2,eth_type=0x800,ipv4_src='10.0.0.2')
        actions = [parser.OFPActionOutput(port=1)]
        self.add_flow(datapath, 0 ,match,actions)
        




    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        #規劃的動作
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        #產生一個Packet-Out事件
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        #將封包傳回至switch
        datapath.send_msg(mod)
