from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive

class BlockPrimitives(Primitives):
    
    def install_primitives(self):
        
        def _restart(ivkbl, frame, interpreter):
            frame.set_bytecode_index(0)
            frame.reset_stack_pointer()
        self._install_instance_primitive(Primitive("restart", self._universe, _restart))
