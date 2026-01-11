from scapy.all import Ether, TCP, IP, sendp, sniff, hexdump, conf
# 显式告诉 Scapy 开启混杂模式
conf.sniff_promisc = True
import time

class HexPacketTool:
    def __init__(self, iface=None):
        """初始化工具，指定网卡（可选）"""
        self.iface = iface
        # 目标以太网类型（十六进制）
        self.target_ether_types = {0x1145, 0x1212}
        # IPv4的以太网类型常量
        self.IPV4_ETHER_TYPE = 0x0800

    def send_test_packet(self, src_mac=None, dst_mac=None, 
                         sport=1145, dport=1212, ether_type=0x1145,
                         ip_src=None, ip_dst=None):
        """发送测试数据包（支持自定义以太网类型或IPv4）"""
        # 构建基础以太网层
        ether_layer = Ether(
            src=src_mac,
            dst=dst_mac,
            type=ether_type
        )
        
        # 构建数据包
        if ether_type == self.IPV4_ETHER_TYPE and ip_src and ip_dst:
            # 构建IPv4数据包
            packet = ether_layer / IP(src=ip_src, dst=ip_dst) / TCP(sport=sport, dport=dport)
        else:
            # 构建自定义以太网类型的TCP数据包
            packet = ether_layer / TCP(sport=sport, dport=dport)
        
        # 发送数据包
        sendp(packet, iface=self.iface, verbose=0)
        if ether_type == self.IPV4_ETHER_TYPE:
            print(f"已发送IPv4数据包 - TCP:{sport}->{dport}, IP:{ip_src}->{ip_dst}")
        else:
            print(f"已发送数据包 - 以太网类型:0x{ether_type:04x}, TCP:{sport}->{dport}")
        return packet

    def handle_special_ether_packet(self, packet):
        """处理特定以太网类型的TCP数据包，打印16进制信息"""
        ether_type = packet[Ether].type
        src_mac = packet[Ether].src
        dst_mac = packet[Ether].dst
        
        print(f"\n[{time.strftime('%H:%M:%S')}] 收到特定以太网类型数据包 (0x{ether_type:04x}):")
        print(f"MAC地址: {src_mac} -> {dst_mac}")
        print(f"16进制原始数据 (以太网类型 0x{ether_type:04x}):")
        
        # 打印16进制格式（带偏移量和ASCII转换）
        hexdump(packet)

    def handle_ipv4_packet(self, packet):
        """处理IPv4数据包"""
        src_mac = packet[Ether].src
        dst_mac = packet[Ether].dst
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        protocol = "TCP" if TCP in packet else "其他"
        src_port = packet[TCP].sport if TCP in packet else "N/A"
        dst_port = packet[TCP].dport if TCP in packet else "N/A"
        
        print(f"\n[{time.strftime('%H:%M:%S')}] 收到IPv4数据包:")
        print(f"MAC地址: {src_mac} -> {dst_mac}")
        print(f"IP地址: {ip_src} -> {ip_dst}")
        print(f"协议: {protocol}, 端口: {src_port} -> {dst_port}")

    def packet_handler(self, packet):
        """主数据包处理函数，手动过滤并区分不同类型的数据包"""
        # 只处理包含以太网层的数据包
        if Ether not in packet:
            return
            
        ether_type = packet[Ether].type
        
        # 过滤条件1：特定以太网类型
        if ether_type in self.target_ether_types:
            self.handle_special_ether_packet(packet)
        
        # 过滤条件2：IPv4类型且包含IP层
        elif ether_type == self.IPV4_ETHER_TYPE and IP in packet:
            self.handle_ipv4_packet(packet)

    def start_listening(self):
        """开始监听数据包（不使用BPF过滤，完全在代码中过滤）"""
        print(f"开始监听 - 不使用BPF过滤，在代码中手动过滤")
        print(f"目标以太网类型（会显示16进制信息）: {[f'0x{et:04x}' for et in self.target_ether_types]}")
        print("按Ctrl+C停止监听")
        
        try:
            # 不设置filter参数，捕获所有数据包
            sniff(
                iface=self.iface,
                prn=self.packet_handler,  # 在handler中手动过滤
                store=0,
            )
        except KeyboardInterrupt:
            print("\n监听已停止")
        except Exception as e:
            print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    # 初始化工具，指定网卡（请根据实际情况修改）
    # tool = HexPacketTool(iface="veth5")  # 替换为你的实际网卡名称
    tool = HexPacketTool(iface="veth7")  # 替换为你的实际网卡名称

    # 开始监听
    tool.start_listening()
