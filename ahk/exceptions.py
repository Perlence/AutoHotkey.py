class Error(Exception):
    def __init__(self, message, what=None, extra=None, file=None, line=None):
        super().__init__(message)
        # XXX: Add AHK exception info to Python traceback?
        self.message = message
        self.what = what
        self.extra = extra
        self.file = file
        self.line = line
