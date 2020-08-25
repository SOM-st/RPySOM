from rpython.rlib import jit
from som.vmobjects.object      import Object


class Class(Object):

    _immutable_fields_ = ["_super_class"
                          "_name",
                          "_instance_fields"
                          "_instance_invokables",
                          "_invokables_table",
                          "_universe"]

    def __init__(self, universe, number_of_fields=-1):
        Object.__init__(self, universe.nilObject, number_of_fields)
        self._super_class = universe.nilObject
        self._name        = None
        self._instance_fields = None
        self._instance_invokables = None
        self._invokables_table = {}
        self._universe = universe

    def get_super_class(self):
        return self._super_class

    def set_super_class(self, value):
        self._super_class = value

    def has_super_class(self):
        return self._super_class is not self._universe.nilObject

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    def get_instance_fields(self):
        return self._instance_fields

    def set_instance_fields(self, value):
        self._instance_fields = value

    def get_instance_invokables(self):
        return self._instance_invokables

    def set_instance_invokables(self, value):
        self._instance_invokables = value

        # Make sure this class is the holder of all invokables in the array
        for i in range(0, self.get_number_of_instance_invokables()):
            invokable = self.get_instance_invokable(i)
            assert invokable is not None
            invokable.set_holder(self)

    def get_number_of_instance_invokables(self):
        """ Return the number of instance invokables in this class """
        return self.get_instance_invokables().get_number_of_indexable_fields()

    def get_instance_invokable(self, index):
        """ Get the instance invokable with the given index """
        return self.get_instance_invokables().get_indexable_field(index)

    def set_instance_invokable(self, index, value):
        # Set this class as the holder of the given invokable
        value.set_holder(self)
        self.get_instance_invokables().set_indexable_field(index, value)

    @jit.elidable_promote("all")
    def lookup_invokable(self, signature):
        # Lookup invokable and return if found
        invokable = self._invokables_table.get(signature, None)
        if invokable:
            return invokable

        # Lookup invokable with given signature in array of instance invokables
        for i in range(0, self.get_number_of_instance_invokables()):
            invokable = self.get_instance_invokable(i)
            # Return the invokable if the signature matches
            if invokable.get_signature() == signature:
                self._invokables_table[signature] = invokable
                return invokable

        # Traverse the super class chain by calling lookup on the super class
        if self.has_super_class():
            invokable = self.get_super_class().lookup_invokable(signature)
            if invokable:
                self._invokables_table[signature] = invokable
                return invokable

        # Invokable not found
        return None

    def lookup_field_index(self, field_name):
        # Lookup field with given name in array of instance fields
        i = self.get_number_of_instance_fields() - 1
        while i >= 0:
            # Return the current index if the name matches
            if field_name == self.get_instance_field_name(i):
                return i
            i -= 1

        # Field not found
        return -1


    def add_instance_invokable(self, value):
        # Add the given invokable to the array of instance invokables
        for i in range(0, self.get_number_of_instance_invokables()):
            # Get the next invokable in the instance invokable array
            invokable = self.get_instance_invokable(i)

            # Replace the invokable with the given one if the signature matches
            if invokable.get_signature() == value.get_signature():
                self.set_instance_invokable(i, value)
                return False

        # Append the given method to the array of instance methods
        self.set_instance_invokables(self.get_instance_invokables().copy_and_extend_with(value, self._universe))
        return True

    def add_instance_primitive(self, value, warn_if_not_existing):
        if self.add_instance_invokable(value) and warn_if_not_existing:
            from som.vm.universe import std_print, std_println
            std_print("Warning: Primitive " + value.get_signature().get_embedded_string())
            std_println(" is not in class definition for class " + self.get_name().get_embedded_string())

    def get_instance_field_name(self, index):
        return self.get_instance_fields().get_indexable_field(index)

    def get_number_of_instance_fields(self):
        # Get the total number of instance fields in this class
        return self.get_instance_fields().get_number_of_indexable_fields()

    @staticmethod
    def _includes_primitives(clazz):
        for i in range(0, clazz.get_number_of_instance_invokables()):
            # Get the next invokable in the instance invokable array
            if clazz.get_instance_invokable(i).is_primitive():
                return True
        return False

    def has_primitives(self):
        return (self._includes_primitives(self) or
                self._includes_primitives(self._class))

    def load_primitives(self):
        from som.primitives.known import (primitives_for_class,
                                          PrimitivesNotFound)
        try:
            prims = primitives_for_class(self)
        except PrimitivesNotFound:
            prims = None
        assert prims is not None, "Loading of prims failed for %s. We yet only support prims for known classes" % self.get_name()
        prims(self._universe).install_primitives_in(self)

    def __str__(self):
        return "Class(" + self.get_name().get_embedded_string() + ")"
