import json
import time
from time import sleep

import requests


from config import api_key, server_url



def run_webserver_client(webserver_queue, mess):
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



def upload_file(api_key, file_path, session, max_retries=15, retry_delay=5):
    url = server_url + '/upload/image'
    headers = {
        'API-Key': api_key,
        "Connection": "keep-alive"
    }

    for attempt in range(max_retries):
        try:
            with open(file_path, 'rb') as file_data:
                files = {'file': file_data}
                response = session.post(url, files=files, headers=headers, timeout=5)

            if response.status_code == 200:
                return True
            else:
                print(f"[{attempt+1}/{max_retries}] Fehler beim Hochladen: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[{attempt+1}/{max_retries}] Fehler beim Hochladen: {e}")

        time.sleep(retry_delay)

    print(f"❌ Konnte Datei nach {max_retries} Versuchen nicht hochladen.")
    return False

def send_text(api_key, text_data, session, max_retries=15, retry_delay=5):
    url = server_url + '/upload/data'
    headers = {
        'API-Key': api_key,
        'Content-Type': 'application/json',
        "Connection": "keep-alive"
    }

    for attempt in range(max_retries):
        try:
            response = session.post(url, data=text_data, headers=headers, timeout=5)
            if response.status_code == 200:
                # Erfolgreich gesendet
                return True
            else:
                print(f"[{attempt+1}/{max_retries}] Server error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[{attempt+1}/{max_retries}] Fehler beim Senden: {e}")

        time.sleep(retry_delay)

    print(f"❌ Konnte Textdaten nach {max_retries} Versuchen nicht senden.")
    return False
