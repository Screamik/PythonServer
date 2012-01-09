import server
import sys

class ExtendedRequestHandler(server.ThreadedTCPRequestHandler):
    def get_port(self, match_obj):
        self.wfile.write(str(self.server.getServerPort()).encode())


if __name__ == "__main__":
    try:
        HOST, PORT = sys.argv[1], int(sys.argv[2])
    except:
        HOST, PORT = "127.0.0.1", 1298
    srv = server.SimpleThreadedTCPServer((HOST, PORT), ExtendedRequestHandler)
    srv.serve_forever()
