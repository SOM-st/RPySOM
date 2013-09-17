from som.vmobjects.object import Object

class BigInteger(Object):
    def __init__(self, nilObject):
        super(BigInteger, self).__init__(nilObject)
        self._embedded_big_integer = None
    
    def get_embedded_big_integer(self):
        return self._embedded_big_integer
    
    def set_embedded_big_integer(self, value):
        self._embedded_big_integer = value