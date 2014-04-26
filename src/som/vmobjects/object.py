from som.vmobjects.abstract_object import AbstractObject


class Object(AbstractObject):

    _immutable_fields_ = ["_class", "_fields"]
    
    # Static field indices and number of object fields
    NUMBER_OF_OBJECT_FIELDS = 0

    def __init__(self, nilObject, number_of_fields = -1):
        num_fields = number_of_fields if number_of_fields != -1 else self._get_default_number_of_fields()
        self._fields = [nilObject] * num_fields
        self._class = nilObject

    def get_class(self, universe):
        return self._class

    def set_class(self, value):
        self._class = value

    def get_field_name(self, index):
        # Get the name of the field with the given index
        return self._class.get_instance_field_name(index)

    def get_field_index(self, name):
        # Get the index for the field with the given name
        return self._class.lookup_field_index(name)

    def get_number_of_fields(self):
        # Get the number of fields in this object
        return len(self._fields)

    def _get_default_number_of_fields(self):
        # Return the default number of fields in an object
        return self.NUMBER_OF_OBJECT_FIELDS
    
    def get_field(self, index):
        # Get the field with the given index
        assert isinstance(index, int)
        return self._fields[index]
  
    def set_field(self, index, value):
        # Set the field with the given index to the given value
        assert isinstance(index, int)
        assert isinstance(value, AbstractObject)
        self._fields[index] = value
