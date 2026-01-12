# 6.1
add_port_forward R1 1 33
add_port_forward R3 1 33
# 6.1.1
拓扑查询
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    0x2501,0x2502, 0x2505, 0x2509
}
{
    R1 0x2501 33
    R2 0x2502 2
}

sudo python3 send_pkt.py -i veth0 --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100

python3 receiver.py -i veth1

# 6.1.2
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    0x2501,0x2502
}
<!-- {
    0x2501 33
    0x2502 2
} -->
直接查询
add_port_forward R3 1 33(重复添加)

sudo python3 send_pkt.py -i veth0 --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100

python3 receiver.py -i veth1
# 6.2.1
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    0x2501, 0x2503,0x2505, 0x2510, 0x2511
}
add_port_forward R2 1 2
add_port_forward R3 1 33 (重复添加)
<!-- clear_port_forward R2 -->
sudo python3 send_pkt.py -i veth0 --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100
python3 receiver.py -i veth1

IPV6
{
    2001::15/128
    2001::16/128
    0x2501, 0x2503, 0x2505, 0x2510, 0x2511
}

<!-- add_port_forward R2 1 2
add_port_forward R3 1 33 -->

# 3. 发送命令 (自动识别 IPv6)
sudo python3 send_pkt.py -i veth0 --src 2001::15 --dst 2001::16 --sport 1001 --dport 1002 -c 100

# 4. 接收命令
python3 receiver.py -i veth1 -q

<!-- clear_port_forward R2 -->

# 6.2.2
UDP
{
    10.0.0.15/24
    10.0.0.16/24
    1001
    1002
    0x2501, 0x2503, 0x2505, 0x2510, 0x2511
}
# 1. 配置中间跳转
add_port_forward R2 1 2
add_port_forward R3 1 33

# 3. 发送命令 (显式指定 UDP)
sudo python3 send_pkt.py -i veth0 --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 --udp -c 100

# 4. 接收命令
python3 receiver.py -i veth1 -q

TCP
{
    10.0.0.15/24
    10.0.0.16/24
    1001
    1002
    0x2501, 0x2503, 0x2505, 0x2510, 0x2511
}
# 1. 配置中间跳转
add_port_forward R2 1 2
add_port_forward R3 1 33

# 3. 发送命令 (默认即为 TCP)
sudo python3 send_pkt.py -i veth0 --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100

# 4. 接收命令
python3 receiver.py -i veth1 -q

# 6.2.3
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    0x2501, 0x2503,0x2505, 0x2510, 0x2511
}
bfrt python 
