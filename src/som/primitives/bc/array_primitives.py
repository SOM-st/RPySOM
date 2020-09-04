from som.vm.universe import Universe
from som.vmobjects.primitive   import UnaryPrimitive, BinaryPrimitive, Primitive
from som.primitives.primitives import Primitives


def _at(rcvr, i):
    return rcvr.get_indexable_field(i.get_embedded_integer() - 1)


def _at_put(ivkbl, frame, interpreter):
    value = frame.pop()
    index = frame.pop()
    rcvr  = frame.top()
    rcvr.set_indexable_field(index.get_embedded_integer() - 1, value)


def _length(rcvr):
    from som.vmobjects.integer import Integer
    return Integer(rcvr.get_number_of_indexable_fields())


def _new(rcvr, length):
    return Universe.new_array_with_length(length.get_embedded_integer())


class ArrayPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(BinaryPrimitive("at:", self._universe, _at))
        self._install_instance_primitive(Primitive("at:put:", self._universe, _at_put))
        self._install_instance_primitive(UnaryPrimitive("length", self._universe, _length))

        self._install_class_primitive(BinaryPrimitive("new:", self._universe, _new))
