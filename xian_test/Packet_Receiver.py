#!/usr/bin/env python3
import argparse
import time
from collections import defaultdict
from scapy.all import *

# ==========================================
# 1. P4 自定义协议定义（保留原有定义）
# ==========================================
ETHERTYPE_FLEP_TOPO = 0x1145
ETHERTYPE_TEMP_FWD  = 0x1234  

class FlepTopo(Packet):
    name = "FlepTopo"
    fields_desc = [
        BitField("messagetype", 0, 4),
        BitField("option", 0, 4),
        ShortField("sourcelabel", 0),
        ShortField("sourceport", 0),
        ShortField("replylabel", 0),
        ShortField("replyport", 0),
        XBitField("sendtstamp", 0, 48)
    ]

class TempForward(Packet):
    name = "TempForward"
    fields_desc = [
        ShortField("temp_port", 0), 
        ShortEnumField("temp_routing_type", 0, {
            0x1212: "FLEP (In-Flight)", 
            0x0800: "IPv4 (Done)",
            0x86dd: "IPv6 (Done)"
        })
    ]

class Felp(Packet):
    name = "Felp"
    fields_desc = [
        ShortField("active_label", 0),
        IntField("key", 0xFFFFFFFF),
        ByteField("key_index", 0),
        ShortEnumField("routing_type", 0x0800, {0x0800:"IPv4", 0x86dd:"IPv6"}),
        ByteField("label_depth", 0),
        ByteField("flags", 1)
    ]

class Flabel(Packet):
    name = "Flabel"
    fields_desc = [ ShortField("label", 0) ]

# 绑定协议层级关系（保留）
bind_layers(Ether, FlepTopo, type=ETHERTYPE_FLEP_TOPO)
bind_layers(Ether, TempForward, type=ETHERTYPE_TEMP_FWD)
bind_layers(TempForward, Felp, temp_routing_type=0x1212)
bind_layers(TempForward, IP, temp_routing_type=0x0800)
bind_layers(TempForward, IPv6, temp_routing_type=0x86dd)
bind_layers(Felp, Flabel)
bind_layers(Flabel, Flabel) 

# ==========================================
# 2. 接收与统计逻辑（无过滤 + 移除网卡检测）
# ==========================================
class AutoReceiver:
    def __init__(self, iface, count=0, show_latency=False, quiet=False, show_hex=False):
        self.iface = iface
        self.limit_count = count
        self.show_latency = show_latency
        self.quiet = quiet
        self.show_hex = show_hex
        self.pkt_idx = 0
        
        # 统计存储: Key=流特征字符串, Value=数量
        self.stats = defaultdict(int)
        # 存储所有时延数据
        self.latencies = [] 

    def _get_latency_val(self, pkt):
        """从 MAC 地址提取时间戳并计算差值 (单位: us)"""
        if not self.show_latency or Ether not in pkt:
            return None
        # try:
        t_in = int(pkt[Ether].src.replace(":", ""), 16)
        t_out = int(pkt[Ether].dst.replace(":", ""), 16)
        # if t_out >= t_in:
        diff_ns = t_out - t_in
        return diff_ns / 1000.0 # ns -> us
        # except Exception:
        #     pass
        # return None

    def _get_l4_info(self, pkt):
        """提取 Layer 4 信息 (TCP/UDP 端口)"""
        proto_str = ""
        ports_str = ""
        
        if pkt.haslayer(TCP):
            proto_str = "TCP"
            ports_str = f"{pkt[TCP].sport}->{pkt[TCP].dport}"
        elif pkt.haslayer(UDP):
            proto_str = "UDP"
            ports_str = f"{pkt[UDP].sport}->{pkt[UDP].dport}"
        else:
            proto_str = "L3-Only"
            
        return proto_str, ports_str

    def handle_packet(self, pkt):
        self.pkt_idx += 1
        
        # --- 1. 计算时延 ---
        lat_val = self._get_latency_val(pkt)
        lat_str = ""
        if lat_val is not None:
            self.latencies.append(lat_val)
            lat_str = f" | Latency: {lat_val:.3f} us"

        # --- 2. 识别所有类型的包（不再过滤，兼容所有协议）---
        signature = "Unknown Packet"
        info_str = "Unknown Content"

        # 优先识别自定义协议
        if pkt.haslayer(TempForward):
            tf = pkt[TempForward]
            p_info = f"[TempForward Port {tf.temp_port}]"
            
            if pkt.haslayer(IP):
                ip = pkt[IP]
                proto, ports = self._get_l4_info(pkt)
                signature = f"IPv4 {ip.src}->{ip.dst} [{proto} {ports}]"
                info_str = f"{p_info} {signature}"
                
            elif pkt.haslayer(IPv6):
                ip = pkt[IPv6]
                proto, ports = self._get_l4_info(pkt)
                signature = f"IPv6 {ip.src}->{ip.dst} [{proto} {ports}]"
                info_str = f"{p_info} {signature}"
                
            elif pkt.haslayer(Felp):
                flep = pkt[Felp]
                inner = "IPv4" if flep.routing_type == 0x0800 else "IPv6"
                signature = f"FLEP (Labels:{flep.label_depth}) Inner:{inner}"
                info_str = f"{p_info} FLEP In-Flight | Depth:{flep.label_depth}"
            else:
                signature = "TempForward (Unknown Payload)"
                info_str = f"{p_info} Unknown TempForward payload"

        elif pkt.haslayer(FlepTopo):
            ft = pkt[FlepTopo]
            mtype = "REQ" if ft.messagetype == 0 else "ANS"
            signature = f"Topo {mtype} Node {hex(ft.sourcelabel)}"
            info_str = f"[TOPO {mtype}] Node {hex(ft.sourcelabel)} -> Reply {hex(ft.replylabel)}"
        
        # 识别常见网络包（新增：显示所有标准协议）
        elif pkt.haslayer(IP):
            ip = pkt[IP]
            proto, ports = self._get_l4_info(pkt)
            signature = f"IPv4 {ip.src}->{ip.dst} [{proto} {ports}]"
            info_str = f"[IPv4] {signature}"
            
        elif pkt.haslayer(IPv6):
            ip = pkt[IPv6]
            proto, ports = self._get_l4_info(pkt)
            signature = f"IPv6 {ip.src}->{ip.dst} [{proto} {ports}]"
            info_str = f"[IPv6] {signature}"
            
        elif pkt.haslayer(ARP):
            arp = pkt[ARP]
            signature = f"ARP {arp.psrc} -> {arp.pdst} ({arp.op})"
            info_str = f"[ARP] {signature}"
            
        elif pkt.haslayer(ICMP):
            icmp = pkt[ICMP]
            signature = f"ICMP Type:{icmp.type} Code:{icmp.code}"
            info_str = f"[ICMP] {signature}"
            
        else:
            # 显示未知包的EtherType（关键调试信息）
            eth_type = hex(pkt[Ether].type) if Ether in pkt else "Unknown"
            signature = f"Other Packet (EtherType: {eth_type})"
            info_str = f"[Other] EtherType: {eth_type} | Length: {len(pkt)} bytes"

        # --- 3. 更新统计 ---
        self.stats[signature] += 1

        # --- 4. 实时打印 (非静默模式) ---
        if not self.quiet:
            ts = time.strftime('%H:%M:%S')
            print(f"[{ts} #{self.pkt_idx}] {info_str}{lat_str}")
            
            # 如果开启 Hex 显示
            if self.show_hex:
                print("-" * 60)
                hexdump(pkt)
                print("-" * 60)

    def print_summary(self):
        """打印最终统计表格"""
        print(f"\n\n{'='*35} 接收统计汇总 {'='*35}")
        print(f"监听接口: {self.iface}")
        print(f"总接收包数: {self.pkt_idx}")
        print(f"模式: 无过滤（捕获所有数据包）")
        
        print(f"\n{'-'*5} 流量分类统计 {'-'*5}")
        print(f"{'流特征 (Signature)':<70} | {'数量':<10}")
        print("-" * 85)
        for sig, count in sorted(self.stats.items()):
            print(f"{sig:<70} | {count:<10}")
        
        if self.show_latency and self.latencies:
            avg_lat = sum(self.latencies) / len(self.latencies)
            min_lat = min(self.latencies)
            max_lat = max(self.latencies)
            print(f"\n{'-'*5} 时延统计 (单位: 微秒) {'-'*5}")
            print(f"平均: {avg_lat:.3f} us")
            print(f"最小: {min_lat:.3f} us")
            print(f"最大: {max_lat:.3f} us")
            print(f"样本: {len(self.latencies)} 个数据包")
        
        print("=" * 85)

    def start(self):
        # 仅保留必要的 Scapy 配置，移除网卡列表打印
        conf.sniff_promisc = True  # 开启混杂模式
        # conf.L3socket = L3RawSocket  # 适配 Windows 原始套接字
        conf.verb = 0  # 关闭 Scapy 冗余日志

        print(f"[*] 开始监听接口: {self.iface} (无过滤模式，捕获所有包)")
        if self.quiet:
            print("[*] 模式: 静默 (只显示最终统计)")
        if self.show_latency:
            print("[*] 功能: 时延计算开启 (SrcMAC=T1, DstMAC=T2)")
        if self.show_hex:
            print("[*] 功能: 详细 Hex 转储开启")
            
        try:
            # 核心：移除 lfilter 过滤规则，捕获所有包
            sniff(
                iface=self.iface,
                prn=self.handle_packet,
                count=self.limit_count,
                store=0,
                timeout=None
            )
        except PermissionError:
            print("\n[!] 权限错误：请以【管理员身份】运行此脚本！")
        except Exception as e:
            print(f"\n[!] 发生错误: {e}")
        finally:
            self.print_summary()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P4 FLEP Receiver (无过滤版本，捕获所有包)")
    
    parser.add_argument("-i", "--iface", required=True, help="监听网卡 (例如: Realtek PCIe GbE Family Controller)")
    parser.add_argument("-c", "--count", type=int, default=0, help="接收数量限制 (0=无限)")
    parser.add_argument("--latency", action="store_true", help="开启时延计算")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式 (不刷屏，只看最后统计)")
    parser.add_argument("--hex", action="store_true", help="打印包的 16 进制内容")

    args = parser.parse_args()

    receiver = AutoReceiver(args.iface, args.count, args.latency, args.quiet, args.hex)
    receiver.start()