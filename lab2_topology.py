# -*- coding:utf-8 -*-
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController

if '__main__' == __name__:
	# 宣告 Mininet 使用的 Controller 種類
    net = Mininet(controller=RemoteController)
	
	# 指定 Controller 的 IP 及 Port，進行初始化
    c0 = net.addController('c0',ip='127.0.0.1', port=6633)
	
	# 加入 Switch
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    s5 = net.addSwitch('s5')
    s6 = net.addSwitch('s6')
    s7 = net.addSwitch('s7')
    s8 = net.addSwitch('s8')
	
	# 加入主機，並指定 MAC，ip
    h1 = net.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1')
    h2 = net.addHost('h2', mac='00:00:00:00:00:02', ip='10.0.0.2')
    h3 = net.addHost('h3', mac='00:00:00:00:00:03', ip='10.0.0.3')
    h4 = net.addHost('h4', mac='00:00:00:00:00:04', ip='10.0.0.4')
    h5 = net.addHost('h5', mac='00:00:00:00:00:05', ip='10.0.0.5')
    h6 = net.addHost('h6', mac='00:00:00:00:00:06', ip='10.0.0.6')
    h7 = net.addHost('h7', mac='00:00:00:00:00:07', ip='10.0.0.7')
    h8 = net.addHost('h8', mac='00:00:00:00:00:08', ip='10.0.0.8')
    h9 = net.addHost('h9', mac='00:00:00:00:00:09', ip='10.0.0.9')
	
	# 建立連線
    # Adding links between switches and hosts
    net.addLink(s1, h1, port1=1, port2=1)
    net.addLink(s3, h2, port1=1, port2=1)
    net.addLink(s6, h8, port1=1, port2=1)
    net.addLink(s7, h3, port1=1, port2=1)
    net.addLink(s5, h4, port1=1, port2=1)
    net.addLink(s5, h5, port1=2, port2=1)
    net.addLink(s8, h6, port1=1, port2=1)
    net.addLink(s8, h7, port1=2, port2=1)
    net.addLink(s4, h9, port1=1, port2=1)

    # Adding links between switches
    net.addLink(s1, s2, port1=2, port2=1)
    net.addLink(s1, s3, port1=3, port2=2)
    net.addLink(s2, s3, port1=2, port2=3)
    net.addLink(s2, s4, port1=3, port2=2)
    net.addLink(s2, s5, port1=4, port2=3)
    net.addLink(s2, s7, port1=5, port2=2)
    net.addLink(s3, s4, port1=4, port2=3)
    net.addLink(s5, s7, port1=4, port2=3)
    net.addLink(s5, s8, port1=5, port2=3)
    net.addLink(s6, s7, port1=2, port2=4)
    net.addLink(s1, s6, port1=4, port2=3)
    net.addLink(s4, s8, port1=4, port2=4)

    # 建立 Mininet
    net.build()
	
    # 啟動 Controller
    c0.start()
	
    # 啟動 Switch，並指定連結的 Controller 為 c0
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])
    s5.start([c0])
    s6.start([c0])
    s7.start([c0])
    s8.start([c0])



    # 執行互動介面(mininet>...)
    CLI(net)
	# 互動介面停止後，則結束 Mininet
    net.stop()