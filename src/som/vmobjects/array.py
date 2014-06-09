from rpython.rlib.jit import promote
from .abstract_object import AbstractObject
from rpython.rlib.debug import make_sure_not_resized


class Array(AbstractObject):

    _immutable_fields_ = ["_indexable_fields"]
    
    def __init__(self, nilObject, number_of_indexable_fields, values = None):
        AbstractObject.__init__(self)
        nilObject = promote(nilObject)

        # Private array of indexable fields
        if values is None:
            self._indexable_fields = [nilObject] * promote(number_of_indexable_fields)
        else:
            self._indexable_fields = values
        make_sure_not_resized(self._indexable_fields)
        
    def get_indexable_field(self, index):
        # Get the indexable field with the given index
        return self._indexable_fields[index]
  
    def set_indexable_field(self, index, value):
        # Set the indexable field with the given index to the given value
        self._indexable_fields[index] = value

    def get_indexable_fields(self):
        return self._indexable_fields

    def get_number_of_indexable_fields(self):
        # Get the number of indexable fields in this array
        return len(self._indexable_fields)

    def copy_and_extend_with(self, value, universe):
        result = Array(universe.nilObject,
                       self.get_number_of_indexable_fields() + 1)

        self._copy_indexable_fields_to(result)

        # Insert the given object as the last indexable field in the new array
        result.set_indexable_field(self.get_number_of_indexable_fields(), value)
        return result

    def _copy_indexable_fields_to(self, destination):
        for i, value in enumerate(self._indexable_fields):
            destination._indexable_fields[i] = value

    def get_class(self, universe):
        return universe.arrayClass
