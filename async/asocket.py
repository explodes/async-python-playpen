try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import socket

READ_LEN = 1024 * 8
DEFAULT_TIMEOUT = 10


class AsyncSocket(object):
    def __init__(self, looper, host, port, timeout=DEFAULT_TIMEOUT):
        self.looper = looper
        self.host = host
        self.port = port
        self.timeout = timeout

    def as_async(self, func, *args, **kwargs):
        self.looper.enqueue_now(func, *args, **kwargs)

    def send_all(self, sock, messages, callback):
        self.as_async(self.send, sock, "".join(messages), 0, callback)

    def send(self, sock, string, index, callback):
        index += sock.send(string[index:])
        if index == len(string):
            self.as_async(callback)
        else:
            self.as_async(self.send, sock, string, index, callback)

    def recv_all(self, sock, buff, callback):
        self.as_async(self.recv, sock, buff, callback)

    def recv(self, sock, buff, callback):
        data = sock.recv(READ_LEN)
        if data:
            buff.write(data)
            self.as_async(self.recv, sock, buff, callback)
        else:
            self.as_async(callback)

    def close(self, sock):
        sock.shutdown(1)
        sock.close()

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(self.timeout)
        return sock
