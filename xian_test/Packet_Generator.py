#!/usr/bin/env python3
import argparse
import time
import sys
from scapy.all import IP, IPv6, TCP, UDP, Ether, Raw, sendp, get_if_hwaddr

def send_traffic(args):
    # 1. 自动识别 IP 版本
    # 如果目标地址包含冒号 ":" (如 2001::1)，则认为是 IPv6
    is_ipv6 = ':' in args.dst
    
    if is_ipv6:
        # IPv6
        l3 = IPv6(src=args.src, dst=args.dst)
        proto_ver = "IPv6"
    else:
        # IPv4
        l3 = IP(src=args.src, dst=args.dst)
        proto_ver = "IPv4"

    # 2. 构建传输层 (TCP/UDP)
    if args.udp:
        l4 = UDP(sport=args.sport, dport=args.dport)
        proto_name = "UDP"
    else:
        # 默认 TCP (带有 SYN 标志)
        l4 = TCP(sport=args.sport, dport=args.dport, flags="S", seq=100)
        proto_name = "TCP"

    # 3. 构建完整数据包 (Ethernet + L3 + L4 + Payload)
    # src MAC 自动获取，dst MAC 设为广播或网关(在 P4 实验中通常不影响 L3 路由)
    eth = Ether(src=get_if_hwaddr(args.iface), dst="ff:ff:ff:ff:ff:ff")
    pkt = eth / l3 / l4 / Raw(load="FLEP_TEST_PAYLOAD")

    # 4. 打印发送配置
    print(f"\n{'='*10} [发送配置] {'='*10}")
    print(f"网卡接口: {args.iface}")
    print(f"协议栈:   {proto_ver} / {proto_name}")
    print(f"路径:     {args.src if args.src else '(auto)'} -> {args.dst}")
    print(f"发送数量: {args.count}")
    print(f"{'='*32}\n")

    # 5. 执行发送循环
    try:
        for i in range(args.count):
            sendp(pkt, iface=args.iface, verbose=False)
            print(f"[{time.strftime('%H:%M:%S')}] 已发送 {i+1}/{args.count}")
            # 如果不是最后一个包，则等待间隔
            if i < args.count - 1:
                time.sleep(args.interval)
                
        print("\n[*] 发送完成。")
        
    except KeyboardInterrupt:
        print("\n[-] 用户强制停止。")
    except Exception as e:
        print(f"\n[!] 发送发生错误: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="标准流量发送器 (IPv4/v6, TCP/UDP)")
    
    # 基础参数
    parser.add_argument("-i", "--iface", required=True, help="发送网卡 (例如: veth0)")
    parser.add_argument("-c", "--count", type=int, default=1, help="发送包的数量")
    parser.add_argument("--interval", type=float, default=0.5, help="发送间隔(秒)")
    
    # 网络参数
    parser.add_argument("--dst", required=True, help="目的IP (自动识别 IPv4 或 IPv6)")
    parser.add_argument("--src", help="源IP (可选)")
    parser.add_argument("--sport", type=int, default=1234, help="源端口")
    parser.add_argument("--dport", type=int, default=80, help="目的端口")
    parser.add_argument("--udp", action="store_true", help="使用 UDP 协议 (默认是 TCP)")

    args = parser.parse_args()
    send_traffic(args)