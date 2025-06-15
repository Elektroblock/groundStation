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
        return f"E-G007 - Fehlercode {error_code} nicht gefunden."
    except FileNotFoundError:
        return "E-G008 - Fehlercode Datei nicht gefunden."
    except Exception as e:
        return f"E-G009 - Ein Fehler beim verarbeiten eines Fehlers ist aufgetreten: {e}"

def debugThread(message_queue, max_retries=10, retry_delay=5):
    session = requests.Session()
    while True:
        if message_queue.empty():
            time.sleep(0.1)
            continue

        webserver_queue_data = message_queue.get()

        # Wenn es ein Fehlercode ist, übersetze ihn
        # if webserver_queue_data[0] == "E" or webserver_queue_data[0] == "I" or webserver_queue_data[0] == "W":
        webserver_queue_data["error"] = get_error_message(webserver_queue_data["error"], "error_codes.txt")

        url = config.server_url + '/upload/error'
        headers = {
            'API-Key': config.api_key,
            'Content-Type': 'application/json',
            "Connection": "keep-alive"
        }

        payload = json.dumps(webserver_queue_data)

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[{attempt}/{max_retries}] Sende Fehlerdaten: {webserver_queue_data}")
                response = session.post(url, data=payload, headers=headers, timeout=5)

                if response.status_code == 200:
                    # Erfolgreich gesendet
                    break
                else:
                    print(f"[{attempt}/{max_retries}] Fehler beim Senden. Status: {response.status_code}, Antwort: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[{attempt}/{max_retries}] Ausnahme beim Senden von Fehlerdaten: {e}")

            time.sleep(retry_delay)
        else:
            print(f"❌ Fehlerdaten konnten nach {max_retries} Versuchen nicht gesendet werden: {webserver_queue_data}")
