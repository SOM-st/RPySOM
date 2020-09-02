from som.vmobjects.primitive   import BcPrimitive as Primitive
from som.primitives.primitives import Primitives


def _at(ivkbl, frame, interpreter):
    i    = frame.pop()
    rcvr = frame.pop()
    frame.push(rcvr.get_indexable_field(i.get_embedded_integer() - 1))


def _atPut(ivkbl, frame, interpreter):
    value = frame.pop()
    index = frame.pop()
    rcvr  = frame.get_stack_element(0)
    rcvr.set_indexable_field(index.get_embedded_integer() - 1, value)


def _length(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_integer(rcvr.get_number_of_indexable_fields()))


def _new(ivkbl, frame, interpreter):
    length = frame.pop()
    frame.pop() # not required
    frame.push(interpreter.get_universe().new_array_with_length(length.get_embedded_integer()))


class ArrayPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("at:", self._universe, _at))
        self._install_instance_primitive(Primitive("at:put:", self._universe, _atPut))
        self._install_instance_primitive(Primitive("length", self._universe, _length))

        self._install_class_primitive(Primitive("new:", self._universe, _new))
