import json
import os
import sys
import threading
from subprocess import Popen, PIPE
import yaml  # pip install pyyaml

FILE_INTERVAL = "\\" if os.name == "nt" else "/"
FILE_PATH = sys.path[0] + FILE_INTERVAL
CONFIG_PATH = sys.path[0] + FILE_INTERVAL + "config.py"


class Table:

    def __init__(self, p4_file_name):
        self.p4_file_name_ = p4_file_name
        # for test
        self.file_lock = threading.Lock()

        f = open(CONFIG_PATH, encoding="utf-8", mode="w")
        f.write("from ipaddress import ip_address as ip\n")
        f.write("p4 = bfrt.{0}.pipe\n".format(p4_file_name))
        f.close()

    def __del__(self):
        pass

    def execute(self):
        # MARK: 修改为增加了线程同步
        with self.file_lock:
            table_file = open(CONFIG_PATH, encoding="utf-8", mode="a")
            table_file.write("bfrt.complete_operations()\n")
            table_file.close()

            f = open(FILE_PATH + "configuration.yml", "r", encoding="utf-8")
            content = f.read()
            parameter = yaml.full_load(content)
            f.close()
            p = Popen(
                "bash $SDE/run_bfshell.sh -b " + CONFIG_PATH,
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                env={"SDE": parameter["SDE"], "SDE_INSTALL": parameter["SDE_INSTALL"]},
            )
            out, err = p.communicate()
            a = out.decode()
            # print(a)
            # MARK: 修改为每次结束清空文件剩余内容，但保留前两行
            with open(CONFIG_PATH, "w", encoding="utf-8") as file:
                file.write("from ipaddress import ip_address as ip\n")
                file.write("p4 = bfrt.{0}.pipe\n".format(self.p4_file_name_))
                file.close()

            # MARK: 修改为如果发生插入错误则进行打印
            if "err" in a or "Err" in a or "fail" in a or "Fail" in a:
                if "Already exists" in a:
                    print("\033[31mError: Already exists\033[0m")
                    return -1
                else:
                    print("\033[31m" + a + "\033[0m")
                    return False
            else:
                return True

    def table_add(self, **kwargs):
        list_temp = [0, 0, 0]
        for key, value in kwargs.items():
            if key == "action":
                list_temp[2] = "add_with_" + value + "("
            elif key == "table_name":
                list_temp[1] = value + "."
            elif key == "block_name":
                list_temp[0] = value + "."
            else:
                list_temp.append(key + "=" + value + ",")
        table_file = open(CONFIG_PATH, encoding="utf-8", mode="a")
        table_file.write("p4." + "".join(list_temp)[:-1] + ")\n")
        # table_file.write('bfrt.complete_operations()\n')
        table_file.close()
        # return self.exec_command()
        return True

    def table_delete(self, **kwargs):
        list_temp = [0, 0]
        for key, value in kwargs.items():
            if key == "table_name":
                list_temp[1] = value + ".delete("
            elif key == "block_name":
                list_temp[0] = value + "."
            else:
                list_temp.append(key + "=" + value + ",")
        table_file = open(CONFIG_PATH, encoding="utf-8", mode="a")
        table_file.write("p4." + "".join(list_temp)[:-1] + ")\n")
        # table_file.write('bfrt.complete_operations()\n')
        table_file.close()
        # return self.exec_command()
        return True

    def table_clear(self, **kwargs):
        list_temp = [0, 0]
        for key, value in kwargs.items():
            if key == "table_name":
                list_temp[1] = value + ".clear("
            elif key == "block_name":
                list_temp[0] = value + "."
        table_file = open(CONFIG_PATH, encoding="utf-8", mode="a")
        table_file.write("p4." + "".join(list_temp)[:-1] + "()\n")
        # table_file.write('bfrt.complete_operations()\n')
        table_file.close()
        # return self.exec_command()
        return True

    """
    def execute(self):
        json_file = open(json_path,encoding="utf-8")
        
        for line in json_file:
            dict_temp = json.loads(line)
            try:
                if dict_temp["type"] == "add":
                    del dict_temp["type"]
                    self.table_add(**dict_temp)
                elif dict_temp["type"] == "delete":
                    del dict_temp["type"]
                    self.table_delete(**dict_temp)
            except Exception as e:
                print("error! no type")
                json_file.close
                return
        
        table_file = open(CONFIG_PATH,encoding="utf-8",mode="a")
        table_file.write('bfrt.complete_operations()\n')
        table_file.close()
        return self.exec_command()
        json_file.close()
    """


if __name__ == "__main__":
    # for test only
    table = Table(p4_file_name="vNAT")
    para = {}
    para["table_name"] = "forward_port"
    para["block_name"] = "Ingress"
    para["action"] = "forward"
    para["ingress_port"] = "0"
    para["port"] = "2"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv4_dst_check"
    para["block_name"] = "Ingress"
    para["action"] = "set_dst_token"
    para["dstAddr"] = "ip('192.168.0.0')"
    para["dstAddr_p_length"] = "16"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv4_src_check"
    para["block_name"] = "Ingress"
    para["action"] = "set_src_token"
    para["srcAddr"] = "ip('192.168.0.0')"
    para["srcAddr_p_length"] = "16"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv6_dst_check"
    para["block_name"] = "Ingress"
    para["action"] = "set_dst_token"
    para["dstAddr"] = "ip('2001::0')"
    para["dstAddr_p_length"] = "16"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv6_src_check"
    para["block_name"] = "Ingress"
    para["action"] = "set_src_token"
    para["srcAddr"] = "ip('2001::0')"
    para["srcAddr_p_length"] = "16"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv4_SNAT"
    para["block_name"] = "Ingress"
    para["action"] = "mod_ipv4_src"
    para["srcAddr"] = "ip('192.168.0.100')"
    para["srcPort"] = "12345"
    para["natsrcaddr"] = "ip('1.2.3.4')"
    para["natsrcport"] = "1145"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv4_SNAT_t"
    para["block_name"] = "Ingress"
    para["action"] = "mod_ipv4_src_t"
    para["srcAddr"] = "ip('192.168.0.100')"
    para["srcPort"] = "12345"
    para["natsrcaddr"] = "ip('1.2.3.4')"
    para["natsrcport"] = "1145"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv6_SNAT"
    para["block_name"] = "Ingress"
    para["action"] = "mod_ipv6_src"
    para["srcAddr"] = "ip('2001::1')"
    para["srcPort"] = "12345"
    para["natsrcaddr"] = "ip('2222::1')"
    para["natsrcport"] = "1145"
    table.table_add(**para)

    para = {}
    para["table_name"] = "ipv6_SNAT_t"
    para["block_name"] = "Ingress"
    para["action"] = "mod_ipv6_src_t"
    para["srcAddr"] = "ip('2001::1')"
    para["srcPort"] = "12345"
    para["natsrcaddr"] = "ip('2222::1')"
    para["natsrcport"] = "1145"
    table.table_add(**para)

    para = {}
    para["table_name"] = "assign_te_index"
    para["block_name"] = "Ingress"
    para["action"] = "set_index"
    para["ipv4_dstAddr"] = "ip('192.168.0.101')"
    para["ipv4_dstAddr_mask"] = "0xffffffff"
    para["index"] = "1"
    para["threshold"] = "5"
    table.table_add(**para)

    para = {}
    para["table_name"] = "assign_te_index"
    para["block_name"] = "Ingress"
    para["action"] = "set_index"
    para["ipv4_dstAddr"] = "ip('192.168.0.102')"
    para["ipv4_dstAddr_mask"] = "0xffffffff"
    para["index"] = "2"
    para["threshold"] = "3"
    table.table_add(**para)

    para = {}
    para["table_name"] = "forward_port_list"
    para["block_name"] = "Ingress"
    para["action"] = "set_port_list"
    para["te_counter_index"] = "1"
    para["port1"] = "1"
    para["port2"] = "3"
    para["port3"] = "5"
    para["port4"] = "7"
    para["port5"] = "9"
    para["port6"] = "11"
    para["port7"] = "13"
    para["port8"] = "15"
    table.table_add(**para)

    para = {}
    para["table_name"] = "forward_port_list"
    para["block_name"] = "Ingress"
    para["action"] = "set_port_list"
    para["te_counter_index"] = "2"
    para["port1"] = "2"
    para["port2"] = "4"
    para["port3"] = "6"
    para["port4"] = "8"
    para["port5"] = "10"
    para["port6"] = "12"
    para["port7"] = "14"
    para["port8"] = "16"
    table.table_add(**para)

    table.execute()

    del table
