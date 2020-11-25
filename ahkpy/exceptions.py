class Error(Exception):
    """The runtime error that was raised in the AutoHotkey.

    Contains the following attributes:

    .. attribute:: message

       The error message.

    .. attribute:: what

       The name of the command, function or label which was executing
       or about to execute when the error occurred.

    .. attribute:: extra

       Additional information about the error, if available.

    .. attribute:: file

       The full path of the AHK script file which contains the line
       where the error occurred.

    .. attribute:: line

       The line number in the AHK script where the error occurred.
    """

    def __init__(self, message, what=None, extra=None, file=None, line=None):
        super().__init__(message)
        # TODO: Add AHK exception info to Python traceback?
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
