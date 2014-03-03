from som.primitives.primitives import Primitives
from som.vmobjects.method import Method
from som.vmobjects.primitive   import Primitive
from som.vmobjects.block       import block_evaluate, Block

from rpython.rlib import jit


def get_printable_location(body_method, condition_method, while_type):
    assert isinstance(condition_method, Method)
    assert isinstance(body_method, Method)

    return "%s while %s: %s" % (condition_method.merge_point_string(),
                                while_type,
                                body_method.merge_point_string())


jitdriver = jit.JitDriver(
    greens=['body_method', 'condition_method', 'while_type'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


def _whileLoop(frame, rcvr, args, while_type, universe):
    loop_body      = args[0]
    loop_condition = rcvr
    body_method    = loop_body.get_method()
    condition_method = loop_condition.get_method()

    while True:
        jitdriver.jit_merge_point(body_method     = body_method,
                                  condition_method= condition_method,
                                  while_type    = while_type)

        condition_result = block_evaluate(loop_condition, None, frame)
        if condition_result is while_type:
            block_evaluate(loop_body, None, frame)
        else:
            break
    
    return universe.nilObject


def _whileFalse(ivkbl, frame, rcvr, args):
    return _whileLoop(frame, rcvr, args, ivkbl.get_universe().falseObject,
                      ivkbl.get_universe())


def _whileTrue(ivkbl, frame, rcvr, args):
    return _whileLoop(frame, rcvr, args, ivkbl.get_universe().trueObject,
                      ivkbl.get_universe())


class BlockPrimitives(Primitives):
    
    def install_primitives(self):        
        self._install_instance_primitive(Primitive("whileTrue:",
                                                   self._universe, _whileTrue))
        self._install_instance_primitive(Primitive("whileFalse:",
                                                   self._universe, _whileFalse))
