import heapq
import time
from collections import namedtuple
from datetime import date
from datetime import datetime
from datetime import timedelta


class Time(object):
    @staticmethod
    def now():
        return int(time.time() * 1000)

    @staticmethod
    def millis_from_now(millis):
        return int(Time.now() + millis)

    @staticmethod
    def seconds_from_now(seconds):
        return Time.millis_from_now(seconds * 1000)

    @staticmethod
    def on_date(date):
        return int(time.mktime(date.timetuple()) * 1000)

    @staticmethod
    def after_timedelta(delta):
        millis = delta.seconds * 1000 + delta.microseconds / 1000
        return Time.millis_from_now(millis)


class Entry(namedtuple("Entry", ["time", "func", "args", "kwargs"])):
    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time

    def __str__(self):
        return "Entry({0}, *{1}, **{2})".format(self.func.__name__, self.args, self.kwargs)


class Looper(object):
    """
    Async looper class.

    Typical lifecycle:

    looper = Looper()
    looper.enqueue(datetime(2016, 10, 3, 17, 34, 24), process)
    looper.loop()

    When the looper runs out of queued callbacks, it will end.
    The loop can be aborted by a call to looper.stop()
    """

    def __init__(self, wait=0.1):
        """
        Create a looper with a specified wait between no-ops
        :param wait: period of time to wait between loop cycles
        """
        self._queue = []
        self._looping = True
        self.wait = wait

    def size(self):
        """
        :return: The current size of the queue
        """
        return len(self._queue)

    def loop(self):
        """
        Loop through all scheduled callbacks.
        If callbacks do not add more callbacks, the loop will end naturally.
        Looping can be aborted by calling stop()
        """
        self._looping = True
        while self._looping and self.size() > 0:
            # get next item
            item = self._queue[0]
            # run it if it is time
            if item.time == 0 or item.time <= Time.now():
                item.func(*item.args, **item.kwargs)
                heapq.heappop(self._queue)
            elif self.wait > 0:
                time.sleep(self.wait)

    def stop(self):
        """
        Stop the looper
        """
        self._looping = False

    def enqueue_now(self, func, *args, **kwargs):
        """
        Enqueue a callback next with low priority. Not guaranteed to be run next.
        :param func: function to call
        :param args: function arguments
        :param kwargs: function kwargs
        """
        self.enqueue(0, func, *args, **kwargs)

    def enqueue_next(self, func, *args, **kwargs):
        """
        Enqueue a callback next with high priority. Not guaranteed to be run next.
        :param func: function to call
        :param args: function arguments
        :param kwargs: function kwargs
        """
        self.enqueue_at(0, func, *args, **kwargs)

    def enqueue(self, when, func, *args, **kwargs):
        """
        Enqueue a scheduled callback
        :param when: millis (int), date, datetime, or timedelta describing when to run
        :param func: function to call
        :param args: function arguments
        :param kwargs: function kwargs
        """
        if isinstance(when, int):
            millis = Time.millis_from_now(when)
        elif isinstance(when, (date, datetime)):
            millis = Time.on_date(when)
        elif isinstance(when, timedelta):
            millis = Time.after_timedelta(when)
        else:
            raise ValueError("Time must be datetime, timedelta, or millis")
        self.enqueue_at(millis, func, *args, **kwargs)

    def enqueue_at(self, timestamp, func, *args, **kwargs):
        """
        Enqueue a callback at a specific timestamp
        :param timestamp: millisecond-precision timestamp
        :param func: function to call
        :param args: function arguments
        :param kwargs: function kwargs
        """
        heapq.heappush(self._queue, Entry(timestamp, func, args, kwargs))
