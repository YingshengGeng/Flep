import requests
import json
import time

# Server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = "11451"
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

print("Test:  inquire labels")
response = requests.post("{}/label/inquire".format(BASE_URL),json={"label": "1"})
print(response.text)
response = requests.post("{}/label/inquire".format(BASE_URL),json={"label": "2"})
print(response.text)
response = requests.post("{}/label/inquire".format(BASE_URL),json={})
print(response.text)

print("Test:  delete labels")
response = requests.post("{}/label/delete".format(BASE_URL),json={"label": 1, "port": 1})
print(response.text)


print("Test:  start verification")
response = requests.post("{}/verification/start".format(BASE_URL),json={})
print(response.text)
# print("----------st------------")
# print("Test:  compute 30s")
# time.sleep(61)
# print("----------end------------")

# print("Test:  add rule 60s")
# default_data = {"period": "2"}
# response = requests.post("{}/rules/configure".format(BASE_URL),json=default_data)
# print(response.text)

# print("Test:  inquire rule 60s")
# response = requests.post("{}/rules/inquire".format(BASE_URL),json={})
# print(response.text)

# print("Test:  compute 60s")
# time.sleep(61)

# print("Test:  delete rule 60s")
# response = requests.post("{}/rules/delete".format(BASE_URL),json={})
# print(response.text)


print("Test:  end verification")
response = requests.post("{}/verification/end".format(BASE_URL),json={})
print(response.text)
