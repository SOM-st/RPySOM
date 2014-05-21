from som.vmobjects.abstract_object import AbstractObject


class BigInteger(AbstractObject):

    _immutable_fields_ = ["_embedded_biginteger"]

    def __init__(self, value):
        AbstractObject.__init__(self)
        assert isinstance(value, int)
        self._embedded_biginteger = value
    
    def get_embedded_biginteger(self):
        return self._embedded_biginteger
    
    def get_embedded_value(self):
        """This Method is polymorphic with Integer"""
        return self._embedded_biginteger
    
    def get_class(self, universe):
        return universe.bigintegerClass
