from http.server import BaseHTTPRequestHandler, HTTPServer


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        msg = input("❯ ")
        self.wfile.write(msg.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        print(post_data)
        self.send_response_only(200, b"recieved")
        self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    PORT = 8888
    print('Starting Listener...')
    httpd = HTTPServer(('', PORT), HTTPHandler)
    print(f'listener initiated on port {PORT}')
    httpd.serve_forever()
