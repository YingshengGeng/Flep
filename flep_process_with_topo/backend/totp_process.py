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
        self.KEY_MATCH_TABLE_NAME = "key_match_tbl"
        self.INSERT_KEY_TABLE_NAME = "insert_key_tbl"
        self.IS_VERIFY_TABLE_NAME = "is_verify_tbl"

        self.periodic_thread = threading.Thread(
            target=self.periodic_function, args=(self.command_queue, self.event)
        )

        self.periodic_thread.daemon = False

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
        para["block_name"] = self.INGRESS_BLOCK_NAME
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
            "block_name": self.INGRESS_BLOCK_NAME,
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
            "block_name": self.INGRESS_BLOCK_NAME,
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
        para["block_name"] = self.INGRESS_BLOCK_NAME

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
            "block_name": self.INGRESS_BLOCK_NAME,
        }

        # First time we needn't delete any key (counter <= 1)
        if self.counter <= 1:
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
            "block_name": self.INGRESS_BLOCK_NAME,
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
            "block_name": self.INGRESS_BLOCK_NAME,
        }

        self.table.table_clear(**para)
        ret = self.table.execute()
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
                    verification_entry_added = False
                    self.counter = 0
                event.clear()  # 清除事件，以便下一次检查
                event.wait()

    def generate_mask(self, prefix_length):
        mask = (1 << prefix_length) - 1
        mask = mask << (32 - prefix_length)
        hex_mask = hex(mask)
        return hex_mask

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
            "block_name": self.INGRESS_BLOCK_NAME,
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

    def pre_init(self):
        """
        For Test
        """

        self.initialize_flep_send(label=1, port=1)
        self.initialize_flep_send(label=2, port=2)

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
    manager = TOTPManager(p4_file_name="flep_process")
    manager.pre_init()
    manager.start()
    manager.input_command("0")

    manager.shutdown()
