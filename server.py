import socketserver
import sys
import time
import substitutor
import re
import threading


class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):
    def loadMethods(self=None):
        exprs = {}
        with open('regular_expr.txt', encoding='utf-8')as expr_file:
            for line in expr_file:
                key, val = line.split()
                exprs[val] = re.compile(key)
        return exprs

    methods = loadMethods()

    def handle(self):
        req = self.rfile.readline().strip().decode()
        for func in self.methods:
            match_obj = self.methods[func].match(req)
            if match_obj:
                try:
                    getattr(self, func)(match_obj)
                except AttributeError:
                    self.wfile.write('Ooops, internal server error - method name not correct.'.encode())
                return
        self.wfile.write('Method not supported.'.encode())

    def get_method(self, match_obj):
        sbst = substitutor.Substitutor()
        time.sleep(sbst.getSleepTime())
        self.wfile.write(('VALUE\n'+sbst.get(match_obj.group(1), None)).encode())

    def put_method(self, match_obj):
        sbst = substitutor.Substitutor()
        rlock = threading.RLock()
        time.sleep(sbst.getSleepTime())
        rlock.acquire()
        sbst.put(match_obj.group(1), match_obj.group(2))
        rlock.release()
        self.wfile.write('OK'.encode())

    def set_sleep_method(self, match_obj):
        sbst = substitutor.Substitutor()
        rlock = threading.RLock()
        rlock.acquire()
        sbst.setSleepTime(int(match_obj.group(1)))
        rlock.release()
        self.wfile.write('OK'.encode())


class SimpleThreadedTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, requestHandlerClass):
        super().__init__(server_address, requestHandlerClass)
        self.port = server_address[1]

    def getServerPort(self):
        return self.port

if __name__ == "__main__":
    try:
        HOST, PORT = sys.argv[1], int(sys.argv[2])
    except:
        HOST, PORT = "127.0.0.1", 1298
    server = SimpleThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.serve_forever()


