from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE
from threading import Thread


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'hello world')

    def log_message(self, format, *args):
        with open("server_logs.log", "a") as slogs:
            slogs.write(f"{self.client_address} {self.path}\n")


def start_ngrok_forwarding():
    Popen(
        "ngrok http --url=allegedly-great-shiner.ngrok-free.app 8001",
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )


def start_executor_server():
    with open("server_logs.log", "w") as slogs:
        slogs.write("starting ngrok daemon...\n")
        Thread(target=start_ngrok_forwarding, args=[], daemon=True).start()
        slogs.write("ngrok daemon started!\n")
        httpd = HTTPServer(('', 8001), HTTPHandler)
        slogs.write("httpd server bind to port 8001\n")
    httpd.serve_forever()
