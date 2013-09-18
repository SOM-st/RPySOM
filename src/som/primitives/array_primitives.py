from som.vmobjects.primitive   import Primitive
from som.primitives.primitives import Primitives

class ArrayPrimitives(Primitives):
    
    def install_primitives(self):
        def _at(self, frame, interpreter):
            i    = frame.pop()
            rcvr = frame.pop()
            frame.push(rcvr.get_indexable_field(i.get_embedded_integer() - 1)) 
        self._install_instance_primitive(Primitive("at:", self._universe, _at))
        
        def _atPut(self, frame, interpreter):
            value = frame.pop()
            index = frame.pop()
            rcvr  = frame.get_stack_element(0)
            rcvr.set_indexable_field(index.get_embedded_integer() - 1, value)
        self._install_instance_primitive(Primitive("at:put:", self._universe, _atPut))
        
        def _length(self, frame, interpreter):
            rcvr = frame.pop()
            frame.push(self._universe.new_integer(rcvr.get_number_of_indexable_fields()))
        self._install_instance_primitive(Primitive("length", self._universe, _length))
        
        def _new(self, frame, interpreter):
            length = frame.pop()
            frame.pop() # not required
            frame.push(self._universe.new_array_with_length(length.get_embedded_integer()))
        self._install_instance_primitive(Primitive("new:", self._universe, _new))
