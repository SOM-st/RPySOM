from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import BcPrimitive as Primitive


def _holder(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_holder())


def _signature(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_signature())


class MethodPrimitives(Primitives):
    def install_primitives(self):
        self._install_instance_primitive(Primitive("holder",
                                                   self._universe, _holder))
        self._install_instance_primitive(Primitive("signature",
                                                   self._universe, _signature))
