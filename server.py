import socketserver
import sys
import time
import substitutor
import threading

dict = {}
sleepTime = 0
rlock = threading.RLock()


class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global dict, sleepTime, rlock
        self.data = self.rfile.readline().strip()
        req = (self.data.decode()).split(' ', 2)
        length = len(req)
        if req[0] == 'GET':
            time.sleep(sleepTime)
            if length >= 2:
                self.wfile.write(('VALUE\n'+substitutor.get(dict, req[1])).encode())
            else:
                self.wfile.write('GET syntax: GET key'.encode())
        elif req[0] == 'SET' and req[1] == 'SLEEP':
            if length == 3:
                rlock.acquire()
                sleepTime = int(req[2])
                rlock.release()
                self.wfile.write('OK'.encode())
            else:
                self.wfile.write('SET syntax: SET SLEEP sleeptime')
        elif req[0] == 'PUT':
            time.sleep(sleepTime)
            if length == 3:
                rlock.acquire()
                substitutor.put(dict, req[1], req[2])
                rlock.release()
                self.wfile.write('OK'.encode())
            else:
                self.wfile.write('PUT syntax: PUT key value'.encode()
)
        else:
            self.wfile.write('Unsupported request! We accept GET, PUT or SET SLEEP here!'.encode()
)


if __name__ == "__main__":
    try:
        HOST, PORT = sys.argv[1:]
    except:
        HOST, PORT = "127.0.0.1", 1298
    server = socketserver.ThreadingTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.serve_forever()


