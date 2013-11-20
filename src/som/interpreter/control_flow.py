class RestartLoopException(BaseException):
    pass

class ReturnException(BaseException):
    
    _immutable_fields_ = ["_result", "_target"]
    
    def __init__(self, result, target):
        self._result = result
        self._target = target
    
    def get_result(self):
        return self._result
    
    def has_reached_target(self, current):
        return current is self._target
