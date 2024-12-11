from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def createTopo():
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)

    # 控制器
    c1 = net.addController('c1', controller=RemoteController)

    # 添加交換機
    switch1 = net.addSwitch('s1')
    switch2 = net.addSwitch('s2')
    switch3 = net.addSwitch('s3')
    switch4 = net.addSwitch('s4')
    switch5 = net.addSwitch('s5')
    switch6 = net.addSwitch('s6')
    switch7 = net.addSwitch('s7')
    switch8 = net.addSwitch('s8')

    # 添加主機，並設定 MAC 地址
    host1 = net.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
    host2 = net.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')
    host3 = net.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')
    host4 = net.addHost('h4', ip='10.0.0.4', mac='00:00:00:00:00:04')
    host5 = net.addHost('h5', ip='10.0.0.5', mac='00:00:00:00:00:05')
    host6 = net.addHost('h6', ip='10.0.0.6', mac='00:00:00:00:00:06')
    host7 = net.addHost('h7', ip='10.0.0.7', mac='00:00:00:00:00:07')
    host8 = net.addHost('h8', ip='10.0.0.8', mac='00:00:00:00:00:08')
    host9 = net.addHost('h9', ip='10.0.0.9', mac='00:00:00:00:00:09')

    # 添加鏈接
    net.addLink(switch6, switch7, port1=2, port2=2)
    net.addLink(switch7, switch5, port1=4, port2=2)
    net.addLink(switch5, switch8, port1=4, port2=4)
    net.addLink(switch8, switch4, port1=3, port2=1)
    net.addLink(switch4, switch3, port1=3, port2=4)
    net.addLink(switch3, switch1, port1=2, port2=4)
    net.addLink(switch1, switch6, port1=2, port2=3)
    net.addLink(switch2, switch1, port1=5, port2=3)
    net.addLink(switch2, switch3, port1=1, port2=3)
    net.addLink(switch2, switch7, port1=4, port2=3)
    net.addLink(switch2, switch5, port1=3, port2=6)
    net.addLink(switch2, switch4, port1=2, port2=4)
    net.addLink(switch5, switch4, port1=5, port2=5)

    # 連接主機與交換機
    net.addLink(host1, switch1, port1=1, port2=1)  # h1 連接到 switch1
    net.addLink(host2, switch3, port1=1, port2=1)  # h2 連接到 switch3
    net.addLink(host3, switch7, port1=1, port2=1)  # h3 連接到 switch7
    net.addLink(host4, switch5, port1=1, port2=1)  # h4 連接到 switch5
    net.addLink(host5, switch5, port1=1, port2=3)  # h5 連接到 switch5
    net.addLink(host6, switch8, port1=1, port2=1)  # h6 連接到 switch8
    net.addLink(host7, switch8, port1=1, port2=2)  # h7 連接到 switch8
    net.addLink(host8, switch6, port1=1, port2=1)  # h8 連接到 switch6
    net.addLink(host9, switch4, port1=1, port2=2)  # h9 連接到 switch4
    
    net.build()

    # 啟動網路
    print("Starting network")
    net.start()
    c1.start()
    switch1.start([c1])
    switch2.start([c1])
    switch3.start([c1])
    switch4.start([c1])
    switch5.start([c1])
    switch6.start([c1])
    switch7.start([c1])
    switch8.start([c1])

    # 開啟CLI介面
    print("Running CLI")
    CLI(net)

    # 停止網路
    print("Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    createTopo()