import os
import signal
import subprocess
import requests
import time
import os, sys, yaml
import argparse

FILE_INTERVAL = "\\" if os.name == "nt" else "/"
FILE_PATH = sys.path[0] + FILE_INTERVAL
CONFIG_PATH = sys.path[0] + FILE_INTERVAL + "config.py"

f = open(FILE_PATH + "configuration.yml", "r", encoding="utf-8")
content = f.read()
parameter = yaml.full_load(content)
f.close()
p4_file_name = parameter["P4_NAME"]
DB_PORT = parameter["DB_PORT"]
DB_NAME = parameter["DB_NAME"]
DB_USER = parameter["DB_USER"]
DB_PASSWORD = parameter["DB_PASSWORD"]

parser = argparse.ArgumentParser(description="Apply switch configuration based on command line argument.")
parser.add_argument("switch_index", help="The index of the switch to apply configuration for.")
args = parser.parse_args()
SERVER_PORT = parameter["SOUTHBOUND_SERVER_PORT"]

def kill_process_on_port(port):
    """find and kill"""
    try:
        output = subprocess.check_output(["lsof", "-i", ":{}".format(port)])
        lines = output.decode().split('\n')
        for line in lines[1:]:
            if line:
                pid = int(line.split()[1])
                os.kill(pid, signal.SIGTERM)
                print("Killed process with PID {} on port {}".format(pid,port))
    except subprocess.CalledProcessError:
        print("No process found using port {}".format(port))

def start_backend_process():
    """start Backend_process.py """
    backend_process = subprocess.Popen(["python3", FILE_PATH + "Backend_encap.py", args.switch_index]) 
    return backend_process

if __name__ == "__main__":

    kill_process_on_port(SERVER_PORT)

    time.sleep(5)
    
    backend_process = start_backend_process()
    
    time.sleep(10)


