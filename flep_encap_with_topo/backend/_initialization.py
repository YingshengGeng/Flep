# Import necessary libraries

import sys
import os
import yaml
import time

switch_index = sys.argv[1]

#system arguments p4name portlist4multicast
FILE_INTERVAL = '\\' if os.name == 'nt' else '/'
FILE_PATH = sys.path[0] + FILE_INTERVAL
f = open(FILE_PATH + 'configuration.yml', 'r')
content = yaml.safe_load(f.read())
f.close()
P4_NAME = content['P4_NAME']

PORT_LIST_INDEX = content['PORT_LIST' + "_" + str(switch_index)]
PORT_LIST_FOR_MC = list(PORT_LIST_INDEX.keys())

PORT_LIMIT = content['PORT_LIMIT' + "_" + str(switch_index)]


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
# Define a function to associate a multicast group ID with a multicast node ID
def associate(mgid_table, target, mgid, node_id, xid=None):
    # Set XID validity and value based on input
    use_xid = 1 if xid is not None else 0
    xid_val = xid if xid is not None else 0
    
    # Modify the multicast group ID table to associate it with the node ID
    mgid_table.entry_mod_inc(
        target,
        [mgid_table.make_key([gc.KeyTuple('$MGID', mgid)])],
        [mgid_table.make_data([
            gc.DataTuple('$MULTICAST_NODE_ID', int_arr_val=[node_id]),
            gc.DataTuple('$MULTICAST_NODE_L1_XID_VALID', bool_arr_val=[use_xid]),
            gc.DataTuple('$MULTICAST_NODE_L1_XID', int_arr_val=[xid_val])])],
        bfruntime_pb2.TableModIncFlag.MOD_INC_ADD
    )

def add_port(bfrt_info, target):
    port_table = bfrt_info.table_get("$PORT")
    print("Add ports")
    for port, limit in PORT_LIMIT.items():
        port_table.entry_add(
            target,
            [port_table.make_key([gc.KeyTuple('$DEV_PORT', port)])],
            [port_table.make_data([gc.DataTuple('$SPEED', str_val="BF_SPEED_" + limit),
                                        gc.DataTuple('$FEC', str_val="BF_FEC_TYP_NONE"),
                                        gc.DataTuple('$PORT_ENABLE', bool_val=True)])])
    print("Wait for port up")
    time.sleep(5)
    
# Establish a connection to the BFRuntime server
try:
    grpc_addr = "0.0.0.0:50052"
    client_id = 0
    device_id = 0
    pipe_id = 0xFFFF  # Pipe ID; FFFF indicates all pipes
    client = gc.ClientInterface(grpc_addr, client_id, device_id)
    target = gc.Target(device_id, pipe_id)
    client.bind_pipeline_config(P4_NAME)  # Bind the pipeline configuration to the device

    # Retrieve information about the bound pipeline
    bfrt_info = client.bfrt_info_get(P4_NAME)

    # Access the required tables
    mgid_table = bfrt_info.table_get("$pre.mgid")
    node_table = bfrt_info.table_get("$pre.node")
    multicast_table = bfrt_info.table_get("Ingress.multicast_send_fleptopo")
    port_index_table = bfrt_info.table_get("Ingress.get_port_index")

    # Ports configuration
    add_port(bfrt_info, target)
    
    # Multicast group configuration
    print("Creating multicast group.")
    mgid = 1  # Multicast Group ID
    mgid_table.entry_add(
        target,
        [mgid_table.make_key([gc.KeyTuple('$MGID', mgid)])]
    )

    # Create a multicast node associated with the multicast group
    print("Creating multicast node.")
    mbr_lags = []  # Member LAG IDs (not used in this example)
    rid = 0  # RID (Replication ID); not used in this example
    node_id = 1  # Multicast Node ID

    #NOTE: Modified from a yml configuration file
    #mbr_ports = [1, 2, 3, 4, 5]  # Member ports
    mbr_ports = PORT_LIST_FOR_MC
    node_table.entry_add(
        target,
        [node_table.make_key([gc.KeyTuple('$MULTICAST_NODE_ID', node_id)])],
        [node_table.make_data([
            gc.DataTuple('$MULTICAST_RID', rid),
            gc.DataTuple('$MULTICAST_LAG_ID', int_arr_val=mbr_lags),
            gc.DataTuple('$DEV_PORT', int_arr_val=mbr_ports)
        ])]
    )

    # Associate the multicast group with the multicast node
    print("Associating multicast group with node.")
    associate(mgid_table, target, mgid, node_id)

    # Set the multicast send action for the specified message type
    print("Setting multicast send action.")
    multicast_table.entry_add(
        target,
        [multicast_table.make_key([gc.KeyTuple('hdr.fleptopo.messagetype', 0)])],
        [multicast_table.make_data([gc.DataTuple('groupid', mgid)], 'multiportsend')]
    )

finally:
    # Tear down the stream when done
    client.tear_down_stream()
    sys.exit()
