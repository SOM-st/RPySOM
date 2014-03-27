class Invokable(object):
    """An 'interface', or common super class for methods and primitives.
       WARNING: This interface is not used in the RPython version, because
                RPython does not support multiple inheritance.
                It is kept merely for informative purposes to show the common
                parts of Method and Primitive.
    """

    # Tells whether this is a primitive
    def is_primitive(self):
        raise NotImplementedError()

    # Get the signature for this invokable object
    def get_signature(self):
        raise NotImplementedError()

    # Get the holder for this invokable object
    def get_holder(self):
        raise NotImplementedError()

    # Set the holder for this invokable object
    def set_holder(self, value):
        raise NotImplementedError()
