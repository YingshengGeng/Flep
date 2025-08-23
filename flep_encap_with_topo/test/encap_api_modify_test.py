import requests
import json
import time

# Server details
SERVER_IP = "192.168.0.6"
SERVER_PORT = "11451"

# Define the base URL for the API
BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
print("Test:  Clear/Reset all tables and rules")
response = requests.post("{}/forward/reset".format(BASE_URL),json={})
response = requests.post("{}/label/clear".format(BASE_URL), json={})
response = requests.post("{}/verification/end".format(BASE_URL),json={})
response = requests.post("{}/rules/delete".format(BASE_URL),json={})

print("Test: add ipv4 label stack")
data1 = {
  "ipv4_src": "10.1.1.2/16",
  "ipv4_dst": "10.2.2.2/16",
  "tp": "tcp",
  "tp_src": "1145",
  "tp_dst": "2002",
  "label_list": "4, 6, 8, 12, 1, 2, 3, 4"
}

data2 = {
  "ipv4_src": "10.2.2.2/16",
  "ipv4_dst":  "10.1.1.2/16",
  "tp": "udp",
  "tp_src": "2930",
  "tp_dst": "3000",
  "label_list": "5, 7, 9, 11"
}

response = requests.post("{}/forward/ipv4/add".format(BASE_URL), json=data1)
print(response.text)
response = requests.post("{}/forward/ipv4/add".format(BASE_URL), json=data2)
print(response.text)
response = requests.post("{}/forward/inquire".format(BASE_URL), json={})
print(response.text)

print("Test: modify exists ipv4 label stack")
default_data = {
  "ipv4_src": "10.1.1.2/16",
  "ipv4_dst": "10.2.2.2/16",
  "tp": "tcp",
  "tp_src": "1145",
  "tp_dst": "2002",
  "label_list": "2839,28931,29301,20102"
}
response = requests.post("{}/forward/ipv4/modify".format(BASE_URL), json=default_data)
print(response.text)
response = requests.post("{}/forward/inquire".format(BASE_URL), json={})
print(response.text)


print("Test: modify not exists ipv4 label stack")
default_data = {
  "ipv4_src": "10.3.2.2/16",
  "ipv4_dst": "10.2.2.2/16",
  "tp": "tcp",
  "tp_src": "1145",
  "tp_dst": "2002",
  "label_list": "2839,28931,29301,20102"
}
response = requests.post("{}/forward/ipv4/modify".format(BASE_URL), json=default_data)
print(response.text)
response = requests.post("{}/forward/inquire".format(BASE_URL), json={})
print(response.text)

print("Test: modify multiply exists ipv4 label stack")
data3 = {
  "ipv4_src": "10.1.1.2/16",
  "ipv4_dst": "10.2.2.2/16",
  "tp": "udp",
  "tp_src": "2901",
  "tp_dst": "2002",
  "label_list": "2839,28931,29301,20102,4,6,8,12"
}
response = requests.post("{}/forward/ipv4/add".format(BASE_URL), json=data3)
default_data = {
  "ipv4_src": "10.1.1.2/16",
  "ipv4_dst": "10.2.2.2/16",
  "label_list": "109, 110, 111, 112"
}
response = requests.post("{}/forward/ipv4/modify".format(BASE_URL), json=default_data)
print(response.text)
response = requests.post("{}/forward/inquire".format(BASE_URL), json={})
print(response.text)



print("Test:  Add labels")
# Initialize flep_processing table entries for forwarding
for label, port in [("1","1"), ("2","2")]:
    data = {"label": label, "port": port}
    response = requests.post("{}/label/add".format(BASE_URL),json=data)
    print(response.text)

response = requests.post("{}/label/inquire".format(BASE_URL), json={})
print(response.text)

print("Test: modify labels")
default_data = {"label": 1, "port": 10}
response = requests.post("{}/label/modify".format(BASE_URL), json=default_data)
print(response.text)
response = requests.post("{}/label/inquire".format(BASE_URL),json={})
print(response.text)

print("Test: modify not exists labels")
default_data = {"label": 110, "port": 110}
response = requests.post("{}/label/modify".format(BASE_URL), json=default_data)
print(response.text)
response = requests.post("{}/label/inquire".format(BASE_URL),json={})
print(response.text)

# no multiple data
