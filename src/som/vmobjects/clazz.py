from som.vmobjects.object import Object

class Class(Object):
    
    # Static field indices and number of class fields
    SUPER_CLASS_INDEX         = 1 + Object.CLASS_INDEX
    NAME_INDEX                = 1 + SUPER_CLASS_INDEX
    INSTANCE_FIELDS_INDEX     = 1 + NAME_INDEX
    INSTANCE_INVOKABLES_INDEX = 1 + INSTANCE_FIELDS_INDEX
    NUMBER_OF_CLASS_FIELDS    = 1 + INSTANCE_INVOKABLES_INDEX

    
    def __init__(self, universe, number_of_fields = None):
        super(Class, self).__init__(universe.nilObject, number_of_fields)
        self._invokables_table = {}
        self._universe = universe
        
    def get_super_class(self):
        # Get the super class by reading the field with super class index
        return self.get_field(self.SUPER_CLASS_INDEX)

    def set_super_class(self, value):
        # Set the super class by writing to the field with super class index
        self.set_field(self.SUPER_CLASS_INDEX, value)
    
    def has_super_class(self):
        # Check whether or not this class has a super class
        return self.get_field(self.SUPER_CLASS_INDEX) != self._universe.nilObject


    def get_name(self):
        # Get the name of this class by reading the field with name index
        return self.get_field(self.NAME_INDEX)
  
    def set_name(self, value):
        # Set the name of this class by writing to the field with name index
        self.set_field(self.NAME_INDEX, value)

    def get_instance_fields(self):
        # Get the instance fields by reading the field with the instance fields index
        return self.get_field(self.INSTANCE_FIELD_INDEX)

    def set_instance_fields(self, value):
        # Set the instance fields by writing to the field with the instance fields index
        self.set_field(self.INSTANCE_FIELD_INDEX, value)
  
