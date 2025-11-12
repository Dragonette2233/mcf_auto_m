import threading


class MCFException(Exception): ...
class MCFTimeoutError(Exception): ...
class MCFNoConnectionError(Exception): ...


class MCFThread(threading.Thread):
    def __init__(self, func, args=False):
        super().__init__()
        self._target = func
        self.daemon = True
        self.name = f"{func.__name__}-Thr"
        if args:
            self._args = args

