from som.vmobjects.abstract_object import AbstractObject

class Double(AbstractObject):

    _immutable_fields_ = ["_embedded_double"]
    
    def __init__(self, value):
        AbstractObject.__init__(self)
        assert isinstance(value, float)
        self._embedded_double = value
    
    def get_embedded_double(self):
        return self._embedded_double

    def get_class(self, universe):
        return universe.doubleClass
