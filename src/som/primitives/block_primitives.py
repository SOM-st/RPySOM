from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive

def _restart(ivkbl, frame, interpreter):
    frame.set_bytecode_index(0)
    frame.reset_stack_pointer()

class BlockPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("restart", self._universe, _restart))
