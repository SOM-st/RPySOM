from som.interpreter.control_flow import RestartLoopException
from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive

def _restart(ivkbl, frame, interpreter):
    raise RestartLoopException()

class BlockPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("restart", self._universe, _restart))
