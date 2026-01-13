import requests
import networkx as nx
import matplotlib.pyplot as plt
import yaml
import sys
import os

FILE_INTERVAL = "\\" if os.name == "nt" else "/"
FILE_PATH = sys.path[0] + FILE_INTERVAL
CONFIG_PATH = os.path.dirname(sys.path[0]) + FILE_INTERVAL + "config.py"

f = open("mapping.yaml", "r", encoding="utf-8")
content_2 = f.read()
parameter_2 = yaml.full_load(content_2)
f.close()

port_mapping = dict(parameter_2["MAPPING_LIST_RE"])
route_mapping = dict(parameter_2["MAPPING_LIST_Route"])
ip_mapping = dict(parameter_2["MAPPING_LIST_IP"])

# 配置文件中的IP地址列表
SOUTHBOUND_SERVER_IPs = [
    '10.0.0.11','10.0.0.12','10.0.0.13'
]

# API端点
def fetch_topology_data(ip):
    """ 从API获取拓扑数据 """
    try:
        url = f"http://{ip}:11451/topology"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(ip_mapping[ip])
            data = response.json()
            new_data = []
            for item in data:
                new_item = {}
                new_item['port'] = port_mapping[item['port']]
                new_item['sw_ind'] = route_mapping[item['label']] 
                new_data.append(new_item)
            # 按 port 对 data 进行排序
            new_data.sort(key=lambda x: x['port'])
            print(new_data)
            return new_data
        else:
            print(f"无法连接到 {ip} - 状态码: {response.status_code}, 响应: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"无法连接到 {ip} - 错误: {e}")
        return None

def build_topology_graph(data_list):
    """ 根据数据列表构建拓扑图 """
    G = nx.Graph()

    # 添加节点
    for data in data_list:
        if data is not None:
            for item in data:
                G.add_node(item['sw_ind'])

    # 添加边
    # 这里假设如果两个端口有相同的标签，则它们之间存在连接
    for node1 in G.nodes:
        for node2 in G.nodes:
            if node1 != node2 and G.nodes[node1]['sw_ind']== G.nodes[node2]['label']:
                G.add_edge(node1, node2)

    return G

def draw_topology_graph(G):
    """ 绘制拓扑图 """
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)  # 使用spring布局算法
    labels = {node: f"{node}\n{G.nodes[node]}" for node in G.nodes}
    
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold")
    plt.show()

# 获取所有IP的拓扑数据
data_list = [fetch_topology_data(ip) for ip in SOUTHBOUND_SERVER_IPs]

# 构建拓扑图
# G = build_topology_graph(data_list)

# 绘制拓扑图
# draw_topology_graph(G)