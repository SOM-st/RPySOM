from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.block       import block_evaluate 

def _execute_block(frame, block, interpreter, universe):
    method = block.get_method()
    b = universe.new_block(method, block.get_context())
    frame.push(b)
    
    block_evaluate(b, interpreter, frame)
    return frame.pop()    

def _whileTrue(ivkbl, frame, interpreter):
    loop_body      = frame.pop()
    loop_condition = frame.pop()
    
    universe = interpreter.get_universe()
    trueObj = universe.trueObject
    
    condition_result = _execute_block(frame, loop_condition, interpreter, universe)
    while condition_result is trueObj:
        _execute_block(frame, loop_body, interpreter, universe)
        condition_result = _execute_block(frame, loop_condition, interpreter, universe)
    
    frame.push(universe.nilObject)

def _whileFalse(ivkbl, frame, interpreter):
    loop_body      = frame.pop()
    loop_condition = frame.pop()
    
    universe = interpreter.get_universe()
    trueObj = universe.falseObject
    
    condition_result = _execute_block(frame, loop_condition, interpreter, universe)
    while condition_result is trueObj:
        _execute_block(frame, loop_body, interpreter, universe)
        condition_result = _execute_block(frame, loop_condition, interpreter, universe)
    
    frame.push(universe.nilObject)

class BlockPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("whileTrue:",  self._universe, _whileTrue))
        self._install_instance_primitive(Primitive("whileFalse:", self._universe, _whileFalse))
