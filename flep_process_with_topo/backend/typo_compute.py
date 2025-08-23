import sys
import json
import os


def _dump_register(control_name, register_name, index_1, index_2):
    label_register = bfrt_info.table_get(
        "Ingress." + control_name + "." + register_name
    )
    save_dict = {}
    for index in range(index_1, index_2 + 1):
        resp = label_register.entry_get(
            target,
            [label_register.make_key([gc.KeyTuple("$REGISTER_INDEX", index)])],
            {"from_hw": True},
        )
        data, _ = next(resp)
        data_dict = data.to_dict()
        data0 = data_dict["Ingress." + control_name + "." + register_name + ".f1"][0]
        data1 = data_dict["Ingress." + control_name + "." + register_name + ".f1"][1]
        if data0 == 0 and data1 != 0:
            save_dict[index] = data1
        elif data0 != 0 and data1 == 0:
            save_dict[index] = data0
        else:
            save_dict[index] = 0

    return save_dict


def _latency_revision(latency_in_dec):
    latency_hex_32 = hex(latency_in_dec)
    latency_hex_48 = latency_hex_32
    latency_dec = int(latency_hex_48, 16)
    return latency_dec


def compute_adjacency(local_label):
    json_list = []
    # data = request.json()
    index1 = 0
    index2 = 127
    label_dict = _dump_register("labeldatacache", "bw_register", index1, index2)
    # print(label_dict)
    port_dict = _dump_register("portdatacache", "bw_register", index1, index2)
    latency_dict = _dump_register("latencydatacache", "bw_register", index1, index2)
    for index in range(index1, index2 + 1):
        if label_dict[index] != 0:
            temp_dict = {}
            temp_dict["label"] = hex(label_dict[index])
            temp_dict["port"] = str(port_dict[index])
            temp_dict["latency"] = str(_latency_revision(latency_dict[index]))
            json_list.append(temp_dict)
    # json_list.append({"local_label": local_label})
    result = json.dumps(json_list)
    # print(result)
    return result


if __name__ == "__main__":
    sde_install = sys.argv[1]
    p4_name = sys.argv[2]
    local_label = sys.argv[3]
    python_version = sys.argv[4]
    
    grpc_addr = "0.0.0.0:50052"

    client_id = 0
    device_id = 0
    pipe_id = 0xFFFF  # Pipe ID; FFFF indicates all pipes Bind the pipeline configuration to the device
    sys.path.extend([
        '{}/lib/{}/site-packages/tofino'.format(sde_install, python_version),
        '{}/lib/{}/site-packages/p4testutils'.format(sde_install, python_version),
        '{}/lib/{}/site-packages'.format(sde_install, python_version),
        '{}/lib/{}/site-packages/tofino/bfrt_grpc/'.format(sde_install, python_version)
    ])
    import bfrt_grpc.client as gc
    import bfruntime_pb2

    try:
        client = gc.ClientInterface(grpc_addr, client_id, device_id)
        target = gc.Target(device_id, pipe_id)
        client.bind_pipeline_config(p4_name)

        # Retrieve information about the bound pipeline
        bfrt_info = client.bfrt_info_get(p4_name)
        result = compute_adjacency(local_label)
        print(result)
        sys.stdout.flush()

    finally:
        # Tear down the stream when done
        client.tear_down_stream()
        sys.exit()
