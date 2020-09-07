from som.primitives.array_primitives import ArrayPrimitivesBase
from som.vmobjects.primitive import Primitive


def _at_put(ivkbl, frame, interpreter):
    value = frame.pop()
    index = frame.pop()
    rcvr  = frame.top()
    rcvr.set_indexable_field(index.get_embedded_integer() - 1, value)


class ArrayPrimitives(ArrayPrimitivesBase):

    def install_primitives(self):
        ArrayPrimitivesBase.install_primitives(self)
        self._install_instance_primitive(Primitive("at:put:", self._universe, _at_put))
