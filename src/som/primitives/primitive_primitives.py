from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive 

def _holder(ivkbl, rcvr, args):
    return rcvr.get_holder()

def _signature(ivkbl, rcvr, args):
    return rcvr.get_signature()

class PrimitivePrimitives(Primitives):
    def install_primitives(self):
        self._install_instance_primitive(Primitive("holder",
                                                   self._universe, _holder))
        self._install_instance_primitive(Primitive("signature",
                                                   self._universe, _signature))
