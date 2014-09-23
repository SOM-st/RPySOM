from som.primitives.primitives import Primitives

from som.vmobjects.abstract_object import AbstractObject
from som.vmobjects.array           import Array
from som.vmobjects.method          import Method
from som.vmobjects.primitive       import Primitive


def _holder(ivkbl, rcvr, args):
    return rcvr.get_holder()


def _signature(ivkbl, rcvr, args):
    return rcvr.get_signature()


def _invoke_on_with(ivkbl, rcvr, args):
    assert isinstance(rcvr,    Method)
    assert isinstance(args[0], AbstractObject)
    assert isinstance(args[1], Array) or args[1] is ivkbl.get_universe().nilObject

    if args[1] is ivkbl.get_universe().nilObject:
        direct_args = []
    else:
        direct_args = args[1].get_indexable_fields()
    return rcvr.invoke(args[0], direct_args)


class MethodPrimitives(Primitives):
    def install_primitives(self):
        self._install_instance_primitive(Primitive("holder",
                                                   self._universe, _holder))
        self._install_instance_primitive(Primitive("signature",
                                                   self._universe, _signature))
        self._install_instance_primitive(Primitive("invokeOn:with:",
                                                   self._universe, _invoke_on_with))
