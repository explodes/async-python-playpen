import unittest

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from async.http import AsyncHttpSocket
from async.looper import Looper

from httplib import HTTPResponse


class HttpTest(unittest.TestCase):
    def setUp(self):
        self.has_response = False
        self.response = None

    def on_response(self, response):
        self.has_response = True
        self.response = response
        self.assertIsNotNone(response)
        self.assertIsInstance(response, HTTPResponse)
        self.assertEqual(200, response.status)

    def test_get(self):
        looper = Looper()

        client = AsyncHttpSocket(looper, "www.google.com")
        client.get("/", self.on_response)

        looper.loop()

        self.assertTrue(self.has_response)
