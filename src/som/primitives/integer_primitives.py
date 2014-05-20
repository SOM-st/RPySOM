from rpython.rlib.rarithmetic import ovfcheck
from rpython.rlib.rbigint import rbigint
from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.biginteger  import BigInteger
from som.vmobjects.integer     import Integer
from som.vmobjects.double      import Double
from som.vmobjects.string      import String

import math


def _asString(ivkbl, rcvr, args):
    return rcvr.prim_as_string(ivkbl.get_universe())


def _sqrt(ivkbl, rcvr, args):
    assert isinstance(rcvr, Integer)
    res = math.sqrt(rcvr.get_embedded_integer())
    if res == float(int(res)):
        return ivkbl.get_universe().new_integer(int(res))
    else:
        return ivkbl.get_universe().new_double(res)


def _atRandom(ivkbl, rcvr, args):
    assert isinstance(rcvr, Integer)
    return ivkbl.get_universe().new_integer(int(
        rcvr.get_embedded_integer() * ivkbl.get_universe().random.random()))


def _plus(ivkbl, rcvr, args):
    return rcvr.prim_add(args[0], ivkbl.get_universe())


def _minus(ivkbl, rcvr, args):
    return rcvr.prim_subtract(args[0], ivkbl.get_universe())


def _mult(ivkbl, rcvr, args):
    return rcvr.prim_multiply(args[0], ivkbl.get_universe())


def _doubleDiv(ivkbl, rcvr, args):
    return rcvr.prim_double_div(args[0], ivkbl.get_universe())


def _intDiv(ivkbl, rcvr, args):
    return rcvr.prim_int_div(args[0], ivkbl.get_universe())


def _mod(ivkbl, rcvr, args):
    return rcvr.prim_modulo(args[0], ivkbl.get_universe())


def _and(ivkbl, rcvr, args):
    return rcvr.prim_and(args[0], ivkbl.get_universe())


def _equals(ivkbl, rcvr, args):
    return rcvr.prim_equals(args[0], ivkbl.get_universe())


def _lessThan(ivkbl, rcvr, args):
    return rcvr.prim_less_than(args[0], ivkbl.get_universe())


def _fromString(ivkbl, rcvr, args):
    param = args[0]
    
    if not isinstance(param, String):
        return ivkbl.get_universe().nilObject
    
    int_value = int(param.get_embedded_string())
    return ivkbl.get_universe().new_integer(int_value)


def _leftShift(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    assert isinstance(right_obj, Integer)

    l = left.get_embedded_integer()
    r = right_obj.get_embedded_integer()
    try:
        result = ovfcheck(l << r)
        return universe.new_integer(result)
    except OverflowError:
        return universe.new_biginteger(
            rbigint.fromint(l).lshift(r))


def _bitXor(ivkbl, rcvr, args):
    right    = args[0]
    left     = rcvr
    universe = ivkbl.get_universe()

    assert isinstance(right, Integer)
    return universe.new_integer(left.get_embedded_integer()
                                ^ right.get_embedded_integer())


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

        self._install_instance_primitive(Primitive("<<", self._universe, _leftShift))
        self._install_instance_primitive(Primitive("bitXor:", self._universe, _bitXor))

        self._install_class_primitive(Primitive("fromString:", self._universe, _fromString))
