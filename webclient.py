import json
import time

import requests


from config import api_key, server_url



def run_webserver_client(webserver_queue):
    session = requests.Session()
    while True:
        if webserver_queue.empty():
            time.sleep(0.1)
            continue

        webserver_queue_data = webserver_queue.get()
        if "image" in webserver_queue_data:
            upload_file(api_key, "images/"+webserver_queue_data["image"], session)
        else:
            send_text(api_key, json.dumps(webserver_queue_data) ,session)



def upload_file(api_key, file_path, session):
    url = server_url + '/upload/image'
    files = {'file': open(file_path, 'rb')}
    headers = {
        'API-Key': api_key,
        "Connection": "keep-alive"
    }
    response = session.post(url, files=files, headers=headers)
    if response.status_code == 201:
        print("File uploaded successfully")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}, Response: {response.text}")

def send_text(api_key, text_data, session):
    url = server_url + '/upload/data'
    headers = {
        'API-Key': api_key,
        'Content-Type': 'application/x-www-form-urlencoded',
        "Connection": "keep-alive"
    }
    response = session.post(url, data=text_data, headers=headers)
    if response.status_code == 201:
        print("Text data sent successfully")
    else:
        print(f"Failed to send text data. Status code: {response.status_code}, Response: {response.text}")