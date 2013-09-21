from som.primitives.primitives import Primitives

from som.vmobjects.primitive import Primitive

def _new(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_instance(rcvr))

class ClassPrimitives(Primitives):
    def install_primitives(self):
        self._install_instance_primitive(Primitive("new", self._universe, _new))