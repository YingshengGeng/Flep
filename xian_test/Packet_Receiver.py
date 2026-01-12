#!/usr/bin/env python3
import argparse
import time
from collections import defaultdict
from scapy.all import *

# ==========================================
# 1. P4 自定义协议定义
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

# 绑定协议层级关系
bind_layers(Ether, FlepTopo, type=ETHERTYPE_FLEP_TOPO)
bind_layers(Ether, TempForward, type=ETHERTYPE_TEMP_FWD)

# TempForward 根据 routing_type 决定下一层
bind_layers(TempForward, Felp, temp_routing_type=0x1212)
bind_layers(TempForward, IP, temp_routing_type=0x0800)
bind_layers(TempForward, IPv6, temp_routing_type=0x86dd)

# Felp 下一层是 Label
bind_layers(Felp, Flabel)
# 如果有多个 Label，通常 Scapy 需要特殊处理，这里简单绑定第一层
bind_layers(Flabel, Flabel) 

# ==========================================
# 2. 接收与统计逻辑
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
        """
        从 MAC 地址提取时间戳并计算差值 (单位: us)
        T1 (Ingress) 在 Src MAC, T2 (Egress) 在 Dst MAC
        """
        if not self.show_latency or Ether not in pkt:
            return None
        try:
            # 去掉冒号，转16进制整数
            t_in = int(pkt[Ether].src.replace(":", ""), 16)
            t_out = int(pkt[Ether].dst.replace(":", ""), 16)
            
            # 简单的溢出保护逻辑
            if t_out >= t_in:
                diff_ns = t_out - t_in
                return diff_ns / 1000.0 # ns -> us
        except Exception:
            pass
        return None

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

        # --- 2. 识别流特征 (Signature) ---
        signature = "Unknown Packet"
        info_str = "Unknown Content"

        if pkt.haslayer(TempForward):
            tf = pkt[TempForward]
            p_info = f"[Port {tf.temp_port}]"
            
        if pkt.haslayer(IP):
            ip = pkt[IP]
            proto, ports = self._get_l4_info(pkt)
            # 特征: IPv4 + 协议 + 端口
            signature = f"IPv4 {ip.src}->{ip.dst} [{proto} {ports}]"
            info_str = f"{p_info} {signature}"
            
        elif pkt.haslayer(IPv6):
            ip = pkt[IPv6]
            proto, ports = self._get_l4_info(pkt)
            # 特征: IPv6 + 协议 + 端口
            signature = f"IPv6 {ip.src}->{ip.dst} [{proto} {ports}]"
            info_str = f"{p_info} {signature}"
            
        elif pkt.haslayer(Felp):
            flep = pkt[Felp]
            inner = "IPv4" if flep.routing_type == 0x0800 else "IPv6"
            # 特征: FLEP 封装包
            signature = f"FLEP (Labels:{flep.label_depth}) Inner:{inner}"
            info_str = f"{p_info} FLEP In-Flight | Depth:{flep.label_depth}"
        else:
            signature = "TempForward (Unknown Payload)"
            info_str = f"{p_info} Unknown TempForward payload"

        elif pkt.haslayer(FlepTopo):
            ft = pkt[FlepTopo]
            mtype = "REQ" if ft.messagetype == 0 else "ANS"
            # 特征: 拓扑发现包
            signature = f"Topo {mtype} Node {hex(ft.sourcelabel)}"
            info_str = f"[TOPO {mtype}] Node {hex(ft.sourcelabel)} -> Reply {hex(ft.replylabel)}"

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
        
        print(f"\n{'-'*5} 流量分类统计 (Layer 3 + Layer 4) {'-'*5}")
        # 调整列宽
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
        print(f"[*] 开始监听接口: {self.iface}")
        if self.quiet:
            print("[*] 模式: 静默 (只显示最终统计)")
        if self.show_latency:
            print("[*] 功能: 时延计算开启 (SrcMAC=T1, DstMAC=T2)")
        if self.show_hex:
            print("[*] 功能: 详细 Hex 转储开启")
            
        try:
            # 开启混杂模式以捕获修改了 MAC 的包
            conf.sniff_promisc = True 
            
            # 过滤器：只看 P4 相关的包，避免捕获 SSH/ARP 等背景流量干扰统计
            sniff(
                iface=self.iface,
                prn=self.handle_packet,
                count=self.limit_count,
                store=0,
                lfilter=lambda p: p.haslayer(TempForward) or p.haslayer(FlepTopo)
            )
        except KeyboardInterrupt:
            print("\n[*] 用户停止捕获...")
        except Exception as e:
            print(f"\n[!] 发生错误: {e}")
        finally:
            self.print_summary()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P4 FLEP Receiver (Stats/Latency/Hex)")
    
    parser.add_argument("-i", "--iface", required=True, help="监听网卡 (例如: veth1)")
    parser.add_argument("-c", "--count", type=int, default=0, help="接收数量限制 (0=无限)")
    parser.add_argument("--latency", action="store_true", help="开启时延计算")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式 (不刷屏，只看最后统计)")
    parser.add_argument("--hex", action="store_true", help="打印包的 16 进制内容")

    args = parser.parse_args()

    receiver = AutoReceiver(args.iface, args.count, args.latency, args.quiet, args.hex)
    receiver.start()