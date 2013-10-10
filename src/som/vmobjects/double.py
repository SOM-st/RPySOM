from som.vmobjects.object import Object

class Double(Object):

    _immutable_fields_ = ["_embedded_double"]
    
    def __init__(self, nilObject, value):
        Object.__init__(self, nilObject)
        self._embedded_double = value
    
    def get_embedded_double(self):
        return self._embedded_double
