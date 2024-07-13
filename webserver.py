import json
from os import walk
from http.server import HTTPServer
from handlers import MainHandler
import os

from simple_websocket_server import WebSocketServer, WebSocket
from threading import Thread


def run_http_server(server_class=HTTPServer, handler_class=MainHandler, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()


def run_webserver(receiver_queue, webserver_queue):
    class GraphSocket(WebSocket):
        def handle(self):
            filenames = next(walk("webservercontent/images"), (None, None, []))[2]
            self.send_message(json.dumps({"allImages": filenames}))

        def connected(self):
            print(self.address, 'connected')
            clients.append(self)

            with open("data.json", 'r') as file:
                json_data = json.load(file)

            filenames = next(walk("webservercontent/images"), (None, None, []))[2]
            self.send_message(json.dumps(json_data))
            self.send_message(json.dumps({"image": filenames[len(filenames) - 1]}))

        def handle_close(self):
            clients.remove(self)
            print(self.address, 'closed')

    clients = []

    def start_websocket_server():
        server = WebSocketServer('', 8005, GraphSocket)
        server.serve_forever()

    # starting websocket and http Server

    websocket_thread = Thread(target=start_websocket_server)
    websocket_thread.daemon = True
    websocket_thread.start()

    html_thread = Thread(target=run_http_server)
    html_thread.daemon = True
    html_thread.start()

    while True:
        if webserver_queue.empty():
            continue

        webserver_queue_data = webserver_queue.get()
        print(webserver_queue_data)
        for client in clients:
            client.send_message(json.dumps(webserver_queue_data))
