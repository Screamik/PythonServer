import socket
import threading
import unittest
import substitutor
import server

class TestSubstitutor(unittest.TestCase):
    def test_replacement(self):
        sbst = substitutor.Substitutor()
        sbst.put("k1", "one")
        sbst.put("k2", "two")
        sbst.put("keys", "1: ${k1}, 2: ${k2}")
        self.assertEquals("1: one, 2: two", sbst.get("keys"))

    def test_emptyReplacement(self):
        sbst = substitutor.Substitutor()
        sbst.put("k", "bla-${inexistent}-bla")
        self.assertEquals("bla--bla", sbst.get("k"))


class TestServer(unittest.TestCase):
    HOST, PORT = "127.0.0.1", 1298

    @classmethod
    def setUpClass(cls):
        cls.server = server.SimpleThreadedTCPServer((cls.HOST, cls.PORT), server.ThreadedTCPRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server_thread._stop()

    def test_getPut(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT k1 one\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("GET k1\n".encode())
        self.assertEquals("VALUE\n", sock.recv(1024).decode())
        self.assertEquals("one", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT keys ${k1} ${k2}\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("GET keys\n".encode())
        self.assertEquals("VALUE\n", sock.recv(1024).decode())
        self.assertEquals("one ", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT k2 two\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("GET keys\n".encode())
        self.assertEquals("VALUE\n", sock.recv(1024).decode())
        self.assertEquals("one two", sock.recv(1024).decode())
        sock.close()

    def test_recursiveGet(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT keys2 ${k5} ${k2}\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT k4 two\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT k5 k1 ${k4}\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("GET keys2\n".encode())
        self.assertEquals("VALUE\n", sock.recv(1024).decode())
        self.assertEquals("k1 two two", sock.recv(1024).decode())
        sock.close()

    def test_recursionError(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT keys3 ${l1} ${l2}\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT l2 two\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("PUT l1 ${k4} ${keys3}\n".encode())
        self.assertEquals("OK", sock.recv(1024).decode())
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.HOST, self.PORT))
        sock.send("GET keys3\n".encode())
        self.assertEquals("VALUE\n", sock.recv(1024).decode())
        self.assertEquals("ERROR: Infinite recursion", sock.recv(1024).decode())
        sock.close()