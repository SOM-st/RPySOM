from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.double      import Double
from som.vmobjects.integer     import Integer

import math

def _coerce_to_double(obj, universe):
    if isinstance(obj, Double):
        return obj
    if isinstance(obj, Integer):
        return universe.new_double(obj.get_embedded_integer())
    raise ValueError("Cannot coerce %s to Double!" % obj)

def _asString(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_string(str(rcvr.get_embedded_double())))

def _sqrt(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_double(math.sqrt(rcvr.get_embedded_double())))

def _plus(ivkbl, frame, interpreter):
    op1 = _coerce_to_double(frame.pop(), interpreter.get_universe())
    op2 = frame.pop()
    frame.push(interpreter.get_universe().new_double(op1.get_embedded_double()
                                         + op2.get_embedded_double()))

def _minus(ivkbl, frame, interpreter):
    op1 = _coerce_to_double(frame.pop(), interpreter.get_universe())
    op2 = frame.pop()
    frame.push(interpreter.get_universe().new_double(op2.get_embedded_double()
                                         - op1.get_embedded_double()))
def _mult(ivkbl, frame, interpreter):
    op1 = _coerce_to_double(frame.pop(), interpreter.get_universe())
    op2 = frame.pop()
    frame.push(interpreter.get_universe().new_double(op2.get_embedded_double()
                                         * op1.get_embedded_double()))

def _doubleDiv(ivkbl, frame, interpreter):
    op1 = _coerce_to_double(frame.pop(), interpreter.get_universe())
    op2 = frame.pop()
    frame.push(interpreter.get_universe().new_double(op2.get_embedded_double()
                                           / op1.get_embedded_double()))

def _mod(ivkbl, frame, interpreter):
    op1 = _coerce_to_double(frame.pop(), interpreter.get_universe())
    op2 = frame.pop()
    frame.push(interpreter.get_universe().new_double(op2.get_embedded_double()
                                         % op1.get_embedded_double()))

def _equals(ivkbl, frame, interpreter):
    op1 = _coerce_to_double(frame.pop(), interpreter.get_universe())
    op2 = frame.pop()
    if op1.get_embedded_double() == op2.get_embedded_double():
        frame.push(interpreter.get_universe().trueObject)
    else:
        frame.push(interpreter.get_universe().falseObject)

def _lessThan(ivkbl, frame, interpreter):
    op1 = _coerce_to_double(frame.pop(), interpreter.get_universe())
    op2 = frame.pop()
    if op2.get_embedded_double() < op1.get_embedded_double():
        frame.push(interpreter.get_universe().trueObject)
    else:
        frame.push(interpreter.get_universe().falseObject)

class DoublePrimitives(Primitives):

    def install_primitives(self):        
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        self._install_instance_primitive(Primitive("sqrt", self._universe, _sqrt))
        self._install_instance_primitive(Primitive("+",  self._universe, _plus))
        self._install_instance_primitive(Primitive("-",  self._universe, _minus))
        self._install_instance_primitive(Primitive("*",  self._universe, _mult))
        self._install_instance_primitive(Primitive("//", self._universe, _doubleDiv))
        self._install_instance_primitive(Primitive("%",  self._universe, _mod))
        self._install_instance_primitive(Primitive("=",  self._universe, _equals))
        self._install_instance_primitive(Primitive("<",  self._universe, _lessThan))
