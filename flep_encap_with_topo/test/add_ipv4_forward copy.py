import requests
import json
import time

# Server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = "11451"
BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
print("ADD Port")
default_data = {
    "ingress_port":
    "port":
}
response = requests.get("{}/forward/port/add".format(BASE_URL), json=default_data)
print(response.text)