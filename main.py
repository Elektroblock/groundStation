import time
from queue import Queue
from threading import Thread
from receiver import wait_for_data
from webclient import run_webserver_client
from config import DEBUG, use_webclient
import json
import os
import glob


def run():
    if (DEBUG):
        with open("data.json", 'w') as file:
            json.dump({"data": []}, file, indent=4)

        print("cleared data.json")

        files = glob.glob('images/*')
        cleared_files = 0
        for f in files:
            if f.endswith('.jpg'):
                os.remove(f)
                cleared_files += 1
        print(f"cleared {cleared_files} Images")
        time.sleep(2)

    webserver_queue = Queue()

    receiver_thread = Thread(target=wait_for_data, args=(webserver_queue,))
    webclient_thread = Thread(target=run_webserver_client, args=(webserver_queue,))
    receiver_thread.daemon = False
    webclient_thread.daemon = False

    receiver_thread.start()

    if use_webclient:
        webclient_thread.start()

    while True:
        time.sleep(100)


if __name__ == '__main__':
    run()
