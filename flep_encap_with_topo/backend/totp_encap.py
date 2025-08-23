import time
import pyotp
import sys
import threading
import json
from queue import Queue
from datetime import datetime, timedelta
from tableAPI_new import Table
from dbAPI_new import DB


class TOTPManager:
    def __init__(self, p4_file_name, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME):
        # def __init__(self, p4_file_name):
        self.table = Table(p4_file_name)
        self.db = DB(DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

        self.secret_key = "IILAVD4MDXRF4DNJM6VQZMTU227ESRZO"
        self.curr_key = "0xFFFFFFFF"
        self.default_key = "0xFFFFFFFF"
        self.counter = 0
        self.key_lock = threading.Lock()

        self.DEFAULT_PERIOD = 30
        self.period = 30
        self.period_lock = threading.Lock()

        self.command_queue = Queue()
        self.event = threading.Event()

        self.forward_flep_protocols = ["ipv4", "ipv6"]
        self.INGRESS_BLOCK_NAME = "Ingress"
        self.EGRESS_BLOCK_NAME = "Egress"
        self.KEY_MATCH_TABLE_NAME = "key_match_tbl"
        self.INSERT_KEY_TABLE_NAME = "insert_key_tbl"
        self.INSERT_PAST_KEY_TABLE_NAME = "insert_past_key_tbl"
        self.IS_VERIFY_TABLE_NAME = "is_verify_tbl"

        self.periodic_thread = threading.Thread(
            target=self.periodic_function, args=(self.command_queue, self.event)
        )

        self.periodic_thread.daemon = False

        self.para_to_key = {
            "ipv4_src": "ipv4_srcAddr",
            "ipv4_dst": "ipv4_dstAddr",
            "ipv6_src": "ipv6_srcAddr",
            "ipv6_dst": "ipv6_dstAddr",
            "ipv4_tp": "ipv4_protocol",
            "ipv6_tp": "ipv6_nextheader",
            "tcp_tp_src": "tcp_srcPort",
            "tcp_tp_dst": "tcp_dstPort",
            "udp_tp_src": "udp_srcPort",
            "udp_tp_dst": "udp_dstPort",
            "label_list": "label_list",
        }

        # self.para_to_key = {
        #     "ipv4_src": "ipv4_srcaddr",
        #     "ipv4_dst": "ipv4_dstaddr",
        #     "ipv6_src": "ipv6_srcaddr",
        #     "ipv6_dst": "ipv6_dstaddr",
        #     "ipv4_tp": "ipv4_protocol",
        #     "ipv6_tp": "ipv6_nextheader",
        #     "tcp_tp_src": "tcp_srcport",
        #     "tcp_tp_dst": "tcp_dstport",
        #     "udp_tp_src": "udp_srcPort",
        #     "udp_tp_dst": "udp_dstPort",
        #     "label_list": "label_list",
        # }
        self.identify_counter = 1

    def manage_period(self, operation, updated_period=1):
        """
        管理周期的函数，根据操作类型执行相应的操作。

        参数:
        operation (str): 操作类型，可以是"get"（获取当前周期）、"update"（更新周期）、"delete"（重置周期）。
        updated_period (int, 可选): 用于更新周期的值，默认为5。

        返回:
        int: 当前的周期值。
        """
        res = self.DEFAULT_PERIOD
        with self.period_lock:
            if operation == "get":
                res = self.period // 30
            elif operation == "update":
                self.period = updated_period * 30
            elif operation == "delete":
                self.period = 30
        return res

    def calculate_totp(self):
        """
        计算当前的TOTP值。

        TOTP (Time-based One-Time Password) 是一种基于时间的一次性密码算法。这个方法使用预共享的密钥和当前时间
        切片来生成一个一次性密码。生成的密码以十六进制字符串的形式返回。

        Returns:
            str: 当前时间窗口内的TOTP值，以十六进制字符串形式表示。
        """
        totp = pyotp.TOTP(self.secret_key)
        self.curr_key = hex(int(totp.now()))
        return self.curr_key

    def calculate_multi_totp(self, num=1):
        """
        计算几个周期的的TOTP值。
        Returns:
            str list: 当前时间窗口内的TOTP值，以十六进制字符串形式表示。
        """
        totp = pyotp.TOTP(self.secret_key)
        curr_keys = []
        # 获取当前时间戳
        current_time = datetime.now()
        current_period_otp = totp.at(current_time)
        if num == 3:
            # 计算前一个周期的开始时间
            previous_period_start = current_time - timedelta(seconds=self.period)
            previous_period_otp = totp.at(previous_period_start)
            curr_keys.append(hex(int(previous_period_otp)))
        if num >= 2:
            curr_keys.append(hex(int(current_period_otp)))
        if num >= 1:
            # 计算下一个周期的开始时间
            next_period_start = current_time + timedelta(seconds=self.period)
            next_period_otp = totp.at(next_period_start)
            curr_keys.append(hex(int(next_period_otp)))
        return curr_keys
    def calculate_multi_totp_v2(self, num=1):
        """
        计算几个周期的的TOTP值。
        Returns:
            str list: 当前时间窗口内的TOTP值，以十六进制字符串形式表示。
        """
        totp = pyotp.TOTP(self.secret_key)
        curr_keys = []
        # 获取当前时间戳
        current_time = datetime.now()
        current_period_otp = totp.at(current_time)
        if num == 3:
            # 计算0, +1, +2周期的开始时间
            for i in range(0, 4):
                next_period_start = current_time + timedelta(seconds=i * self.period)
                next_period_otp = totp.at(next_period_start)
                curr_keys.append(hex(int(next_period_otp)))
        if num == 1:
            # 计算+2周期的开始时间
            next_period_start = current_time + timedelta(seconds=2 * self.period)
            next_period_otp = totp.at(next_period_start)
            curr_keys.append(hex(int(next_period_otp)))
        return curr_keys
    def write_key_to_key_match_tbl(self, update_key, update_key_index):
        """
        更新键匹配表中的键值和索引。


        :param update_key: 需要更新的键值。
        :param update_key_index: 需要更新的键索引。
        :return: True表示更新成功, False表示更新失败。
        """

        para = {}
        para["table_name"] = self.KEY_MATCH_TABLE_NAME
        para["block_name"] = self.EGRESS_BLOCK_NAME
        para["action"] = "NoAction"

        para["key"] = update_key
        para["key_index"] = str(update_key_index)

        self.table.table_add(**para)
        ret = self.table.execute()

        data = {"key": update_key, "key_index": str(update_key_index)}
        if ret:
            self.db.add(para["table_name"], data)

        return ret

    def add_default_verification_entry(self):
        """
        向验证表中添加默认条目。

        :return: True表示添加成功, False表示添加失败。
        """
        para = {
            "table_name": self.IS_VERIFY_TABLE_NAME,
            "block_name": self.EGRESS_BLOCK_NAME,
            "action": "start_verify",
            "key": "0xFFFFFFFF",  # Example key, adjust as needed
            "key_mask": "0x00000000",  # Example key mask, adjust as needed
        }

        self.table.table_add(**para)
        ret = self.table.execute()

        # data = {"key": "0xFFFFFFFF"}
        # if ret:
        #     self.db.add(para["table_name"], data)

        return ret

    def delete_default_verification_entry(self):
        """
        从验证表中删除默认条目。

        :return: True表示删除成功, False表示删除失败。
        """
        para = {
            "table_name": self.IS_VERIFY_TABLE_NAME,
            "block_name": self.EGRESS_BLOCK_NAME,
            "key": "0xFFFFFFFF",
            "key_mask": "0x00000000",
        }

        self.table.table_delete(**para)

        ret = self.table.execute()
        # data = {"key": "0xFFFFFFFF"}
        # if ret:
        #     self.db.delete(para["table_name"], data)

        return ret

    def read_key_match_tbl(self):
        """
        Reads the key_match_tbl from the database.
        """
        key_entries = {}

        table_name = self.KEY_MATCH_TABLE_NAME
        key_entries = self.db.query(table_name, {})

        return key_entries

    def clear_key_match_tbl(self):
        """
        Clears the key_match_tbl from the database.
        """
        table_name = self.KEY_MATCH_TABLE_NAME
        para = {}
        para["table_name"] = table_name
        para["block_name"] = self.EGRESS_BLOCK_NAME

        self.table.table_clear(**para)
        ret = self.table.execute()
        if ret:
            self.db.clear(table_name)

    def delete_previous_key_match_tbl(self, key_entries):
        """
        Delete the previous key from the hardware.
        """
        table_name = self.KEY_MATCH_TABLE_NAME
        para = {
            "table_name": table_name,
            "block_name": self.EGRESS_BLOCK_NAME,
        }

        # First time we needn't delete any key (counter = 1)
        if self.counter == 1:
            return
        # Others delete the key with lowest index
        low_elme = min(key_entries, key=lambda x: int(x["key_index"]))
        para["key"] = low_elme["key"]
        para["key_index"] = str(low_elme["key_index"])
        self.table.table_delete(**para)
        ret = self.table.execute()
        print(low_elme, ret)
        if ret:
            self.db.delete(para["table_name"], low_elme)

    def delete_previous_key_match_tbl_v2(self, key_entries):
        """
        Delete the previous key from the hardware.
        """
        table_name = self.KEY_MATCH_TABLE_NAME
        para = {
            "table_name": table_name,
            "block_name": self.EGRESS_BLOCK_NAME,
        }

        # First time we needn't delete any key (counter <= 3)
        if self.counter <= 2:
            return
        # Others delete the key with lowest index
        low_elme = min(key_entries, key=lambda x: int(x["key_index"]))
        para["key"] = low_elme["key"]
        para["key_index"] = str(low_elme["key_index"])
        self.table.table_delete(**para)
        ret = self.table.execute()
        print(low_elme, ret)
        if ret:
            self.db.delete(para["table_name"], low_elme)
    def clear_default_verification_entry(self):
        """
        Clears the insert_key_tbl from the hardware.
        """
        table_name = self.IS_VERIFY_TABLE_NAME
        para = {
            "table_name": table_name,
            "block_name": self.EGRESS_BLOCK_NAME,
        }

        self.table.table_clear(**para)
        ret = self.table.execute()
        return ret

    def clear_insert_key_tbl(self):
        """
        Clears the insert_key_tbl from the hardware.
        """
        table_name = self.INSERT_KEY_TABLE_NAME
        para = {}
        para["table_name"] = table_name
        para["block_name"] = self.EGRESS_BLOCK_NAME

        self.table.table_clear(**para)
        ret = self.table.execute()
        return ret

    def clear_insert_past_key_tbl(self):
        """
        Clears the insert_past_key_tbl from the hardware.
        """
        table_name = self.INSERT_PAST_KEY_TABLE_NAME
        para = {}
        para["table_name"] = table_name
        para["block_name"] = self.EGRESS_BLOCK_NAME

        self.table.table_clear(**para)
        ret = self.table.execute()
        return ret
    def delete_insert_key_tbl(self, past_key_index):

        para = {
            "table_name": self.INSERT_KEY_TABLE_NAME,
            "block_name": self.EGRESS_BLOCK_NAME,
            "identify_index": str(past_key_index),
            "identify_index_mask": "0x00"
        }

        self.table.table_delete(**para)
        ret = self.table.execute()
        return ret

    def write_key_to_insert_key_tbl(self, update_key, update_key_index):
        para = {
            "table_name": self.INSERT_KEY_TABLE_NAME,
            "block_name": self.EGRESS_BLOCK_NAME,
            "action": "insert_key",
            "identify_index": "0x00",
            "identify_index_mask": "0x00",
            "key": update_key,
            "key_index": str(update_key_index),
        }

        self.table.table_add(**para)
        ret = self.table.execute()
        # 不需要存入数据库
        return ret

    def write_key_to_insert_past_key_tbl(self, past_update_key, past_update_key_index):
        para = {
            "table_name": self.INSERT_PAST_KEY_TABLE_NAME,
            "block_name": self.EGRESS_BLOCK_NAME,
            "action": "insert_key",
            "identify_index": "0x00",
            "identify_index_mask": "0x00",
            "key": past_update_key,
            "key_index": str(past_update_key_index),
        }

        self.table.table_add(**para)
        ret = self.table.execute()
        # 不需要存入数据库
        return ret
    def periodic_function(self, command_queue, event):

        enable_verification = False
        verification_entry_added = False

        last_execution_time = time.time()
        while True:

            while not command_queue.empty():
                command = command_queue.get_nowait()
                if command == "0":
                    enable_verification = False
                elif command == "1":
                    enable_verification = True
                elif command == "2":
                    command_queue.task_done()
                    print("thread finish")
                    return
                print(
                    "Verification {}".format('enabled' if enable_verification else 'disabled'),
                    flush=True,
                )

            if enable_verification:
                self.period_lock.acquire()
                current_time = time.time()
                elapsed_time = current_time - last_execution_time
                print("elapsed_time: {}".format(elapsed_time), flush=True)
                if elapsed_time >= self.period or not verification_entry_added:
                    self.key_lock.acquire()
                    # current_password = self.calculate_totp()
                    passwords = []
                    if self.counter == 0:
                        # now and next
                        # passwords = self.calculate_multi_totp(num=2)
                        passwords = self.calculate_multi_totp_v2(num=3)
                    else:
                        # next
                        # passwords = self.calculate_multi_totp(num=1)
                        passwords = self.calculate_multi_totp_v2(num=1)
                    last_execution_time = current_time
                    self.counter += 1

                    if not verification_entry_added:
                        verification_entry_added = True
                        self.clear_key_match_tbl()
                        self.clear_default_verification_entry()
                        self.add_default_verification_entry()
                        # 写入默认表项(index 此时应该为0)
                        self.write_key_to_key_match_tbl(self.default_key, 0)

                    key_entries = self.read_key_match_tbl()
                    # self.clear_key_match_tbl()
                    # self.delete_previous_key_match_tbl(key_entries)
                    self.delete_previous_key_match_tbl_v2(key_entries)
                    # write the next key to the hardware
                    next_password = ""
                    # next_index = self.counter + 1
                    next_index = self.counter + 2
                    if len(passwords) > 1:
                        # write temp password
                        for i in range(0, 2):
                            self.write_key_to_key_match_tbl(passwords[i], self.counter + i)                        
                        next_password = passwords[2]
                    else:
                        next_password = passwords[0]
                    self.write_key_to_key_match_tbl(next_password, next_index)
                    print(
                        "Next Next TOTP: {}, index: {}".format(next_password, next_index),
                        flush=True,
                    )

                    # encap key only need the current key
                    curr_password = ""
                    past_password = ""
                    if len(passwords) > 1:
                        # write temp password
                        curr_password = passwords[0]
                        past_password = self.default_key
                    else:
                        # 保证获取的值有序的前提下
                        curr_password = key_entries[3]["key"]
                        past_password = key_entries[2]["key"]
                    
                    print(
                        "Cur TOTP: {}, index: {}".format(curr_password, self.counter),
                        flush=True,
                    )
                    self.write_key_to_insert_past_key_tbl(past_password, self.counter - 1)
                    self.clear_insert_key_tbl()
                    self.write_key_to_insert_key_tbl(curr_password, self.counter)
                    self.clear_insert_past_key_tbl()
                    
                    self.key_lock.release()

                current_time = time.time()
                elapsed_time = current_time - last_execution_time
                sleep_time = max(0, self.period - elapsed_time)
                if sleep_time == 0:
                    sleep_time = self.period

                self.period_lock.release()

                event.clear()
                event.wait(sleep_time)
            else:

                if verification_entry_added:
                    self.delete_default_verification_entry()
                    self.clear_key_match_tbl()
                    self.clear_insert_key_tbl()
                    verification_entry_added = False
                    self.counter = 0

                event.clear()  # 清除事件，以便下一次检查

                event.wait()

    def generate_mask(self, prefix_length):

        mask = (1 << prefix_length) - 1

        mask = mask << (32 - prefix_length)

        hex_mask = hex(mask)

        return hex_mask

    def convert_match_part_from_data(
        self, protocol, ori_data, para_flep, para_labels_list, need_label_para=True
    ):
        """
        根据给定的数据和协议类型, 转换P4表中匹配部分的数据结构。

        参数:
        protocol: string, 协议类型, 如ipv4或ipv6
        ori_data: dict, 原始数据，包含需要转换的字段。
        para_flep: dict, 用于存储转换后的标签头部参数。
        para_labels_list: list, 用于存储标签栈相关信息的列表。
        need_label_para: bool, default=True, 是否需要处理标签栈信息的列表。

        返回:
        无返回值, 但修改了para_flep和para_labels_list参数。

        可能的输入
        ipv4_src	10.0.0.1/16
        ipv4_dst	10.0.0.2/16
        ipv6_src	2001::1/32
        ipv6_dst	2002::2/32
        tp		    tcp, udp
        tp_src	    11451
        tp_dst	    2002
        label_list	1,3,4,6,8,12
        不考虑key, key index
        对于delete是从数据库中读出来的,所以keys应该有identify_index,否则无
        """
        paradict = [
            "ipv4_src",
            "ipv4_dst",
            "ipv6_src",
            "ipv6_dst",
            "tp",
            "tp_src",
            "tp_dst",
            "label_list",
        ]

        table_name = "flep_" + protocol + "_classifier"
        para_flep.update(
            {
                "table_name": table_name,
                "block_name": self.INGRESS_BLOCK_NAME,
                "action": "create_flep",
            }
        )
        # 处理identify_index
        if "identify_index" not in ori_data.keys():
            # 如果无，代表来自add操作, 则补上
            ori_data["identify_index"] = self.identify_counter
            self.identify_counter += 1
        para_flep.update({"identify_index": str(ori_data["identify_index"])})

        if need_label_para:
            label_list = ori_data["label_list"].rstrip(",").split(",")
            # 计算有多少个这样的表项
            label_depth = len(label_list)
            labels_tabel_name = "insert_" + protocol + "_label"
            # 12345678 --> [5,6,7,8], [1,2,3,4]
            insert_recir_count = 0
            while label_depth > 0:
                if label_depth >= 5:
                    para_labels_list.append(
                        {
                            "remain_labels_count": str(label_depth),
                            "recir_count": str(insert_recir_count),
                            "identify_index": para_flep["identify_index"],
                        }
                    )
                    
                    label_depth -= 5
                else:
                    para_labels_list.append(
                        {
                            "remain_labels_count": str(label_depth),
                            "recir_count": str(insert_recir_count),
                            "identify_index": para_flep["identify_index"],
                        }
                    )
                    label_depth = 0
                    break
                insert_recir_count += 1
            # 构建其他部分
            for para_label in para_labels_list:
                para_label.update(
                    {
                        "table_name": labels_tabel_name,
                        "block_name": self.EGRESS_BLOCK_NAME,
                    }
                )

        # 获取匹配项相关
        for key in paradict:
            if (
                key == "label_list"
                or (protocol == "ipv6" and key[0:4] == "ipv4")
                or (protocol == "ipv4" and key[0:4] == "ipv6")
            ):
                continue

            # 实际P4参数使用的key
            new_key = ""
            if (
                key == "ipv4_src"
                or key == "ipv4_dst"
                or key == "ipv6_src"
                or key == "ipv6_dst"
            ):
                new_key = self.para_to_key[key]
            elif key == "tp_src" or key == "tp_dst":
                new_key = self.para_to_key[ori_data["tp"] + "_" + key]
            else:
                new_key = self.para_to_key[protocol + "_" + key]

            # 对于空参数应该补充长度为0的匹配项
            if key not in ori_data.keys() or ori_data[key] == "":
                para_flep[new_key] = "0x0"
                para_flep[new_key + "_mask"] = "0x0"
                continue

            if (
                key == "ipv4_src"
                or key == "ipv4_dst"
                or key == "ipv6_src"
                or key == "ipv6_dst"
            ):
                # ipv4/ipv6地址
                # 通过'/'分割字符串
                ip_address, prefix_length_str = ori_data[key].split("/")
                # 将掩码部分从字符串转换为整数
                prefix_length = int(prefix_length_str)
                # ipv4/ipv6地址
                para_flep[new_key] = "ip('" + ip_address + "')"
                para_flep[new_key + "_mask"] = self.generate_mask(prefix_length)

            elif key == "tp":
                # tcp/udp
                if ori_data[key] == "tcp":
                    para_flep[new_key] = "0x06"
                    para_flep["udp_srcPort"] = "0x0"
                    para_flep["udp_srcPort_mask"] = "0x0"
                    para_flep["udp_dstPort"] = "0x0"
                    para_flep["udp_dstPort_mask"] = "0x0"
                elif ori_data[key] == "udp":
                    para_flep[new_key] = "0x11"
                    para_flep["tcp_srcPort"] = "0x0"
                    para_flep["tcp_srcPort_mask"] = "0x0"
                    para_flep["tcp_dstPort"] = "0x0"
                    para_flep["tcp_dstPort_mask"] = "0x0"
                para_flep[new_key + "_mask"] = "0xff"

            elif key == "tp_src" or key == "tp_dst":
                # 端口
                para_flep[new_key] = str(ori_data[key])
                para_flep[new_key + "_mask"] = "0xffff"
            else:
                # 其实也就是不存在else
                para_flep[new_key] = str(ori_data[key])

    def insert_forward_flep(self, protocol, ori_data):
        table_name = "flep_" + protocol + "_classifier"
        para_flep = {}
        para_labels_list = []
        # 构建匹配项部分
        self.convert_match_part_from_data(
            protocol, ori_data, para_flep, para_labels_list
        )
        label_list = ori_data["label_list"].rstrip(",").split(",")
        label_depth = len(label_list)

        # 构建para_flep标签栈部分
        para_flep.update(
            {
                "label_depth": str(label_depth),
            }
        )
        self.table.table_add(**para_flep)

        # 12345678 --> [5,6,7,8], [1,2,3,4]
        start_pos = label_depth
        for para_label in para_labels_list:
            end_pos = start_pos
            if int(para_label["remain_labels_count"]) > 5:
                temp_count = 5
            else:   
                temp_count = int(para_label["remain_labels_count"])
            start_pos -= temp_count

            for i, label in enumerate(label_list[start_pos:end_pos]):
                para_label["label{}".format(i+1)] = str(label)

            para_label["action"] = "flep_encap_{}_label".format(temp_count)
            # 写入P4
            self.table.table_add(**para_label)

        # print(table_name, para_labels_list)
        # print(table_name, para_flep)
        # ret = True
        ret = self.table.execute()
        if ret:
            self.db.add(table_name, ori_data)
        # print("insert_forward_flep success")
        return ret

    def initialize_flep_send(self, label, port):
        """
        Initializes the flep_processing table entry for forwarding.
        For Test

        :param table: An instance of the Table class.
        :param label: Label value.
        :param port: Port number for forwarding.
        """
        para = {
            "table_name": "flep_processing",
            "block_name": self.EGRESS_BLOCK_NAME,
            "action": "flep_send",
            "label": str(label),
            "port": str(port),
        }

        self.table.table_add(**para)
        ret = self.table.execute()

        data = {"label": label, "port": port}
        if ret:
            self.db.add(para["table_name"], data)

        print("initialize_flep_send success")

    def initialize_ip_send(self, protocal, data):
        para = {
            "table_name": protocal + "_lpm",
            "block_name": self.INGRESS_BLOCK_NAME,
            "action": "send",
            "port": str(data["port"]),
        }

        # 根据输入填充其他参数
        # 通过'/'分割字符串
        ip_address, prefix_length_str = data["ip"].split("/")
        # ipv4/ipv6地址
        para["dstAddr"] = "ip('" + ip_address + "')"
        para["dstAddr" + "_p_length"] = prefix_length_str
        para["port"] = str(data["port"])
        # print(para)
        self.table.table_add(**para)
        ret = self.table.execute()
        if ret:
            self.db.add(para["table_name"], data)
        print("initialize_ip_send success")
    def pre_init(self):
        """
        For Test
        """
        default_data = {
            "ipv4_src": "10.2.2.2/32",
            "ipv4_dst": "10.1.1.2/32",
            "tp": "tcp",
            "tp_src": "5001",
            "tp_dst": "5002",
            "label_list": "1",
        }
        
        
        self.insert_forward_flep(protocol="ipv4", ori_data=default_data)
        self.initialize_flep_send(label=1, port=1)
        self.initialize_flep_send(label=2, port=2)
        def_data = {
                "ip" : "10.2.2.2/32", 
                "port":"2"
        }
        self.initialize_ip_send("ipv4", def_data)

    def command_listener(command_queue, event):
        """
        For Test
        """
        try:
            while True:
                command = input("Enter command: ")
                command_queue.put(command)
                print("receive: {}".format(command))
                event.set()
                if command == "2":
                    break
            print("break")
            command_queue.task_done()
        except EOFError:
            print("Command listener exiting...")
        except KeyboardInterrupt:
            print("\nCommand listener interrupted.")

    def input_command(self, command):
        if command != "0" and command != "1" and command != "2":
            print("Command Error")
            return
        try:
            self.command_queue.put(command)
            print("receive: {}".format(command))
            self.event.set()
        except (EOFError, KeyboardInterrupt):
            print("Exiting...")

    def start(self):

        self.periodic_thread.start()

    def __del__(self):

        if self.periodic_thread.is_alive():
            self.periodic_thread.join()

    def shutdown(self):
        """Cleanly shut down the manager."""
        if self.periodic_thread.is_alive():

            manager.input_command("2")

            self.periodic_thread.join()


if __name__ == "__main__":
    DB_PORT = "3306"
    DB_NAME = "flep_encap"
    DB_USER = "root"
    DB_PASSWORD = "123456"

    manager = TOTPManager("flep_encap", DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    # manager = TOTPManager("flep_encap")
    manager.pre_init()
    manager.start()
    manager.input_command("0")

    manager.shutdown()
