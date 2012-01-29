import socketserver
import time
import substitutor
import re
import threading
from configparser import ConfigParser

class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):
    def loadMethods(self=None):
        exprs = {}
        parser = ConfigParser()
        parser.read('config.txt')
        for method, expr in parser['regular_expr'].items():
            exprs[method] = re.compile(expr)
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
        self.wfile.write('VALUE\n'.encode())
        try:
            self.wfile.write(sbst.get(match_obj.group(1), None).encode())
        except substitutor.InfiniteRecursionException:
            self.wfile.write('ERROR: Infinite recursion'.encode())

    def put_method(self, match_obj):
        sbst = substitutor.Substitutor()
        rlock = threading.RLock()
        time.sleep(sbst.getSleepTime())
        with rlock:
            sbst.put(match_obj.group(1), match_obj.group(2))
        self.wfile.write('OK'.encode())

    def set_sleep_method(self, match_obj):
        sbst = substitutor.Substitutor()
        rlock = threading.RLock()
        with rlock:
            sbst.setSleepTime(int(match_obj.group(1)))
        self.wfile.write('OK'.encode())


class SimpleThreadedTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, requestHandlerClass):
        parser = ConfigParser()
        parser.read('config.txt')
        server_address = (parser['server_config']['HOST'], parser['server_config'].getint('PORT'))
        super().__init__(server_address, requestHandlerClass)
        self.port = server_address[1]

    def getServerPort(self):
        return self.port

if __name__ == "__main__":
    server = SimpleThreadedTCPServer(ThreadedTCPRequestHandler)
    server.serve_forever()


