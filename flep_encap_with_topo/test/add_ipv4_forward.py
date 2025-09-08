import requests
import json
import time

# Server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = "11451"
BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
print("ADD IPV$")
default_data = {
    "ip":"10.3.3.3/16",
    "port":"2"
}
response = requests.post("{}/neighbor/ipv4/add".format(BASE_URL), json=default_data)
print(response.text)