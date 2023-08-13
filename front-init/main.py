from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import urllib.parse
import mimetypes
import pathlib
import socket
import threading
import json

json_data = {}

class MainServer(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
                self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        client(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def client(message):
        host = socket.gethostname()
        port = 5000
        server = host, port

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(message, server)

        client_socket.close()


def server():
    host = socket.gethostname()
    port = 5000
    server = host, port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server)
    
    while True:
        data = server_socket.recvfrom(1024)
        if not data:
            break

        data_parse = urllib.parse.unquote_plus(data.decode())
        data_parse = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

        with open(pathlib.Path().joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json_data.update({str(datetime.now()): data_parse})
            json.dump(json_data, fd, ensure_ascii=False)

    server_socket.close()


def run(server_class=HTTPServer, handler_class=MainServer):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        sockert_server = threading.Thread(target=server)
        http_server = threading.Thread(target=http.serve_forever)
        sockert_server.start()
        http_server.start()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()