from som.primitives.primitives import Primitives
from som.vm.globals import falseObject, trueObject
from som.vmobjects.primitive import AstPrimitive as Primitive


def _not(ivkbl, frame, interpreter):
    frame.pop()
    frame.push(falseObject)


def _or(ivkbl, frame, interpreter):
    frame.pop()
    frame.push(trueObject)


def _and(ivkbl, frame, interpreter):
    block = frame.pop()
    frame.pop()
    block_method = block.get_method()
    block_method.invoke(frame, interpreter)


class TruePrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("not", self._universe, _not))
        self._install_instance_primitive(Primitive("or:", self._universe, _or))
        # self._install_instance_primitive(Primitive("and:", self._universe, _and))
        self._install_instance_primitive(Primitive("||", self._universe, _or))
        # self._install_instance_primitive(Primitive("&&", self._universe, _and))
