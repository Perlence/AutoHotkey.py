class Error(Exception):
    def __init__(self, message, what=None, extra=None, file=None, line=None):
        super().__init__(message)
        # XXX: Add AHK exception info to Python traceback?
        self.message = message
        self.what = what
        self.extra = extra
        self.file = file
        self.line = line

    def __setattr__(self, name, value):
        if name == "message":
            super().__setattr__("message", value)
            super().__setattr__("args", (value,))
            return

        super().__setattr__(name, value)
