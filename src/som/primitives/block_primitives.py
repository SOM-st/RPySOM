from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.block       import block_evaluate 

from rpython.rlib import jit

def get_printable_location(interpreter, method_body, method_condition, while_type):
    from som.vmobjects.method import Method
    from som.interpreter.bytecodes import bytecode_as_str
    assert isinstance(method_body, Method)
    assert isinstance(method_condition, Method)
    #bc = method.get_bytecode(bytecode_index)
#     return "%s @ %d in %s" % (bytecode_as_str(bc),
#                               bytecode_index,
#                               method.merge_point_string())
    return "TODO"


jitdriver = jit.JitDriver(
    greens=['interpreter', 'method_body', 'method_condition', 'while_type'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


def _execute_block(frame, block, block_method, interpreter, universe):
    b = universe.new_block(block_method, block.get_context())
    frame.push(b)
    
    block_evaluate(b, interpreter, frame)
    return frame.pop()    


def _whileLoop(frame, interpreter, while_type):
    loop_body      = frame.pop()
    loop_condition = frame.pop()
    
    universe = interpreter.get_universe()

    method_body = loop_body.get_method()
    method_condition = loop_condition.get_method()
    
    while True:
        jitdriver.jit_merge_point(interpreter=interpreter,
                                  method_body=method_body,
                                  method_condition=method_condition,
                                  #universe=universe,
                                  while_type=while_type)
        condition_result = _execute_block(frame, loop_condition, method_condition, interpreter, universe)
        if condition_result is while_type:
            _execute_block(frame, loop_body, method_body, interpreter, universe)
        else:
            break
    
    frame.push(universe.nilObject)


def _whileFalse(ivkbl, frame, interpreter):
    _whileLoop(frame, interpreter, interpreter.get_universe().falseObject)


def _whileTrue(ivkbl, frame, interpreter):
    _whileLoop(frame, interpreter, interpreter.get_universe().trueObject)

class BlockPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("whileTrue:",  self._universe, _whileTrue))
        self._install_instance_primitive(Primitive("whileFalse:", self._universe, _whileFalse))
