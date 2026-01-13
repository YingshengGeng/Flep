# 6.1
clear_port_forward R1
clear_port_forward R2
clear_port_forward R3
add_port_forward R1 1 33
add_port_forward R3 1 33
# 6.1.1
IPV4
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
    0x2502, 0x2507, 0x2505, 0x2509
}
0x2502 1
add_port_forward R1 33 1
add_port_forward R2 2 1
add_port_forward R3 1 33

python .\Packet_Receiver.py -i "Realtek PCIe GbE Family Controller" --hex 
python Packet_Generator.py -i "USB2.0 Ethernet Adapter" --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100 --interval 0.01


# 6.1.2
clear_port_forward R1
clear_port_forward R2
clear_port_forward R3
add_port_forward R1 1 33
add_port_forward R3 1 33

IPV4
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
    0x2502, 0x2503
}

0x2502 1
0x2503 1

add_port_forward R3 1 33(重复添加)

python .\Packet_Receiver.py -i "Realtek PCIe GbE Family Controller" --hex 
python3 Packet_Generator.py -i "USB2.0 Ethernet Adapter" --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100 --interval 0.01


# 6.2
# 6.2.1
clear_port_forward R1
clear_port_forward R2
clear_port_forward R3
add_port_forward R1 1 33
add_port_forward R3 1 33
IPV4
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
    0x2502, 0x2503,0x2505, 0x2510, 0x2511
}

0x2502 1

add_port_forward R2 2 1
add_port_forward R3 1 33(重复添加)


python .\Packet_Receiver.py -i "Realtek PCIe GbE Family Controller" --hex 
python Packet_Generator.py -i "USB2.0 Ethernet Adapter" --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100 --interval 0.01


IPV6
{
    2001::15/24
    2001::16/24
    1001
    1002
    0x2502, 0x2503,0x2505, 0x2510, 0x2511
}

<!-- add_port_forward R2 1 2
add_port_forward R3 1 33 -->

# 3. 发送命令 (自动识别 IPv6)

# 4. 接收命令
python .\Packet_Receiver.py -i "Realtek PCIe GbE Family Controller" --hex 
python Packet_Generator.py -i "USB2.0 Ethernet Adapter" --src 2001::15 --dst 2001::16 --sport 1001 --dport 1002 -c 100

<!-- clear_port_forward R2 -->

# 6.2.2
UDP
{
    10.0.0.15/24
    10.0.0.16/24
    1001
    1002
    0x2502, 0x2507, 0x2505, 0x2509
}
<!-- # 1. 配置中间跳转
add_port_forward R2 1 2
add_port_forward R3 1 33 -->

# 3. 发送命令 (显式指定 UDP)
python .\Packet_Receiver.py -i "Realtek PCIe GbE Family Controller" --hex 
python Packet_Generator.py -i "USB2.0 Ethernet Adapter" --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 --udp -c 100 --interval 0.01


TCP
{
    10.0.0.15/24
    10.0.0.16/24
    1001
    1002
    0x2502, 0x2503, 0x2505, 0x2510, 0x2511
}
# 1. 配置中间跳转
add_port_forward R2 1 2
add_port_forward R3 1 33

# 3. 发送命令 (默认即为 TCP)
python Packet_Generator.py -i "USB2.0 Ethernet Adapter" --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100

# 4. 接收命令
python3 receiver.py -i veth1 -q

# 6.2.3
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
    0x2502, 0x2503,0x2505, 0x2510, 0x2511
}
bfrt python 
bfrt.flep_encap.pipe.Ingress.flep_ipv4_classifier
dump

jupyter

bfrt python 
bfrt.flep_encap.pipe.Ingress.flep_ipv4_classifier
dump

# 6.2.4
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
    0x2501, 0x2503,0x2505, 0x2510, 0x2511
}

IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
    0x2501, 0x2503
}


IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
}

IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    1001
    1002
}

# 6.2.5
转发功能
0x2502 1

0x2502 2

0x2502 1

0x2502

0x2502

# 6.3
# 6.3.1

# 6.3.2
修改代码
cd $PROGRAM_DIR
vim ./flep_encap_with_topo/backend/_set_pkt_gen.py
<!-- cd $PROGRAM_DIR
vim ./flep_process_with_topo/backend/_set_pkt_gen.py -->
python3 ${PROGRAM_DIR}/flep_encap_with_topo/backend/deploy_backend.py 3
<!-- python3 ${PROGRAM_DIR}/flep_process_with_topo/backend/deploy_backend.py 2 -->
<!-- python3 ${PROGRAM_DIR}/flep_encap_with_topo/backend/deploy_backend.py 1 -->
bfrt python 
bfrt.flep_encap.pipe.Ingress.labeldatacache
bw_register.get(REGISTER_INDEX=1)

python -c "while True: print(hex(int(input('数字: '))))"

# 6.3.3
前端 + postman
# 6.4
clear_port_forward R1
clear_port_forward R2
clear_port_forward R3
add_port_forward R1 1 33
add_port_forward R3 1 33
# 6.4.1
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    1001,
    1002,
    0x2502,0x2503,0x2504,0x2505,0x2506,0x2507,0x2508,0x2509,0x2510
}
0x2502 1
0x2503 1
python Packet_Generator.py -i "USB2.0 Ethernet Adapter" --src 10.0.0.15 --dst 10.0.0.16 --sport 1001 --dport 1002 -c 100 --interval 0.01
# 6.4.2
pm port-del 1/0
pm port-add 1/0 10G NONE
pm port-enb 1/0

pm port-del 1/0
pm port-add 1/0 25G NONE
pm port-enb 1/0

pm port-del 33/0
pm port-add 33/0 1G NONE
pm port-enb 33/0


0x2503 34
pm port-del 33/0
pm port-add 33/0 10G NONE
pm port-enb 33/0
clear_port_forward R3
add_port_forward R3 34 33

# 6.4.3
sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna -o ${PROGRAM_DIR}/flep_encap_with_topo/target_latency/ -g ${PROGRAM_DIR}/flep_encap_with_topo/flep_encap_latency.p4

sudo cp ${PROGRAM_DIR}/flep_encap_with_topo/target_latency/flep_encap_latency.conf ${SDE_INSTALL_DIR}/share/p4/targets/tofino/

sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna -o ${PROGRAM_DIR}/flep_process_with_topo/target_latency/ -g ${PROGRAM_DIR}/flep_process_with_topo/flep_process_latency.p4

sudo cp ${PROGRAM_DIR}/flep_process_with_topo/target_latency/flep_process_latency.conf ${SDE_INSTALL_DIR}/share/p4/targets/tofino/

% 改config
bash  ${SDE}/run_switchd.sh -p flep_encap_latency
python3 ${PROGRAM_DIR}/flep_encap_with_topo/backend/deploy_backend.py


bash  ${SDE}/run_switchd.sh -p flep_process_latency
python3 ${PROGRAM_DIR}/flep_process_with_topo/backend/deploy_backend.py

> /home/ruijie/onl-bf-sde/code_latency/flep_encap_with_topo/flep_encap_latency.p4
vim /home/ruijie/onl-bf-sde/code_latency/flep_encap_with_topo/flep_encap_latency.p4

> /home/ruijie/onl-bf-sde/code_latency/flep_process_with_topo/flep_process_latency.p4
vim /home/ruijie/onl-bf-sde/code_latency/flep_process_with_topo/flep_process_latency.p4
IPV4"
{
    10.0.0.15/24 
    10.0.0.16/24
    1001,
    1002,
    0x2502, 0x2503
}
0x2502 1
add_port_forward R2 2 1
add_port_forward R3 1 33
断电和数据库

{
    10.0.0.15/24 
    10.0.0.16/24
    1001,
    1002,
    0x2502, 0x2503, 0x2504
}
0x2503 1

拓扑处理，标签处理

6.4.4
修改时间
拓扑发现
信息查看
抓包

6.5
光盘，console（名字是不是得改）
6.6 果茶浏览器
6.7.1 接口文档测
6.7.2 

