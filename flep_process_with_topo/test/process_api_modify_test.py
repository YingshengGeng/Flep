import requests
import json
import time

# Server details
SERVER_IP = "192.168.0.6"
SERVER_PORT = "11452"
# Define the base URL for the API
BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
print("Test:  Clear all tables and rules")
response = requests.post("{}/label/clear".format(BASE_URL), json={})
response = requests.post("{}/verification/end".format(BASE_URL),json={})
response = requests.post("{}/rules/delete".format(BASE_URL),json={})

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
