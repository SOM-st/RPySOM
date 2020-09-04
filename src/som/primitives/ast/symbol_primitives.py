from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import AstPrimitive as Primitive
from som.vm.globals import trueObject, falseObject


def _asString(ivkbl, rcvr, args):
    return String(rcvr.get_embedded_string())


def _equals(ivkbl, rcvr, args):
    op1 = args[0]
    op2 = rcvr

    if op1 is op2:
        return trueObject
    else:
        return falseObject


class SymbolPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe,
                                                   _asString))
        self._install_instance_primitive(Primitive("=", self._universe, _equals), False)
