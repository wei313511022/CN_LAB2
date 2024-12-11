from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI

def custom_topology():
    net = Mininet(controller=RemoteController)

    # Add switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    s5 = net.addSwitch('s5')
    s6 = net.addSwitch('s6')
    s7 = net.addSwitch('s7')
    s8 = net.addSwitch('s8')

    # Add hosts
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    h5 = net.addHost('h5')
    h6 = net.addHost('h6')
    h7 = net.addHost('h7')
    h8 = net.addHost('h8')
    h9 = net.addHost('h9')

    # Add links between hosts and switches
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s7)
    net.addLink(h4, s5)
    net.addLink(h5, s5)
    net.addLink(h6, s8)
    net.addLink(h7, s8)
    net.addLink(h8, s6)
    net.addLink(h9, s4)

    # Add links between switches
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s2, s3)
    net.addLink(s2, s4)
    net.addLink(s2, s5)
    net.addLink(s2, s7)
    net.addLink(s3, s4)
    net.addLink(s5, s7)
    net.addLink(s5, s8)
    net.addLink(s6, s7)
    net.addLink(s7, s8)

    # Add controller
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Start the network
    net.build()
    c0.start()
    net.start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    custom_topology()
