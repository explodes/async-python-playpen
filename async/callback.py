class ExtensibleCallback(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = list(args)
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        args = self.args + list(args)
        kwargs.update(self.kwargs)
        self.func(*args, **kwargs)

    def call(self):
        self()


class StaticCallback(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = list(args)
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        self.func(*self.args, **self.kwargs)

    def call(self):
        self()
