import requests
import json
import time

# Server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = "11451"
BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
print("Test:  Add labels")
# Initialize flep_processing table entries for forwarding
for label, port in [("0x2502","2"), ("0x2503","3")]:
    data = {"label": label, "port": port}
    response = requests.post("{}/label/add".format(BASE_URL),json=data)
    print(response.text)