import socket
import time

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
    while True:
        if message_queue.empty():
            time.sleep(0.1)
            continue
        webserver_queue_data = message_queue.get()
        if webserver_queue_data[0] == "E":
            webserver_queue_data = get_error_message(webserver_queue_data, "error_codes.txt")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((config.debug_server_host, config.debug_server_port))
                client_socket.sendall(webserver_queue_data.encode())  # Daten senden
                print("Daten gesendet.")
        except:
            print("Fehler beim senden zu Debug Server")