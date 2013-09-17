from som.vmobjects.object    import Object
from som.vmobjects.primitive import Primitive

class Block(Object):
    
    METHOD_INDEX           = 1 + Object.CLASS_INDEX
    CONTEXT_INDEX          = 1 + METHOD_INDEX
    NUMBER_OF_BLOCK_FIELDS = 1 + CONTEXT_INDEX
    
    def __init__(self, nilObject):
        super(Block, self).__init__(nilObject)
        self._number_of_arguments = 0
        
    def get_method(self):
        # Get the method of this block by reading the field with method index
        return self.get_field(self.METHOD_INDEX)
  

    def set_method(self, value):
        # Set the method of this block by writing to the field with method index
        self.set_field(self.METHOD_INDEX, value)
  
    def get_context(self):
        # Get the context of this block by reading the field with context index
        return self.get_field(self.CONTEXT_INDEX)

    def set_context(self, value):
        # Set the context of this block by writing to the field with context index
        return self.setField(self.CONTEXT_INDEX, value)

    def _get_default_number_of_fields(self):
        # Return the default number of fields for a block
        return self._NUMBER_OF_BLOCK_FIELDS

    @classmethod
    def get_evaluation_primitive(cls, num_args, universe):
        return Evaluation(num_args, universe)
  
    class Evaluation(Primitive):
        def __init__(self, num_args, universe):
            super(Evaluation, self).__init__(self._compute_signature_string(num_args), universe, self.invoke)
            self._number_of_arguments = num_args

        def invoke(self, frame, interpreter):
            # Get the block (the receiver) from the stack
            rcvr = frame.get_stack_element(self._number_of_arguments - 1)

            # Get the context of the block...
            context = rcvr.get_context()

            # Push a new frame and set its context to be the one specified in
            # the block
            new_frame = interpreter.push_new_frame(rcvr.get_method())
            new_frame.copy_arguments_from(frame);
            new_frame.set_context(context)


        def _compute_signature_string(self, num_args):
            # Compute the signature string
            signature_string = "value"
            if num_args > 1:
                signature_string += ":"

            # Add extra value: selector elements if necessary
            for _ in range(2, num_args):
                signature_string += "with:"
          
            # Return the signature string
            return signature_string
