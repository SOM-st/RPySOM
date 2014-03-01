from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.biginteger  import BigInteger
from som.vmobjects.integer     import integer_value_fits, Integer
from som.vmobjects.double      import Double
from som.vmobjects.string      import String
from som.vmobjects.block       import block_evaluate

import math


def _long_result(frame, result, universe):
    # Check with integer bounds and push:
    if integer_value_fits(result):
        return universe.new_integer(int(result))
    else:
        return universe.new_biginteger(result)


def _resend_as_biginteger(frame, operator, left, right, universe):
    left_biginteger = universe.new_biginteger(left.get_embedded_integer())
    operands = [right]
    return left_biginteger.send(frame, operator, operands, universe, universe.get_interpreter())


def _resend_as_double(frame, operator, left, right, universe):
    left_double = universe.new_double(left.get_embedded_integer())
    operands    = [right]
    return left_double.send(frame, operator, operands, universe, universe.get_interpreter())


def _asString(ivkbl, frame, rcvr, args):
    return ivkbl.get_universe().new_string(str(rcvr.get_embedded_integer()))


def _sqrt(ivkbl, frame, rcvr, args):
    res = math.sqrt(rcvr.get_embedded_integer())
    if res == float(int(res)):
        return ivkbl.get_universe().new_integer(int(res))
    else:
        return ivkbl.get_universe().new_double(res)


def _atRandom(ivkbl, frame, rcvr, args):
    return ivkbl.get_universe().new_integer(int(
        rcvr.get_embedded_integer() * ivkbl.get_universe().random.random()))

def _plus(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "+", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "+", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() + right.get_embedded_integer()
        return _long_result(frame, result, universe)


def _minus(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "-", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "-", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() - right.get_embedded_integer()
        return _long_result(frame, result, universe)

def _mult(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "*", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "*", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() * right.get_embedded_integer()
        return _long_result(frame, result, universe)


def _doubleDiv(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "/", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "/", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = float(left.get_embedded_integer()) / float(right.get_embedded_integer())
        return universe.new_double(result)


def _intDiv(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "/", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "/", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() / right.get_embedded_integer()
        return _long_result(frame, result, universe)


def _mod(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger(frame, "%", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "%", left, right_obj, universe)
    else:
        # Do operation:
        return _long_result(frame, left.get_embedded_integer()
                                   % right_obj.get_embedded_integer(), universe)

def _and(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "&", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "&", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() & right.get_embedded_integer()
        return _long_result(frame, result, universe)


def _equals(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()
    
    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "=", left, right_obj, universe)
    elif isinstance(right_obj, Integer):
        if left.get_embedded_integer() == right_obj.get_embedded_integer():
            return universe.trueObject
        else:
            return universe.falseObject
    elif isinstance(right_obj, Double):
        if left.get_embedded_integer() == right_obj.get_embedded_double():
            return universe.trueObject
        else:
            return universe.falseObject
    else:
        return universe.falseObject


def _lessThan(ivkbl, frame, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()
    
    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger(frame, "<", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double(frame, "<", left, right_obj, universe)
    else:
        if left.get_embedded_integer() < right_obj.get_embedded_integer():
            return universe.trueObject
        else:
            return universe.falseObject


def _fromString(ivkbl, frame, rcvr, args):
    param = args[0]
    
    if not isinstance(param, String):
        return ivkbl.get_universe().nilObject
    
    int_value = int(param.get_embedded_string())
    return ivkbl.get_universe().new_integer(int_value)


from rpython.rlib import jit


def get_printable_location(interpreter, block_method):
    from som.vmobjects.method import Method
    assert isinstance(block_method, Method)
    return "TODO"


jitdriver = jit.JitDriver(
    greens=['interpreter', 'block_method'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


def _toDo(ivkbl, frame, rcvr, args):
    universe = ivkbl.get_universe()
    block = frame.pop()
    limit = frame.pop()
    self  = frame.pop() # we do leave it on there

    block_method = block.get_method()
    context      = block.get_context()

    i = self.get_embedded_integer()
    if isinstance(limit, Double):
        top = limit.get_embedded_double()
    else:
        top = limit.get_embedded_value()
    while i <= top:
        jitdriver.jit_merge_point(interpreter=interpreter,
                                  block_method=block_method)

        b = universe.new_block(block_method, context)
        frame.push(b)
        frame.push(universe.new_integer(i))
        block_evaluate(b, interpreter, frame)
        frame.pop()
        i += 1

    frame.push(self)


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
        
        self._install_instance_primitive(Primitive("to:do:", self._universe, _toDo))
        
        self._install_class_primitive(Primitive("fromString:", self._universe, _fromString))
