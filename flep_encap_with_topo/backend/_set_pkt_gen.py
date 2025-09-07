# Import necessary libraries

import sys
import os
import yaml
import time

is_gen = sys.argv[1]

#system arguments p4name portlist4multicast
FILE_INTERVAL = '\\' if os.name == 'nt' else '/'
FILE_PATH = sys.path[0] + FILE_INTERVAL
f = open(FILE_PATH + 'configuration.yml', 'r')
content = yaml.safe_load(f.read())
f.close()
P4_NAME = content['P4_NAME']



# Add the Tofino SDK paths to the system path for Python
sde_install = content['SDE_INSTALL']#os.environ['SDE_INSTALL']
python_version = content['PYTHON_VERSION']
sys.path.extend([
    '{}/lib/{}/site-packages/tofino'.format(sde_install, python_version),
    '{}/lib/{}/site-packages/p4testutils'.format(sde_install, python_version),
    '{}/lib/{}/site-packages'.format(sde_install, python_version),
    '{}/lib/{}/site-packages/tofino/bfrt_grpc/'.format(sde_install, python_version)
])

# import ptf.testutils as testutils
import bfrt_grpc.client as gc
import bfruntime_pb2
from scapy.all import Ether, Raw
def simple_eth_payload_packet(
    pktlen=1000, 
    eth_dst="00:01:02:03:04:05", 
    eth_src="00:06:07:08:09:0a", 
    eth_type=0x1919,
    payload=b""  # 新增：自定义payload，默认为空字节串
):
    """
    使用Scapy创建带有自定义payload的以太网数据包
    
    参数:
        pktlen: 数据包总长度，默认60字节
        eth_dst: 目的MAC地址
        eth_src: 源MAC地址
        eth_type: 以太网类型字段，默认0x88CC（LLDP）
        payload: 自定义负载数据，应为字节串格式
    
    返回:
        构建好的Scapy以太网数据包
    """
    print("here1")
    # 创建以太网层
    eth = Ether(dst=eth_dst, src=eth_src, type=eth_type)
    
    # 计算当前已有长度（以太网头部 + payload）
    current_length = len(eth) + len(payload)
    
    # 计算需要填充的字节数
    if current_length < pktlen:
        padding_length = pktlen - current_length
        padding = b'\x00' * padding_length
        # 组合：以太网头部 + payload + 填充
        pkt = eth / Raw(load=payload + padding)
    else:
        # 如果payload过长，截断到刚好满足总长度
        truncated_payload = payload[:pktlen - len(eth)]
        pkt = eth / Raw(load=truncated_payload)
    
    return pkt, payload

# Establish a connection to the BFRuntime server
try:
    grpc_addr = "0.0.0.0:50052"
    client_id = 1 # diff from others
    device_id = 0
    pipe_id = 0xFFFF  # Pipe ID; FFFF indicates all pipes
    client = gc.ClientInterface(grpc_addr, client_id, device_id)
    target = gc.Target(device_id, pipe_id)
    client.bind_pipeline_config(P4_NAME)  # Bind the pipeline configuration to the device

    # Retrieve information about the bound pipeline
    bfrt_info = client.bfrt_info_get(P4_NAME)

    # Access the required tables
    pktgen_app_cfg_table = bfrt_info.table_get("app_cfg")
    pktgen_pkt_buffer_table = bfrt_info.table_get("pkt_buffer")
    pktgen_port_cfg_table = bfrt_info.table_get("port_cfg")
    
    g_timer_app_id = 1  # Application ID for the timer-based packet generation
    if is_gen == '1':
      # Enable packet generation on a specific port
      print("Enabling packet generation on port.")
      src_port = 68  # Source port for packet generation, for tofino limit to 68-71
      # p = testutils.simple_eth_packet(pktlen=100, eth_type=0x1919)  # Create a simple Ethernet packet
      hex_payload = b"\x01\x00\x00\x03\x00\x01\x00\x06\x07\x08\x09\x0a\x11\x45\x00\x25" \
              b"\x01\xff\xff\xff\xff\xff\xff\x05\x97\xd7\xcd\x33\x30\x74\x68\x69" \
              b"\x73\x20\x69\x73\x20\x61\x20\x63\x75\x73\x74\x6f\x6d"
      p = simple_eth_payload_packet(pktlen=100, eth_type=0x1919, payload=hex_payload)
      pktgen_port_cfg_table.entry_mod(
          target,
          [pktgen_port_cfg_table.make_key([gc.KeyTuple('dev_port', src_port)])],
          [pktgen_port_cfg_table.make_data([gc.DataTuple('pktgen_enable', bool_val=True)])]
      )

      print("Configuring packet generation application.")
      pktlen = 100  # Packet length
      buff_offset = 144  # Buffer offset for packet payload
      b_count = 4  # Batch count
      p_count = 2  # Packets per batch
      data = pktgen_app_cfg_table.make_data([
          gc.DataTuple('timer_nanosec', (1<<32) - 1),  # Timer interval in nanoseconds
          gc.DataTuple('app_enable', bool_val=False),  # Application initially disabled
          gc.DataTuple('pkt_len', (pktlen - 6)),  # Adjusted packet length
          gc.DataTuple('pkt_buffer_offset', buff_offset),  # Packet buffer offset
          gc.DataTuple('pipe_local_source_port', src_port),  # Source port
          gc.DataTuple('increment_source_port', bool_val=False),  # Source port incrementation disabled
          gc.DataTuple('batch_count_cfg', b_count - 1),  # Configured batch count
          gc.DataTuple('packets_per_batch_cfg', p_count - 1),  # Configured packets per batch
          gc.DataTuple('ibg', 1),  # Inter-batch gap
          gc.DataTuple('ibg_jitter', 0),  # Inter-batch jitter
          gc.DataTuple('ipg', 1000),  # Inter-packet gap
          gc.DataTuple('ipg_jitter', 500),  # Inter-packet jitter
          gc.DataTuple('batch_counter', 0),  # Batch counter
          gc.DataTuple('pkt_counter', 0),  # Packet counter
          gc.DataTuple('trigger_counter', 0)  # Trigger counter
      ], 'trigger_timer_periodic')  # Action to trigger periodic timer
      pktgen_app_cfg_table.entry_mod(
          target,
          [pktgen_app_cfg_table.make_key([gc.KeyTuple('app_id', g_timer_app_id)])],
          [data]
      )

      # Configure the packet buffer
      print("Configuring packet buffer.")
      pktgen_pkt_buffer_table.entry_mod(
          target,
          [pktgen_pkt_buffer_table.make_key([gc.KeyTuple('pkt_buffer_offset', buff_offset),
                                            gc.KeyTuple('pkt_buffer_size', (pktlen - 6))])],
          [pktgen_pkt_buffer_table.make_data([gc.DataTuple('buffer', bytearray(bytes(p)[6:]))])]
      )
      
      # Enable the packet generation application
      print("Enabling packet generation.")
      pktgen_app_cfg_table.entry_mod(
          target,
          [pktgen_app_cfg_table.make_key([gc.KeyTuple('app_id', g_timer_app_id)])],
          [pktgen_app_cfg_table.make_data([gc.DataTuple('app_enable', bool_val=True)], 'trigger_timer_one_shot')]
      )
    else:
      # Enable the packet generation application
      print("Enabling packet disable.")
      pktgen_app_cfg_table.entry_mod(
          target,
          [pktgen_app_cfg_table.make_key([gc.KeyTuple('app_id', g_timer_app_id)])],
          [pktgen_app_cfg_table.make_data([gc.DataTuple('app_enable', bool_val=False)], 'trigger_timer_one_shot')]
      )

finally:
    # Tear down the stream when done
    client.tear_down_stream()
    sys.exit()
