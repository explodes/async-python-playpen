try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import ssl
from httplib import HTTPResponse

import asocket
from async.callback import StaticCallback

CRLF = "\r\n"
HTTP_VERSION = "HTTP/1.0"
USER_AGENT = "python-toy/0.0.0"


class FakeSocket:
    def __init__(self, buff):
        self._file = buff

    def makefile(self, *args, **kwargs):
        return self._file


class AsyncHttpSocket(asocket.AsyncSocket):
    def __init__(self, looper, host, port=80, timeout=asocket.DEFAULT_TIMEOUT):
        super(AsyncHttpSocket, self).__init__(looper, host, port, timeout=timeout)

    def parse(self, buff, callback):
        buff.seek(0)
        response = HTTPResponse(FakeSocket(buff))
        response.begin()
        self.as_async(callback, response)

    def close_and_parse(self, sock, buff, callback):
        self.close(sock)
        self.parse(buff, callback)

    def request(self, method, url, callback):
        url = url if url else "/"

        sock = self.create_socket()
        sock.connect((self.host, self.port))

        buff = StringIO()

        messages = [
            "{method} {url} {version}{crlf}".format(method=method, url=url, crlf=CRLF, version=HTTP_VERSION),
            "Host: {host}{crlf}".format(host=self.host, crlf=CRLF),
            "User-Agent: {agent}{crlf}".format(agent=USER_AGENT, crlf=CRLF),
            "Accept: */*{crlf}".format(crlf=CRLF),
            "{crlf}".format(crlf=CRLF)
        ]

        self.send_all(sock, messages,
                      StaticCallback(self.recv_all, sock, buff,
                                     StaticCallback(self.close_and_parse, sock, buff, callback)))

    def get(self, url, callback):
        return self.request("GET", url, callback)


class HttpsSocketAsync(AsyncHttpSocket):
    def __init__(self, looper, host, port=443, timeout=asocket.DEFAULT_TIMEOUT):
        super(HttpsSocketAsync, self).__init__(looper, host, port=port, timeout=timeout)

    def create_socket(self):
        sock = super(HttpsSocketAsync, self).create_socket()
        sock = ssl.wrap_socket(sock)
        return sock
