from scapy.all import IP, TCP, UDP, send
import time

def send_packets(data, count=1, interval=0.1, iface=None):
    """
    发送指定数量的数据包
    
    参数:
        data: 包含网络参数的字典
        count: 发送数量，默认1个
        interval: 包之间的发送间隔（秒），默认0.1秒
        iface: 发送数据包的网卡接口名称，默认为None（Scapy自动选择）
    """
    # 提取IP地址（忽略子网掩码）
    ipv4_src = data["ipv4_src"].split('/')[0]
    ipv4_dst = data["ipv4_dst"].split('/')[0]
    
    # 创建IP层
    ip = IP(src=ipv4_src, dst=ipv4_dst)
    
    # 创建传输层
    tp = data["tp"].lower()
    src_port = int(data["tp_src"])
    dst_port = int(data["tp_dst"])
    
    if tp == "tcp":
        transport = TCP(sport=src_port, dport=dst_port)
    elif tp == "udp":
        transport = UDP(sport=src_port, dport=dst_port)
    else:
        raise ValueError(f"不支持的协议: {tp}，仅支持tcp和udp")
    
    # 构建数据包
    packet = ip / transport
    print(f"准备发送{count}个{tp}包: {ipv4_src}:{src_port} -> {ipv4_dst}:{dst_port}")
    packet.show()
    
    # 发送指定数量的数据包
    for i in range(count):
        # 传入 iface 参数
        send(packet, verbose=0, iface=iface)
        print(f"已发送第{i+1}/{count}个包")
        if i < count - 1:  # 最后一个包不需要间隔
            time.sleep(interval)

# 测试数据
default_data = {
    "ipv4_src": "10.1.1.2",
    "ipv4_dst": "10.2.2.2",
    "tp": "tcp",
    "tp_src": "1145",
    "tp_dst": "2002",
}

if __name__ == "__main__":
    # 请将 'your_interface_name' 替换为实际网卡名称，例如 'eth0' 或 'enp0s3'
    # 发送100个数据包，间隔0.01秒，并指定网卡
    send_packets(default_data, count=100, interval=0.01, iface='enp0s3')