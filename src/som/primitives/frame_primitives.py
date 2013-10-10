from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive

def _method(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_method())

def _previous_frame(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_previous_frame())

class FramePrimitives(Primitives):
    
    def install_primitives(self):
        self._install_instance_primitive(Primitive("method",
                                         self._universe, _method))
        self._install_instance_primitive(Primitive("previousFrame",
                                         self._universe, _previous_frame))
 