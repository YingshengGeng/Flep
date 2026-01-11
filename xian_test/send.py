from scapy.all import IP, TCP, UDP, Ether, sendp  # 导入Ether和sendp
import time

def send_packets(data, count=1, interval=0.1, iface=None):
    """
    发送指定数量的数据包，优化网卡指定方式
    
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
    
    # 构建数据包（添加以太网层，使sendp更可靠）
    # 注意：如果不指定src/dst MAC，Scapy会自动填充
    packet = Ether() / ip / transport
    print(f"准备发送{count}个{tp}包: {ipv4_src}:{src_port} -> {ipv4_dst}:{dst_port}")
    packet.show()
    
    # 发送指定数量的数据包（使用sendp替代send，更适合指定网卡）
    for i in range(count):
        # 发送二层数据包，iface参数在这里更可靠
        sendp(packet, verbose=0, iface=iface)
        print(f"已发送第{i+1}/{count}个包")
        if i < count - 1:
            time.sleep(interval)

# 测试数据
default_data = {
    "ipv4_src": "10.1.1.2",
    "ipv4_dst": "10.2.2.2",
    "tp": "tcp",
    "tp_src": "2001",
    "tp_dst": "2002",
}

if __name__ == "__main__":
    # 指定网卡发送（请替换为实际网卡名称）
    send_packets(default_data, count=100, interval=0.01, iface='veth1')
