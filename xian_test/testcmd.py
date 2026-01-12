import cmd
import requests
import yaml
import os
import sys


# 连接字典
connect_dict = {
    "R1": [
        {"port": 1, "sw_ind": "R2"},
    ],
    "R2": [
        {"port": 1, "sw_ind": "R1"},
        {"port": 2, "sw_ind": "R2"},
    ],
    "R3": [
        {"port": 1, "sw_ind": "R2"},
    ],
}
FILE_INTERVAL = "\\" if os.name == "nt" else "/"
# 读取配置文件
CONFIG_PATH = (
    ".."
    + FILE_INTERVAL
    + "flep_encap_with_topo"
    + FILE_INTERVAL
    + "backend"
    + FILE_INTERVAL
    + "configuration.yml"
)
MAPPING_PATH = "mapping.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    parameter_ip = yaml.safe_load(f)

with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    parameter_mapping = yaml.safe_load(f)

port_mapping = dict(parameter_mapping["MAPPING_LIST"])
route2xlabel_mapping = dict(parameter_mapping["MAPPING_LIST_Route_RE"])


# 构建URL
def build_url(id):
    id_str = "SOUTHBOUND_SERVER_IP_{}".format(id)
    return "http://{}:11451".format(parameter_ip[id_str])


# 添加标签
def add_label(target_ids):
    # 所以这里要求的输入是数字
    for id in target_ids:
        url = build_url(id)
        for link in connect_dict["R{}".format(id)]:
            port = link["port"]
            sw_index = link["sw_ind"]
            data = {
                "label": route2xlabel_mapping[sw_index],
                "port": str(port),
                # "port": port_mapping[str(port) if id != 1 else f"{port}_R{id}"],
            }
            send_post_request(url, "label/add", data)


# 发送POST请求
def send_post_request(url, endpoint, data):
    full_url = "{}/{}".format(url, endpoint)
    try:
        response = requests.post(full_url, json=data)
        response.raise_for_status()
        print("Request was successful: {}".format(response.text))
        return response.text
    except requests.RequestException as e:
        print("Request failed: {}".format(response.text))
        return None


class NetworkConfigCLI(cmd.Cmd):
    intro = (
        "Welcome to the Network Configuration CLI. Type help or ? to list commands.\n"
    )
    prompt = "(network) "

    def do_vnf_version(self, arg):
        # "vnf version"
        print("可编程虚拟网元软件包V1.0")

    def do_label_version(self, arg):
        # "label version"
        print("基于标签转发的定制化协议栈V1.0")

    def do_environment_version(self, arg):
        # "environment version"
        print("P4可编程开发环境V1.0")
        
    def do_add_label(self, arg):
        "Add label forwarding rules to specified routers: add_label R10"
        routers = arg.split()
        target_ids = [s[1:] for s in routers]
        # 这里的输入格式
        add_label(target_ids)

    def do_get_label(self, arg):
        "Get label forwarding rules to specified routers: get_label R10"
        routers = arg.split()
        for router in routers:
            url = build_url(router[1:])
            send_post_request(url, "label/inquire", {})
        
    def do_clear_labels(self, arg):
        "Clear labels: clear_labels R10 R1 R4 R5 R3 R2"
        routers = arg.split()
        for router in routers:
            url = build_url(router[1:])
            send_post_request(url, "label/clear", {})

    def do_add_port_forward(self, arg):
        "Add port forwarding rules: add_port_forward R1 8 7"
        args = arg.split()
        if len(args) != 3:
            print("Usage: add_port_forward <router> <ingress_port> <egress_port>")
            return
        router, ingress_port, egress_port = args
        url = build_url(router[1:])
        # 这里的输入格式
        data = {
            # "ingress_port": port_mapping[ingress_port],
            # "port": port_mapping[egress_port],
            "ingress_port": ingress_port,
            "port": egress_port,
        }
        send_post_request(url, "forward/port/add", data)

    def do_clear_port_forward(self, arg):
        "Clear port forward rules: clear_port_forward R10"
        args = arg.split()
        if len(args) != 1:
            print("Usage: clear_port_forward <router>")
            return
        router = args[0]
        url = build_url(router[1:])
        send_post_request(url, "forward/port/clear", {})

    def do_add_ipv4_forward(self, arg):
        "Add IPv4 forwarding rule with label stack: add_ipv4_forward R10 10.1.1.2/16 10.2.2.2/16 5001 5002 R1 R4 R2 R11"
        args = arg.split()
        if len(args) < 7:
            print(
                "Usage: add_ipv4_forward <router> <ipv4_src> <ipv4_dst> <tp_src> <tp_dst> <label_list...>"
            )
            return
        router, ipv4_src, ipv4_dst, tp_src, tp_dst, *label_list = args
        url = build_url(router[1:])
        path_str = ",".join([str(route2xlabel_mapping[label]) for label in label_list])
        data = {
            "ipv4_src": ipv4_src,
            "ipv4_dst": ipv4_dst,
            "tp": "udp",
            "tp_src": tp_src,
            "tp_dst": tp_dst,
            "label_list": path_str,
        }
        send_post_request(url, "forward/ipv4/add", data)

    def do_delete_ipv4_forward(self, arg):
        "Delete IPv4 forwarding rule: delete_ipv4_forward R10 10.1.1.2/16 10.2.2.2/16"
        args = arg.split()
        if len(args) != 3:
            print("Usage: delete_ipv4_forward <router> <ipv4_src> <ipv4_dst>")
            return
        router, ipv4_src, ipv4_dst = args
        url = build_url(router[1:])
        data = {
            "ipv4_src": ipv4_src,
            "ipv4_dst": ipv4_dst,
        }
        send_post_request(url, "forward/ipv4/clear", data)
        
    def do_get_ipv4_forward(self, arg):
        "Get IPv4 forwarding rule: get_ipv4_forward R10 10.1.1.2/16 10.2.2.2/16"
        args = arg.split()
        if len(args) != 3:
            print("Usage: get_ipv4_forward <router> <ipv4_src> <ipv4_dst>")
            return
        router, ipv4_src, ipv4_dst = args
        url = build_url(router[1:])
        data = {
            "ipv4_src": ipv4_src,
            "ipv4_dst": ipv4_dst,
        }
        send_post_request(url, "forward/ipv4/inquire", data)

    def do_add_local_net(self, arg):
        "Set local network: add_local_net R11 10.1.1.2 16"
        args = arg.split()
        if len(args) != 3:
            print("Usage: add_local_net <router> <Addr> <Addr_p_length>")
            return
        router, addr, addr_p_length = args
        url = build_url(router[1:])
        data = {"Addr": addr, "Addr_p_length": addr_p_length}
        send_post_request(url, "nat/ipv4/local/add", data)

    def do_clear_local_net(self, arg):
        "Clear local network: clear_local_net R11 10.1.1.2 16"
        args = arg.split()
        if len(args) != 3:
            print("Usage: clear_local_net <router> <Addr> <Addr_p_length>")
            return
        router, addr, addr_p_length = args
        url = build_url(router[1:])
        data = {"Addr": addr, "Addr_p_length": addr_p_length}
        send_post_request(url, "nat/ipv4/local/clear", data)

    def do_add_in2out_fw_rule(self, arg):
        "Add in2out firewall rule: add_in2out_fw_rule R11 10.2.2.2 5002"
        args = arg.split()
        if len(args) != 3:
            print("Usage: add_in2out_fw_rule <router> <ipv4_dstAddr> <udp_dstPort>")
            return
        router, ipv4_dst_addr, udp_dst_port = args
        url = build_url(router[1:])
        data = {"ipv4_dstAddr": ipv4_dst_addr, "udp_dstPort": udp_dst_port}
        send_post_request(url, "fw/ipv4/in_to_out/add", data)

    def do_delete_in2out_fw_rule(self, arg):
        "Delete in2out firewall rule: delete_in2out_fw_rule R11 10.2.2.2 5002"
        args = arg.split()
        if len(args) != 3:
            print("Usage: delete_in2out_fw_rule <router> <ipv4_dstAddr> <udp_dstPort>")
            return
        router, ipv4_dst_addr, udp_dst_port = args
        url = build_url(router[1:])
        data = {"ipv4_dstAddr": ipv4_dst_addr, "udp_dstPort": udp_dst_port}
        send_post_request(url, "fw/ipv4/in_to_out/clear", data)

    def do_add_in2out_white_fw_rule(self, arg):
        "Add in2out firewall rule: add_in2out_fw_rule R11 10.2.2.2 5002"
        args = arg.split()
        if len(args) != 3:
            print("Usage: do_add_in2out_white_fw_rule <router> <ipv4_dstAddr> <udp_dstPort>")
            return
        router, ipv4_dst_addr, udp_dst_port = args
        url = build_url(router[1:])
        data = {"ipv4_dstAddr": ipv4_dst_addr, "udp_dstPort": udp_dst_port}
        send_post_request(url, "white_fw/ipv4/in_to_out/add", data)

    def do_delete_in2out_white_fw_rule(self, arg):
        "Delete in2out firewall rule: delete_in2out_fw_rule R11 10.2.2.2 5002"
        args = arg.split()
        if len(args) != 3:
            print("Usage: do_delete_in2out_white_fw_rule <router> <ipv4_dstAddr> <udp_dstPort>")
            return
        router, ipv4_dst_addr, udp_dst_port = args
        url = build_url(router[1:])
        data = {"ipv4_dstAddr": ipv4_dst_addr, "udp_dstPort": udp_dst_port}
        send_post_request(url, "white_fw/ipv4/in_to_out/clear", data)

    def do_add_snat_rule(self, arg):
        "Add SNAT rule: add_snat_rule R11 10.1.1.2 5001 udp 1.2.3.4 5003"
        args = arg.split()
        if len(args) != 6:
            print(
                "Usage: add_snat_rule <router> <Addr> <Port> <TP> <natAddr> <natPort>"
            )
            return
        router, addr, port, tp, nat_addr, nat_port = args
        url = build_url(router[1:])
        data = {
            "Addr": addr,
            "Port": port,
            "TP": tp,
            "natAddr": nat_addr,
            "natPort": nat_port,
        }
        send_post_request(url, "nat/ipv4/snat/add", data)

    def do_delete_snat_rule(self, arg):
        "Delete SNAT rule: delete_snat_rule R11 10.1.1.2 5001 udp 1.2.3.4 5003"
        args = arg.split()
        if len(args) != 6:
            print(
                "Usage: delete_snat_rule <router> <Addr> <Port> <TP> <natAddr> <natPort>"
            )
            return
        router, addr, port, tp, nat_addr, nat_port = args
        url = build_url(router[1:])
        data = {
            "Addr": addr,
            "Port": port,
            "TP": tp,
            "natAddr": nat_addr,
            "natPort": nat_port,
        }
        send_post_request(url, "nat/ipv4/snat/clear", data)

    def do_add_lb(self, arg):
        "Add load balancing: add_lb R11 10.2.2.2 1 33,2"
        args = arg.split()
        if len(args) != 4:
            print("Usage: add_lb <router> <ipv4_dstAddr> <index> <port_list>")
            return
        router, ipv4_dst_addr, index, port_list = args
        url = build_url(router[1:])
        ports = [port_mapping[port] for port in port_list.split(",")]
        data = {
            "ipv4_dstAddr": ipv4_dst_addr,
            "index": index,
            "port_list": ",".join(ports),
        }
        send_post_request(url, "te/add", data)

    def do_delete_lb(self, arg):
        "Delete load balancing: delete_lb R11 10.2.2.2 1 33,2"
        args = arg.split()
        if len(args) != 4:
            print("Usage: delete_lb <router> <ipv4_dstAddr> <index> <port_list>")
            return
        router, ipv4_dst_addr, index, port_list = args
        url = build_url(router[1:])
        ports = [port_mapping[port] for port in port_list.split(",")]
        data = {
            "ipv4_dstAddr": ipv4_dst_addr,
            "index": index,
            "port_list": ",".join(ports),
        }
        send_post_request(url, "te/clear", data)

    def do_restore_state(self, arg):
        "Restore state for specified routers: restore_state R10 R1 R4 R5 R3 R2"
        routers = arg.split()
        target_ids = [s[1:] for s in routers]

        for id in target_ids:
            url = build_url(id)
            response = send_post_request(url, "label/clear", {})
            print(response or "Failed to clear labels on R{}".format(id))
            print("Delete labels to R{}".format(id))
            response = send_post_request(url, "forward/port/clear", {})
            print(response or "Failed to clear port forward rules  on R{}".format(id))
            print("Clear port forward rules to R{}".format(id))

    def do_exit(self, arg):
        "Exit the CLI: exit"
        print("Exiting...")
        return True


if __name__ == "__main__":
    NetworkConfigCLI().cmdloop()

