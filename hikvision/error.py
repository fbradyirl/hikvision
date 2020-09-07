"""
hikvision.error
~~~~~~~~~~~~~~~~~~~~

Module errors and exceptionss

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""


class MissingParamError(Exception):

    """
    This exception is raised when there is a Missing
    Required param.
    """

    def __init__(self, message='', original=None):
        Exception.__init__(self)
        self.message = message
        self.original = original

    def __str__(self):
        if self.original:
            original_name = type(self.original).__name__
            message = '%s Original exception: '\
                '%s, "%s"' % (self.message, original_name, str(self.original))
            return message
        return self.message


class HikvisionError(Exception):

    """
    This exception is raised when there has occurred an error related to
    communication with hikvision. It is a subclass of Exception.
    """

    def __init__(self, message='', original=None):
        Exception.__init__(self)
        self.message = message
        self.original = original

    def __str__(self):
        if self.original:
            original_name = type(self.original).__name__
            message = '%s Original exception:'\
                ' %s, "%s"' % (self.message, original_name, str(self.original))
            return message
        return self.message
