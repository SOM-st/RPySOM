from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.biginteger  import BigInteger
from som.vmobjects.integer     import integer_value_fits, Integer
from som.vmobjects.double      import Double
from som.vmobjects.string      import String

import math


def _long_result(result, universe):
    # Check with integer bounds and push:
    if integer_value_fits(result):
        return universe.new_integer(int(result))
    else:
        return universe.new_biginteger(result)


def _resend_as_biginteger(operator, left, right, universe):
    left_biginteger = universe.new_biginteger(left.get_embedded_integer())
    operands = [right]
    return left_biginteger.send(operator, operands, universe)


def _resend_as_double(operator, left, right, universe):
    left_double = universe.new_double(left.get_embedded_integer())
    operands    = [right]
    return left_double.send(operator, operands, universe)


def _asString(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_string(str(rcvr.get_embedded_integer()))


def _sqrt(ivkbl, rcvr, args):
    res = math.sqrt(rcvr.get_embedded_integer())
    if res == float(int(res)):
        return ivkbl.get_universe().new_integer(int(res))
    else:
        return ivkbl.get_universe().new_double(res)


def _atRandom(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_integer(int(
        rcvr.get_embedded_integer() * ivkbl.get_universe().random.random()))

def _plus(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("+", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("+", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() + right.get_embedded_integer()
        return _long_result(result, universe)


def _minus(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("-", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("-", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() - right.get_embedded_integer()
        return _long_result(result, universe)

def _mult(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("*", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("*", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() * right.get_embedded_integer()
        return _long_result(result, universe)


def _doubleDiv(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("/", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("/", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = float(left.get_embedded_integer()) / float(right.get_embedded_integer())
        return universe.new_double(result)


def _intDiv(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("/", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("/", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() / right.get_embedded_integer()
        return _long_result(result, universe)


def _mod(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        _resend_as_biginteger("%", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("%", left, right_obj, universe)
    else:
        # Do operation:
        return _long_result(left.get_embedded_integer()
                                   % right_obj.get_embedded_integer(), universe)

def _and(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("&", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("&", left, right_obj, universe)
    else:
        # Do operation:
        right = right_obj
        result = left.get_embedded_integer() & right.get_embedded_integer()
        return _long_result(result, universe)


def _equals(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()
    
    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("=", left, right_obj, universe)
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


def _lessThan(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()
    
    # Check second parameter type:
    if isinstance(right_obj, BigInteger):
        # Second operand was BigInteger
        return _resend_as_biginteger("<", left, right_obj, universe)
    elif isinstance(right_obj, Double):
        return _resend_as_double("<", left, right_obj, universe)
    else:
        if left.get_embedded_integer() < right_obj.get_embedded_integer():
            return universe.trueObject
        else:
            return universe.falseObject


def _fromString(ivkbl, rcvr, args):
    param = args[0]
    
    if not isinstance(param, String):
        return ivkbl.get_universe().nilObject
    
    int_value = int(param.get_embedded_string())
    return ivkbl.get_universe().new_integer(int_value)


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

        self._install_class_primitive(Primitive("fromString:", self._universe, _fromString))
