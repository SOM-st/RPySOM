from som.primitives.primitives import Primitives

from som.vmobjects.primitive import Primitive

class ClassPrimitives(Primitives):
    def install_primitives(self):
        def _new(self, frame, interpreter):
            rcvr = frame.pop()
            frame.push(self._universe.new_instance(rcvr))
        self._install_instance_primitive(Primitive("new", self._universe, _new))