from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.biginteger  import BigInteger
from som.vmobjects.integer     import integer_value_fits, Integer
from som.vmobjects.double      import Double

import math

def _push_long_result(frame, result, universe):
    # Check with integer bounds and push:
    if integer_value_fits(result):
        frame.push(universe.new_integer(result))
    else:
        frame.push(universe.new_biginteger(result))

def _resend_as_biginteger(operator, left, right, universe):
    left_biginteger = universe.new_biginteger(left.get_embedded_integer())
    operands = [right]
    left_biginteger.send(operator, operands, universe, universe.get_interpreter())

def _resend_as_double(operator, left, right, universe):
    left_double = universe.new_double(left.get_embedded_integer())
    operands    = [right]
    left_double.send(operator, operands, universe, universe.get_interpreter())

def _asString(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_string(str(rcvr.get_embedded_integer())))

def _sqrt(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_double(math.sqrt(rcvr.get_embedded_integer())))

def _atRandom(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.universe().new_integer(int(
        rcvr.get_embedded_integer() * interpreter.universe().random.random())))

def _plus(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("+", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("+", left, right_obj, interpreter.get_universe())
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() + right.get_embedded_integer()
        _push_long_result(frame, result, interpreter.get_universe())

def _minus(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("-", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("-", left, right_obj, interpreter.get_universe())
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() - right.get_embedded_integer()
        _push_long_result(frame, result, interpreter.get_universe())

def _mult(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("*", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("*", left, right_obj, interpreter.get_universe())
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() * right.get_embedded_integer()
        _push_long_result(frame, result, interpreter.get_universe())

def _doubleDiv(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("/", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("/", left, right_obj, interpreter.get_universe())
    else:
        # Do operation:
        right = right_obj
        result = float(left.get_embedded_integer()) / float(right.get_embedded_integer())
        frame.push(interpreter.get_universe().new_double(result))

def _intDiv(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("/", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("/", left, right_obj, interpreter.get_universe())
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() / right.get_embedded_integer()
        _push_long_result(frame, result, interpreter.get_universe())

def _mod(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("%", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("%", left, right_obj, interpreter.get_universe())
    else:
        # Do operation:
        _push_long_result(frame, left.get_embedded_integer() % right_obj.get_embedded_integer(), interpreter.get_universe())

def _and(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("&", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("&", left, right_obj, interpreter.get_universe())
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() & right.get_embedded_integer()
        _push_long_result(frame, result, interpreter.get_universe())


def _equals(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    
    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("=", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Integer):
        if left.get_embedded_integer() == right_obj.get_embedded_integer():
            frame.push(interpreter.get_universe().trueObject)
        else:
            frame.push(interpreter.get_universe().falseObject)
    elif isinstance(right_obj, Double):
        if left.get_embedded_integer() == right_obj.get_embedded_double():
            frame.push(interpreter.get_universe().trueObject)
        else:
            frame.push(interpreter.get_universe().falseObject)
    else:
        frame.push(interpreter.get_universe().falseObject)

def _lessThan(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    
    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("<", left, right_obj, interpreter.get_universe())
    elif isinstance(right_obj, Double):
        _resend_as_double("<", left, right_obj, interpreter.get_universe())
    else:
        if left.get_embedded_integer() < right_obj.get_embedded_integer():
            frame.push(interpreter.get_universe().trueObject)
        else:
            frame.push(interpreter.get_universe().falseObject)

class IntegerPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        self._install_instance_primitive(Primitive("sqrt",     self._universe, _sqrt))
        self._install_instance_primitive(Primitive("atRandom", self._universe, _atRandom))
        
        self._install_instance_primitive(Primitive("+",  self._universe, _plus))
        self._install_instance_primitive(Primitive("-",  self._universe, _minus))

        self._install_instance_primitive(Primitive("*",  self._universe, _mult))
        self._install_instance_primitive(Primitive("//", self._universe, _doubleDiv))
        self._install_instance_primitive(Primitive("/",  self._universe, _intDiv))
        self._install_instance_primitive(Primitive("%",  self._universe, _mod))
        self._install_instance_primitive(Primitive("&",  self._universe, _and))
        self._install_instance_primitive(Primitive("=",  self._universe, _equals))
        self._install_instance_primitive(Primitive("<",  self._universe, _lessThan))
        