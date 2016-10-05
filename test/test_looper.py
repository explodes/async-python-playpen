import unittest
from datetime import date
from datetime import datetime
from datetime import timedelta

from async.looper import Looper
from async.looper import Time


class LooperTest(unittest.TestCase):
    def setUp(self):
        self.looper = Looper(wait=0)

    def dummy(self):
        pass

    def dummy2(self):
        pass

    def stopper(self):
        self.looper.stop()

    def test_empty_loop_exits(self):
        self.looper.loop()

    def test_stop_stops(self):
        self.looper.enqueue_now(self.stopper)
        self.looper.enqueue_now(self.dummy)
        self.looper.enqueue_now(self.dummy)

        self.looper.loop()

        self.assertEquals(2, self.looper.size())

    def test_enqueue_now(self):
        # race condition - will fail sometimes
        time = Time.now()
        self.looper.enqueue_now(self.dummy)
        self.assertEquals(1, self.looper.size())
        self.assertEquals(time, self.looper._queue[0].time)

    def test_enqueue_next(self):
        self.looper.enqueue_now(self.dummy)
        self.looper.enqueue_next(self.dummy2)
        self.assertEquals(2, self.looper.size())
        self.assertEquals(0, self.looper._queue[0].time)
        self.assertEquals(self.dummy2, self.looper._queue[0].func)

    def test_enqueue_with_millis(self):
        # race condition - will fail sometimes
        time = Time.millis_from_now(1000)
        self.looper.enqueue(1000, self.dummy)
        self.assertEquals(1, self.looper.size())
        self.assertEquals(time, self.looper._queue[0].time)

    def test_enqueue_with_datetime(self):
        d = datetime(2016, 1, 1, 12, 12, 12)
        self.looper.enqueue(d, self.dummy)
        self.assertEquals(1, self.looper.size())
        self.assertEquals(Time.on_date(d), self.looper._queue[0].time)

    def test_enqueue_with_date(self):
        d = date(2016, 1, 1)
        self.looper.enqueue(d, self.dummy)
        self.assertEquals(1, self.looper.size())
        self.assertEquals(Time.on_date(d), self.looper._queue[0].time)

    def test_enqueue_with_timedelta(self):
        # race condition - will fail sometimes
        d = timedelta(milliseconds=340)
        self.looper.enqueue(d, self.dummy)
        self.assertEquals(1, self.looper.size())
        self.assertEquals(Time.after_timedelta(d), self.looper._queue[0].time)

    def test_enqueue_at(self):
        # race condition - will fail sometimes
        time = Time.millis_from_now(1000)
        self.looper.enqueue_at(time, self.dummy)
        self.assertEquals(1, self.looper.size())
        self.assertEquals(time, self.looper._queue[0].time)

    def test_size(self):
        self.assertEquals(0, self.looper.size())

        self.looper.enqueue_now(self.stopper)
        self.assertEquals(1, self.looper.size())

        self.looper.enqueue_now(self.stopper)
        self.assertEquals(2, self.looper.size())

        self.looper.loop()

        self.assertEquals(1, self.looper.size())