import json
import socket
import time
from time import sleep

import requests

import config


# Client-Socket erstellen

def get_error_message(error_code, filepath): # Danke Chat GPT für die Funktion
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    code, message = line.split(" - ", 1)
                    if code == error_code:
                        return error_code + " - " + message
        return "Fehlercode nicht gefunden."
    except FileNotFoundError:
        return "Datei nicht gefunden."
    except Exception as e:
        return f"Ein Fehler ist aufgetreten: {e}"

def debugThread(message_queue):
    session = requests.Session()
    while True:
        if message_queue.empty():
            time.sleep(0.1)
            continue
        webserver_queue_data = message_queue.get()
        if webserver_queue_data[0] == "E":
            webserver_queue_data = get_error_message(webserver_queue_data, "error_codes.txt")
        try:
            url = config.server_url + '/upload/error'
            headers = {
                'API-Key': config.api_key,
                'Content-Type': 'application/json',
                "Connection": "keep-alive"
            }
            print(webserver_queue_data)
            response = session.post(url, json.dumps({"error": webserver_queue_data}), headers=headers)
            if response.status_code == 200:
                #print("Text data sent successfully")
                sleep(0)
            else:
                print(f"Failed to send error data. Status code: {response.status_code}, Response: {response.text}")
        except:
            print("Fehler beim senden zu Debug Server")