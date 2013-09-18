from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive

class SymbolPrimitives(Primitives):
    
    def install_primitives(self):
        def _asString(ivkbl, frame, interpreter):
            rcvr = frame.pop()
            frame.push(self._universe.new_string(rcvr.get_string()))
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
