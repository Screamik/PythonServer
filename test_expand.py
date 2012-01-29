import server

class ExtendedRequestHandler(server.ThreadedTCPRequestHandler):
    def get_port(self, match_obj):
        self.wfile.write(str(self.server.getServerPort()).encode())


if __name__ == "__main__":
    srv = server.SimpleThreadedTCPServer(ExtendedRequestHandler)
    srv.serve_forever()
