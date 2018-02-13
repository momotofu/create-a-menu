from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Hello!</body></html>"
                self.wfile.write(output)
                print(output)
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        server.serve_forever()
        print("Web server running on port %s" % port)

    except KeyboardInterrupt:
        # A python defined exception when the user
        # presses control-C on their keyboard
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
