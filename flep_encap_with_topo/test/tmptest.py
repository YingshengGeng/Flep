import requests
import json
import time

# Server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = "11451"
BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
print("Test: inquire all label")
default_data = {
}
response = requests.post("{}/label/inquire".format(BASE_URL), json=default_data)
print(response.text)
response = requests.post("{}/label/clear".format(BASE_URL), json=default_data)
print(response.text)