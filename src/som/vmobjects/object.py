class Object(object):
    
    # Static field indices and number of object fields
    CLASS_INDEX             = 0
    NUMBER_OF_OBJECT_FIELDS = 1 + CLASS_INDEX

    def __init__(self, nilObject, number_of_fields = None):
        num_fields = number_of_fields if number_of_fields else self._get_default_number_of_fields()
        self._fields = None
        self.set_number_of_fields_and_clear(num_fields, nilObject)
    
    def get_class(self):
        # Get the class of this object by reading the field with class index
        return self.get_field(self.CLASS_INDEX)

    def set_class(self, value):
        # Set the class of this object by writing to the field with class index
        self.set_field(self.CLASS_INDEX, value)

    def get_field_name(self, index):
        # Get the name of the field with the given index
        return self.get_class().get_instance_field_name(index)

    def get_field_index(self, name):
        # Get the index for the field with the given name
        return self.get_class().lookup_field_fndex(name)

    def get_number_of_fields(self):
        # Get the number of fields in this object
        return len(self._fields)

    def set_number_of_fields_and_clear(self, value, nilObject):
        # Allocate a new array of fields
        self._fields = [nilObject] * value

    def _get_default_number_of_fields(self):
        # Return the default number of fields in an object
        return self.NUMBER_OF_OBJECT_FIELDS
    
    def get_field(self, index):
        # Get the field with the given index
        return self._fields[index]
  
    def set_field(self, index, value):
        # Set the field with the given index to the given value
        self._fields[index] = value