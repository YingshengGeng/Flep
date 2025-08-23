import requests
import json
import time

# Server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = "11451"
BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
print("Test:  Clear/Reset all tables and rules")
response = requests.post("{}/forward/reset".format(BASE_URL),json={})
response = requests.post("{}/label/clear".format(BASE_URL), json={})
response = requests.post("{}/verification/end".format(BASE_URL),json={})
response = requests.post("{}/rules/delete".format(BASE_URL),json={})


print("Test: add ipv4 label stack")
default_data = {
  "ipv4_src": "10.1.1.2/16",
  "ipv4_dst": "10.2.2.2/16",
  "tp": "tcp",
  "tp_src": "1145",
  "tp_dst": "2002",
  "label_list": "4, 6, 8, 12, 1, 2, 3, 4"
}
response = requests.post("{}/forward/ipv4/add".format(BASE_URL), json=default_data)
print(response.text)

print("Test:  Add labels")
# Initialize flep_processing table entries for forwarding
for label, port in [("1","1"), ("2","2")]:
    data = {"label": label, "port": port}
    response = requests.post("{}/label/add".format(BASE_URL),json=data)
    print(response.text)

