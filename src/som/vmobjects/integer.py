from som.vmobjects.abstract_object import AbstractObject

class Integer(AbstractObject):
    
    _immutable_fields_ = ["_embedded_integer"]
    
    def __init__(self, value):
        AbstractObject.__init__(self)
        self._embedded_integer = value
    
    def get_embedded_integer(self):
        return self._embedded_integer
        
    def get_embedded_value(self):
        """This Method is polymorphic with BigInteger"""
        return self._embedded_integer
    
    def __str__(self):
        return str(self._embedded_integer)
    
    def get_class(self, universe):
        return universe.integerClass
    
def integer_value_fits(value):
    return -2147483646 < value <= 2147483647
