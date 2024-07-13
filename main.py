from queue import Queue
from threading import Thread
from receiver import wait_for_data
from webserver import run_webserver

receiver_queue = Queue()
webserver_queue = Queue()

receiver_thread = Thread(target=wait_for_data, args=(receiver_queue, webserver_queue,))
webserver_thread = Thread(target=run_webserver, args=(receiver_queue, webserver_queue,))
receiver_thread.daemon = False
webserver_thread.daemon = False

receiver_thread.start()
webserver_thread.start()

while True:
    pass
