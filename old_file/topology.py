from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
import networkx as nx
import requests
import json

# Create a network graph with nodes and edges (switches and hosts)
G = nx.Graph()

# Add nodes (hosts and switches)
hosts = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9']
switches = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']

G.add_nodes_from(hosts + switches)

# Define edges between switches and hosts
G.add_edges_from([
    ('s6', 's7'), ('s7', 's5'), ('s5', 's8'), ('s8', 's4'), ('s4', 's3'),
    ('s3', 's1'), ('s1', 's6'), ('s2', 's1'), ('s2', 's3'), ('s2', 's7'),
    ('s2', 's5'), ('s2', 's4'), ('s5', 's4'),
    ('h1', 's1'), ('h2', 's3'), ('h3', 's7'), ('h4', 's5'), ('h5', 's5'),
    ('h6', 's8'), ('h7', 's8'), ('h8', 's6'), ('h9', 's4')
])
path = nx.shortest_path(G, source='h1', target='h3')
print("Shortest path from h1 to h3:", path)

# Define the function to calculate disjoint paths
def find_disjoint_paths(G, src, dst):
    # Find the first shortest path
    path1 = nx.shortest_path(G, source=src, target=dst)
    
    # Remove edges between switches in path1
    G_copy = G.copy()
    for i in range(len(path1) - 1):
        if path1[i].startswith('s') and path1[i+1].startswith('s'):
            G_copy.remove_edge(path1[i], path1[i+1])
    
    if nx.has_path(G_copy, source=src, target=dst):
        # Find the second shortest path
        path2 = nx.shortest_path(G_copy, source=src, target=dst)
        return path1, path2
    else:
        return path1, []  # Return an empty path if no disjoint path found

# Define the Mininet topology creation function
def createTopo():
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)

    # Add remote controller (this can be connected to your Ryu controller)
    c1 = net.addController('c1', controller=RemoteController)

    # Add switches
    switches = [net.addSwitch(f's{i}') for i in range(1, 9)]

    # Add hosts
    hosts = [net.addHost(f'h{i}', mac='00:00:00:00:00:0{i}', ip=f'10.0.0.{i}') for i in range(1, 10)]

    # Add links between switches and hosts
    links = [
        (hosts[0], switches[0]), (hosts[1], switches[2]), (hosts[2], switches[6]),
        (hosts[3], switches[4]), (hosts[4], switches[4]), (hosts[5], switches[7]),
        (hosts[6], switches[7]), (hosts[7], switches[5]), (hosts[8], switches[3]),
        (switches[5], switches[6]), (switches[6], switches[4]), (switches[4], switches[7]),
        (switches[7], switches[3]), (switches[3], switches[2]), (switches[2], switches[1]),
        (switches[1], switches[0])
    ]
    for link in links:
        net.addLink(link[0], link[1])

    # Build the network
    net.build()

    # Start the controller and switches
    c1.start()
    for switch in switches:
        switch.start([c1])

    # Start the network
    net.start()
    print("Network started.")

    # Start CLI
    CLI(net)

    # Stop the network
    net.stop()

# Function to deploy path to switches via OpenFlow (send flow rules)
def deploy_path(src_ip, dst_ip, path):
    url = "http://127.0.0.1:5000/deploy_path"
    headers = {"Content-Type": "application/json"}
    data = {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "path": path[1:-1]  # Remove the source and destination from path to avoid loop
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print(f"Path deployed successfully from {src_ip} to {dst_ip}")
    else:
        print(f"Failed to deploy path from {src_ip} to {dst_ip}, error: {response.text}")

# Integrate topology and path deployment
def main():
    setLogLevel('info')
    createTopo()

    # Find paths for each host pair in the topology
    disjoint_paths = {}
    for i, src in enumerate(hosts):
        for dst in hosts[i + 1:]:
            path1, path2 = find_disjoint_paths(G, src, dst)
            disjoint_paths[(src, dst)] = (path1, path2)

    # Deploy the paths to switches
    for key, paths in disjoint_paths.items():
        src_ip, dst_ip = key
        if paths[1]:
            deploy_path(src_ip, dst_ip, paths[0])
            deploy_path(src_ip, dst_ip, paths[1])
        else:
            deploy_path(src_ip, dst_ip, paths[0])

if __name__ == '__main__':
    main()