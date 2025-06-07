from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE
from multiprocessing.connection import Client
from time import sleep


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        conn.send(self.headers['X-Forwarded-For'])
        msg = conn.recv()
        self.wfile.write(msg)

    def log_message(self, format, *args):
        try:
            conn.send(f"[ LOG ] {self.requestline}")
            conn.recv()
        except Exception as e:
            print(e)


def start_ngrok_forwarding():
    Popen(
        "ngrok http --url=allegedly-great-shiner.ngrok-free.app 8001",
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )


def start_executor_server():
    global conn
    addr = ('localhost', 36250)
    sleep(1)
    conn = Client(addr, authkey=b'intcomm')
    httpd = HTTPServer(('', 8001), HTTPHandler)
    try:
        httpd.serve_forever()
    finally:
        conn.close()
