"""
Bare-bones event handling code taken from: http://stackoverflow.com/a/1094423
"""

class EventHook:

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def __call__(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    # NOTE unclear if this works properly
    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler
