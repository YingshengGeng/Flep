#!/usr/bin/env python3
from scapy.all import *
import argparse
import time

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

# 绑定协议
bind_layers(Ether, FlepTopo, type=ETHERTYPE_FLEP_TOPO)
bind_layers(Ether, TempForward, type=ETHERTYPE_TEMP_FWD)
bind_layers(TempForward, Felp, temp_routing_type=0x1212)
bind_layers(TempForward, IP, temp_routing_type=0x0800)
bind_layers(TempForward, IPv6, temp_routing_type=0x86dd)

# ==========================================
# 2. 接收与显示逻辑
# ==========================================
class AutoReceiver:
    def __init__(self, iface, count=0, show_latency=False):
        self.iface = iface
        self.limit_count = count
        self.show_latency = show_latency
        self.pkt_idx = 0

    def _get_latency_str(self, pkt):
        """
        从 MAC 地址中提取时间戳并计算延迟 (微秒)
        假设 P4 Ingress 写 SrcMAC, Egress 写 DstMAC
        """
        if not self.show_latency or Ether not in pkt:
            return ""
        
        try:
            # Scapy 的 MAC 是 "xx:xx:xx..." 格式，去掉冒号转整数
            t_in = int(pkt[Ether].src.replace(":", ""), 16)
            t_out = int(pkt[Ether].dst.replace(":", ""), 16)
            
            # 计算差值 (单位: ns -> us)
            if t_out >= t_in:
                diff_ns = t_out - t_in
                diff_us = diff_ns / 1000.0
                return f" | Latency: {diff_us:.3f} us"
            else:
                # 可能发生溢出或逻辑错误
                return f" | Latency: Error (Out < In)"
        except Exception:
            return " | Latency: ParseErr"

    def handle_packet(self, pkt):
        self.pkt_idx += 1
        ts = time.strftime('%H:%M:%S')
        prefix = f"[{ts} #{self.pkt_idx}]"
        
        # 获取延迟字符串 (如果开启)
        lat_str = self._get_latency_str(pkt)

        # --- A. 处理数据转发包 (TempForward) ---
        if pkt.haslayer(TempForward):
            tf = pkt[TempForward]
            p4_info = f"[Port {tf.temp_port}]" 
            
            # 1. 转发完成 (IPv4)
            if pkt.haslayer(IP):
                print(f"{prefix} {p4_info} {pkt[IP].summary()}{lat_str}")

            # 2. 转发完成 (IPv6)
            elif pkt.haslayer(IPv6):
                print(f"{prefix} {p4_info} {pkt[IPv6].summary()}{lat_str}")

            # 3. 仍在转发中 (FLEP 封装)
            elif pkt.haslayer(Felp):
                flep = pkt[Felp]
                inner_type = "IPv4" if flep.routing_type == 0x0800 else "IPv6"
                print(f"{prefix} {p4_info} FLEP In-Flight | Depth:{flep.label_depth} | Inner:{inner_type}{lat_str}")
            
            else:
                print(f"{prefix} {p4_info} Unknown TempForward Content{lat_str}")

        # --- B. 处理拓扑发现包 (Topo) ---
        elif pkt.haslayer(FlepTopo):
            ft = pkt[FlepTopo]
            mtype = "REQ" if ft.messagetype == 0 else "ANS"
            print(f"{prefix} [TOPO {mtype}] Node {hex(ft.sourcelabel)} -> Reply {hex(ft.replylabel)}")

    def start(self):
        print(f"[*] 开始监听接口: {self.iface}")
        if self.show_latency:
            print(f"[*] 延迟计算: 开启 (单位: 微秒 us)")
        else:
            print(f"[*] 延迟计算: 关闭")
            
        target_str = f"{self.limit_count} 个包" if self.limit_count > 0 else "无限 (Ctrl+C 停止)"
        print(f"[*] 目标: {target_str}")
        print("-" * 60)

        try:
            # 必须开启混杂模式，因为 MAC 被改为时间戳后不再匹配网卡 MAC
            conf.sniff_promisc = True 
            
            sniff(
                iface=self.iface,
                prn=self.handle_packet,
                count=self.limit_count,
                store=0,
                lfilter=lambda p: p.haslayer(TempForward) or p.haslayer(FlepTopo)
            )
        except KeyboardInterrupt:
            print("\n[*] 监听已停止。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P4 FLEP Receiver")
    parser.add_argument("-i", "--iface", required=True, help="监听网卡 (例如: veth1)")
    parser.add_argument("-c", "--count", type=int, default=0, help="接收数量 (0 表示一直接收)")
    parser.add_argument("--latency", action="store_true", help="解析 MAC 时间戳并计算延迟 (us)")
    args = parser.parse_args()

    receiver = AutoReceiver(args.iface, args.count, args.latency)
    receiver.start()