import os
from http.server import SimpleHTTPRequestHandler


class MainHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.base_path = os.path.join(os.getcwd(), 'webservercontent')  # Ordner mit Bildern
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('webservercontent/index.html', 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode())
        elif self.path.startswith('/images'):
            file_path = os.path.join(self.base_path, self.path.lstrip('/'))
            print(file_path)
            if os.path.isfile(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "File not found")