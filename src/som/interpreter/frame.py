from rpython.rlib import jit


class Frame(object):
        
    _immutable_fields_ = ["_receiver", "_arguments[*]", "_temps"]

    def __init__(self, receiver, arguments, number_of_temps, caller_frame,
                 nilObject):
        self._receiver       = receiver
        self._arguments      = arguments
        self._caller_frame   = caller_frame
        self._temps          = [nilObject] * number_of_temps

    def get_argument(self, index):
        jit.promote(index)
        return self._arguments[index]

    def set_argument(self, index, value):
        self._arguments[index] = value

    def get_temp(self, index):
        return self._temps[index]

    def set_temp(self, index, value):
        self._temps[index] = value

    def get_self(self):
        return self._receiver

    def is_on_stack(self):
        return self._caller_frame is not None

    def mark_as_no_longer_on_stack(self):
        self._caller_frame = None

    def __str__(self):
        return "Frame(%s, %s, %s)" % (self._receiver, self._arguments,
                                      self._temps)
