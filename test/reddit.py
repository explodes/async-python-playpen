# coding=utf-8
import json

from async.callback import ExtensibleCallback
from async.http import HttpsSocketAsync
from async.looper import Looper


class RedditReader:
    def __init__(self):
        self.looper = Looper(wait=0.01)
        self.client = HttpsSocketAsync(self.looper, 'www.reddit.com')

    def request_top_post(self, subreddit, n=4):
        url = '/r/{0}/top.json?sort=top&t=day&limit={1}'.format(subreddit, n)
        self.client.request("GET", url, ExtensibleCallback(self.on_response))

    def on_response(self, response):
        if response.status == 200:
            json_body = json.loads(response.read())
            self.on_json(json_body)
        else:
            self.on_http_error(None, response)

    def on_json(self, response):
        for post in response['data']['children']:
            data = post["data"]
            print u"/r/{subreddit:<12} {ups:>4}↕{downs:<3} {title} ({url})".format(**data)

    def run(self):
        self.looper.enqueue_now(self.request_top_post, "python")
        self.looper.enqueue_now(self.request_top_post, "programming")
        self.looper.enqueue_now(self.request_top_post, "java")
        self.looper.enqueue_now(self.request_top_post, "android")
        self.looper.enqueue_now(self.request_top_post, "vive")
        self.looper.loop()

    def on_http_error(self, url, response):
        print "Error {0} at {1}".format(response.status, url)
        for header in response.getheaders():
            print header
        self.looper.stop()


def main():
    RedditReader().run()


if __name__ == '__main__':
    main()
