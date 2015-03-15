from rpython.rlib.rarithmetic import ovfcheck, LONG_BIT
from rpython.rlib.rbigint import rbigint
from rpython.rtyper.lltypesystem import rffi
from rpython.rtyper.lltypesystem import lltype
from som.primitives.primitives import Primitives
from som.vm.globals import nilObject
from som.vmobjects.array import Array
from som.vmobjects.biginteger import BigInteger
from som.vmobjects.primitive   import Primitive
from som.vmobjects.integer     import Integer
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


def _remainder(ivkbl, rcvr, args):
    return rcvr.prim_remainder(args[0], ivkbl.get_universe())


def _and(ivkbl, rcvr, args):
    return rcvr.prim_and(args[0], ivkbl.get_universe())


def _equals(ivkbl, rcvr, args):
    return rcvr.prim_equals(args[0], ivkbl.get_universe())


def _unequals(ivkbl, rcvr, args):
    return rcvr.prim_unequals(args[0], ivkbl.get_universe())


def _lessThan(ivkbl, rcvr, args):
    return rcvr.prim_less_than(args[0], ivkbl.get_universe())


def _lessThanOrEqual(ivkbl, rcvr, args):
    return rcvr.prim_less_than_or_equal(args[0], ivkbl.get_universe())


def _greaterThan(ivkbl, rcvr, args):
    return rcvr.prim_greater_than(args[0], ivkbl.get_universe())


def _fromString(ivkbl, rcvr, args):
    param = args[0]
    
    if not isinstance(param, String):
        return nilObject
    
    int_value = int(param.get_embedded_string())
    return ivkbl.get_universe().new_integer(int_value)


def _leftShift(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    assert isinstance(right_obj, Integer)

    l = left.get_embedded_integer()
    r = right_obj.get_embedded_integer()

    assert isinstance(l, int)
    assert isinstance(r, int)

    try:
        if r >= LONG_BIT:
            raise OverflowError()
        result = ovfcheck(l << r)
        return universe.new_integer(result)
    except OverflowError:
        return universe.new_biginteger(
            rbigint.fromint(l).lshift(r))


def _unsignedRightShift(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr
    universe  = ivkbl.get_universe()

    assert isinstance(right_obj, Integer)

    l = left.get_embedded_integer()
    r = right_obj.get_embedded_integer()

    u_l = rffi.cast(lltype.Unsigned, l)
    u_r = rffi.cast(lltype.Unsigned, r)

    return universe.new_integer(rffi.cast(lltype.Signed, u_l >> u_r))


def _bitXor(ivkbl, rcvr, args):
    right    = args[0]
    left     = rcvr
    universe = ivkbl.get_universe()

    assert isinstance(right, Integer)
    return universe.new_integer(left.get_embedded_integer()
                                ^ right.get_embedded_integer())


def _abs(ivkbl, rcvr, args):
    left     = rcvr
    universe = ivkbl.get_universe()
    return universe.new_integer(abs(left.get_embedded_integer()))


def _as32BitSignedValue(ivkbl, rcvr, args):
    val = rffi.cast(lltype.Signed, rffi.cast(rffi.INT, rcvr.get_embedded_integer()))
    return ivkbl.get_universe().new_integer(val)


def _as32BitUnsignedValue(ivkbl, rcvr, args):
    val = rffi.cast(lltype.Signed, rffi.cast(rffi.UINT, rcvr.get_embedded_integer()))
    return ivkbl.get_universe().new_integer(val)


def _equalsequals(ivkbl, rcvr, args):
    op2 = args[0]
    universe = ivkbl.get_universe()
    if isinstance(op2, Integer) or isinstance(op2, BigInteger):
        return rcvr.prim_equals(op2, universe)
    else:
        return universe.falseObject


def _to(ivkbl, rcvr, args):
    assert isinstance(rcvr, Integer)
    arg = args[0]
    assert isinstance(arg, Integer)
    return Array.from_integers(range(rcvr.get_embedded_integer(),
        arg.get_embedded_integer() + 1))


class IntegerPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("==",  self._universe, _equalsequals))

        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        self._install_instance_primitive(Primitive("sqrt",     self._universe, _sqrt))
        self._install_instance_primitive(Primitive("atRandom", self._universe, _atRandom))
        
        self._install_instance_primitive(Primitive("+",  self._universe, _plus))
        self._install_instance_primitive(Primitive("-",  self._universe, _minus))

        self._install_instance_primitive(Primitive("*",  self._universe, _mult))
        self._install_instance_primitive(Primitive("//", self._universe, _doubleDiv))
        self._install_instance_primitive(Primitive("/",  self._universe, _intDiv))
        self._install_instance_primitive(Primitive("%",  self._universe, _mod))
        self._install_instance_primitive(Primitive("rem:",self._universe, _remainder))
        self._install_instance_primitive(Primitive("&",  self._universe, _and))
        self._install_instance_primitive(Primitive("=",  self._universe, _equals))
        self._install_instance_primitive(Primitive("<",  self._universe, _lessThan))
        self._install_instance_primitive(Primitive("<=", self._universe, _lessThanOrEqual))
        self._install_instance_primitive(Primitive(">",  self._universe, _greaterThan))
        self._install_instance_primitive(Primitive("<>", self._universe, _unequals))

        self._install_instance_primitive(Primitive("<<", self._universe, _leftShift))
        self._install_instance_primitive(Primitive("bitXor:", self._universe, _bitXor))
        self._install_instance_primitive(Primitive(">>>", self._universe, _unsignedRightShift))
        self._install_instance_primitive(Primitive("as32BitSignedValue", self._universe, _as32BitSignedValue))
        self._install_instance_primitive(Primitive("as32BitUnsignedValue", self._universe, _as32BitUnsignedValue))

        self._install_instance_primitive(Primitive("abs", self._universe, _abs))
        self._install_instance_primitive(Primitive("to:", self._universe, _to))

        self._install_class_primitive(Primitive("fromString:", self._universe, _fromString))
