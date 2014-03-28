from rpython.rlib import jit


class _FrameOnStackMarker(object):
    
    def __init__(self):
        self._on_stack = True
    
    def is_on_stack(self):
        return self._on_stack
    
    def frame_no_longer_on_stack(self):
        self._on_stack = False


class Frame(object):
        
    _immutable_fields_ = ["_receiver", "_arguments[*]", "_temps"]

    def __init__(self, receiver, arguments, number_of_temps,
                 nilObject):
        self._receiver       = receiver
        self._arguments      = arguments
        self._temps          = [nilObject] * number_of_temps
        self._on_stack_marker= None

    def get_argument(self, index):
        jit.promote(index)
        return self._arguments[index]

    def set_argument(self, index, value):
        self._arguments[index] = value

    def get_temp(self, index):
        jit.promote(index)
        return self._temps[index]

    def set_temp(self, index, value):
        jit.promote(index)
        self._temps[index] = value

    def get_self(self):
        return self._receiver
    
    def init_and_get_on_stack_marker(self):
        self._on_stack_marker = _FrameOnStackMarker()
        return self._on_stack_marker
    
    def get_on_stack_marker(self):
        return self._on_stack_marker

    def __str__(self):
        return "Frame(%s, %s, %s)" % (self._receiver, self._arguments,
                                      self._temps)
