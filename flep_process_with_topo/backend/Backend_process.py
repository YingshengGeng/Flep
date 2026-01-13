import os, sys, yaml
import json
from flask import *
from ipaddress import *
from tableAPI_new import Table
from dbAPI_new import DB
from totp_process import TOTPManager
import subprocess
import argparse
import logging
from flask_cors import CORS

FILE_INTERVAL = "\\" if os.name == "nt" else "/"
FILE_PATH = sys.path[0] + FILE_INTERVAL
CONFIG_PATH = os.path.dirname(sys.path[0]) + FILE_INTERVAL + "config.py"

f = open(FILE_PATH + "configuration.yml", "r", encoding="utf-8")
content = f.read()
parameter = yaml.full_load(content)
f.close()
p4_file_name = parameter["P4_NAME"]
DB_PORT = parameter["DB_PORT"]
DB_NAME = parameter["DB_NAME"]
DB_USER = parameter["DB_USER"]
DB_PASSWORD = parameter["DB_PASSWORD"]

SDE_INSTALL = parameter["SDE_INSTALL"]

P4_NAME = parameter["P4_NAME"]
python_version = parameter['PYTHON_VERSION']

parser = argparse.ArgumentParser(
    description="Apply switch configuration based on command line argument."
)
parser.add_argument(
    "switch_index", help="The index of the switch to apply configuration for."
)
args = parser.parse_args()

SERVER_IP = parameter["SOUTHBOUND_SERVER_IP" + "_" + str(args.switch_index)]
SERVER_PORT = parameter["SOUTHBOUND_SERVER_PORT"]

PORT_LIST_INDEX = parameter["PORT_LIST" + "_" + str(args.switch_index)]
PORT_LIST_FOR_MC = list(PORT_LIST_INDEX.keys())
REVERSE_PORT_LIST_INDEX = {str(v): str(k) for k, v in PORT_LIST_INDEX.items()}
LOCAL_LABEL = parameter["LOCAL_LABEL" + "_" + str(args.switch_index)]

manager = TOTPManager("flep_process", DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
manager.start()

app = Flask(__name__)
CORS(app)


def _response(ret):
    if ret == True:
        response = make_response("Succeed", 200)
    elif ret == -1:
        response = make_response("Already Exists", 409)
    else:
        response = make_response("Failed", 400)
    return response


@app.route("/forward/port/<operation>", methods=["POST"])
def handle_port(operation):
    global manager
    table_name = "fwd_port"
    data = request.get_json()
    # not db
    table = Table(p4_file_name=p4_file_name)

    if operation == "inquire":
        pass
    elif operation == "clear":
        temp = {"table_name": table_name, "block_name": "Ingress"}
        table.table_clear(**temp)
        ret = table.execute()
    else:
        para = {"table_name": table_name, "block_name": "Ingress"}
        para["action"] = "send"
        # 将掩码部分从字符串转换为整数
        # ipv4/ipv6地址
        para["ingress_port"] = REVERSE_PORT_LIST_INDEX[str(data["ingress_port"])]
        para["port"] = REVERSE_PORT_LIST_INDEX[str(data["port"])]
        
        ret = False
        if operation == "add":
            table.table_add(**para)
            ret = table.execute()
        elif operation == "delete":
            try:
                para.pop("action")
                para.pop("port")
            except:
                pass
            table.table_delete(**para)
            ret = table.execute()
        else:
            del table
            response = make_response("Failed", 404)
            return response
    
    del table
    return _response(ret)

@app.route("/label/<operation>", methods=["POST"])
def handle_label_rule(operation):
    parakey = {"label", "port"}
    table_name = "flep_processing"
    data = request.get_json(force=True, silent=True)
    db = DB(DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    if operation == "inquire":
        # 用于查询, 直接从数据库读
        results = db.query(table_name, data)
        del db
        r = json.dumps(results)
        response = make_response(r)
        response.headers["Content-Type"] = "application/json"
        return response

    para = {}
    para["table_name"] = table_name
    # Mark
    para["block_name"] = "Ingress"
    para["action"] = "flep_send"
    
    # 根据输入填充其他参数
    if data != None:
        for key in parakey:
            if key not in data.keys():
                continue
            para[key] = str(data[key])
    if "port" in para.keys():
        para["port"] = REVERSE_PORT_LIST_INDEX[para["port"]] # str, str
    table = Table(p4_file_name=p4_file_name)
    ret = False
    if operation == "add":
        table.table_add(**para)
        ret = table.execute()
        if ret:
            db.add(table_name, data)
    elif operation == "delete":
        try:
            para.pop("action")
            para.pop("port")
        except:
            pass
        table.table_delete(**para)
        ret = table.execute()
        if ret:
            db.delete(table_name, data)

    elif operation == "clear":
        temp = {"table_name": table_name, "block_name": "Ingress"}
        table.table_clear(**temp)
        ret = table.execute()
        if ret:
            db.clear(table_name)
    elif operation == "modify":
        temp_port = None
        if "port" in data.keys():
            temp_port = data["port"]
        try:
            data.pop("port")
        except:
            pass
        # pop in other place
        # 1. check if the rule exists from db
        results = db.query(table_name, data)
        # 1.1 if not exists, return 404
        if len(results) == 0:
            response = make_response("Do not exists this item", 404)
        # 1.2 if more than one, return 409
        # MARK: here will never happen, because the label is unique
        elif len(results) > 1:
            response = make_response("More than one item", 409)
        else:  
            # 2. if exists, delete the rule
            previous_data = results[0]
            try:
                para.pop("action")
                para.pop("port")
            except:
                pass
            table.table_delete(**para)
            ret = table.execute()
            if ret:
                db.delete(table_name, data)
            else:
                # if delete failed, return 400
                return make_response("Failed to delete item", 400)

            # 4. modify the corresponding data
            # 4.1 if port exists, reconstruct it
            if temp_port is not None:
                data["port"] = temp_port

            for key in data.keys():
                if key in previous_data.keys():
                    previous_data[key] = data[key]
            
            # 5. add the new rule
            para["action"] = "flep_send"
            para["label"] = str(previous_data["label"])
            para["port"] = REVERSE_PORT_LIST_INDEX[str(previous_data["port"])]
            table.table_add(**para)
            ret = table.execute()
            if ret:
                db.add(table_name, data)
            response = _response(ret)
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        del table
        response = make_response("Failed", 404)
        return response
    del table
    return _response(ret)



@app.route("/verification/<operation>", methods=["POST"])
def handle_verification(operation):
    global manager

    if operation == "start":
        manager.input_command("1")
    elif operation == "end":
        manager.input_command("0")
    else:
        response = make_response("Failed", 404)
        return response
    return _response(True)


@app.route("/rules/<operation>", methods=["POST"])
def handle_rules(operation):
    global manager
    data = request.get_json()
    ret = False
    if operation == "inquire":
        results = manager.manage_period("get")
        r = json.dumps({"period": results})
        response = make_response(r)
        response.headers["Content-Type"] = "application/json"
        return response

    if operation == "configure":
        manager.manage_period("update", int(data["period"]))
        ret = True

    elif operation == "delete":
        manager.manage_period("delete")
        ret = True
    else:
        response = make_response("Failed", 404)
        return response
    return _response(ret)


@app.route("/topology", methods=["GET"])
def get_adjacency():
    script_path = FILE_PATH + "typo_compute.py"

    process = subprocess.Popen(
        ["python3", script_path, SDE_INSTALL, p4_file_name, LOCAL_LABEL, python_version],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception("Error calling Python 3 script: {}".format(stderr.decode()))

    # MARK 
    raw_data = stdout.decode()
    valid_json = raw_data.replace("'", '"')
    json_data = json.loads(valid_json)
    response = make_response(json.dumps(json_data))
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/pkt_gen/<operation>", methods=["POST"])
def pkt_gen_manager(operation):
    script_path = FILE_PATH + "_set_pkt_gen.py"
    print(script_path)
    if operation == "start":
         process = subprocess.Popen(
        ["python3", script_path, "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    elif operation == "stop":
         process = subprocess.Popen(
        ["python3", script_path, "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())
    response = make_response("Success", 200)
    if process.returncode != 0:
       response = make_response("Failed", 404)
       
    response.headers["Content-Type"] = "application/json"
    return response

def clear_database_and_tables():
    """Clear database and tables before starting the Flask app."""
    print("Clearing database and tables...")
    # Connect to the database
    db = DB(DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

    # Clear each table
    tables_to_clear = ["flep_processing", "key_match_tbl"]
    for table_name in tables_to_clear:
        db.clear(table_name)

    # Close the database connection
    del db

    # Clear the P4 tables
    table = Table(p4_file_name=p4_file_name)
    for table_name in ["flep_processing", "key_match_tbl"]:
        temp = {"table_name": table_name, "block_name": "Ingress"}
        table.table_clear(**temp)
        table.execute()
    del table

    print("Database and tables cleared.")



def pre_initialization():
    """
    This function is used to pre-initialization the table.
    """
    script_path = FILE_PATH + "_initialization.py"

    process = subprocess.Popen(
        ["python3", script_path, args.switch_index],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception("Error calling Python 2 script: {}".format(stderr.decode()))
    print("Pre init finished")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def sync_time():
    try:
        # 构建脚本路径
        script_path = os.path.join(FILE_PATH, "../tools/sync_time.sh")
        
        # 运行脚本
        with subprocess.Popen(["sudo", "bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            stdout, stderr = process.communicate()
            process.wait()
            if process.returncode == 0:
                logging.info("Time synchronized successfully.")
            else:
                logging.error("Error synchronizing time: {}".format(stderr.strip()))
    except Exception as e:
        logging.error("Error synchronizing time: {}".format(e))
        
if __name__ == "__main__":

    clear_database_and_tables()
    pre_initialization()
    # 设置同步时间的频率（例如，每 60 分钟同步一次）
    # sync_time()
    
    app.run(host=SERVER_IP, port=int(SERVER_PORT), debug=False)
