from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive


def _asString(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_string(rcvr.get_string()))


class SymbolPrimitives(Primitives):
    
    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
