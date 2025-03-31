from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE
from threading import Thread


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'hello world')

    def log_message(self, format, *args):
        pass


def start_ngrok_forwarding():
    Popen(
        "ngrok http --url=allegedly-great-shiner.ngrok-free.app 8001",
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )


def start_executor_server():
    Thread(target=start_ngrok_forwarding, args=[], daemon=True).start()
    print("binding server")
    httpd = HTTPServer(('', 8001), HTTPHandler)
    print("starting server")
    httpd.serve_forever()
