from rpython.rlib import jit

from som.vmobjects.abstract_object import AbstractObject
from som.vmobjects.primitive import Primitive

class Block(AbstractObject):
    
    _immutable_fields_ = ["_method", "_context"]
    
    def __init__(self, method, context):
        AbstractObject.__init__(self)
        self._method  = method
        self._context = context
        
    def get_method(self):
        return jit.promote(self._method)
    
    def get_context(self):
        return self._context

    def get_outer_self(self):
        return self._context.get_self()
    
    def get_class(self, universe):
        return universe.blockClasses[self._method.get_number_of_arguments()]
  
    class Evaluation(Primitive):

        _immutable_fields_ = ['_number_of_arguments']

        def __init__(self, num_args, universe, invoke):
            Primitive.__init__(self, self._compute_signature_string(num_args),
                               universe, invoke)
            self._number_of_arguments = num_args

        @staticmethod
        def _compute_signature_string(num_args):
            # Compute the signature string
            signature_string = "value"
            if num_args > 1:
                signature_string += ":"
                if num_args > 2:
                    # Add extra with: selector elements if necessary
                    signature_string += "with:" * (num_args - 2)
          
            # Return the signature string
            return signature_string


def block_evaluation_primitive(num_args, universe):
    return Block.Evaluation(num_args, universe, _invoke)


def block_evaluate(block, args):
    method = block.get_method()
    return method.invoke(block, args)


def _invoke(ivkbl, rcvr, args):
    assert isinstance(ivkbl, Block.Evaluation)
    return block_evaluate(rcvr, args)
