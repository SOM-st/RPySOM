from rpython.rlib.rarithmetic import ovfcheck, LONG_BIT
from rpython.rlib.rbigint import rbigint
from rpython.rtyper.lltypesystem import rffi
from rpython.rtyper.lltypesystem import lltype
from som.primitives.primitives import Primitives
from som.vm.globals import nilObject, falseObject
from som.vmobjects.array_strategy import Array
from som.vmobjects.biginteger import BigInteger
from som.vmobjects.double import Double
from som.vmobjects.primitive import Primitive, BinaryPrimitive, UnaryPrimitive
from som.vmobjects.integer     import Integer
from som.vmobjects.string      import String

import math


def _as_string(rcvr):
    return rcvr.prim_as_string()


def _sqrt(rcvr):
    assert isinstance(rcvr, Integer)
    res = math.sqrt(rcvr.get_embedded_integer())
    if res == float(int(res)):
        return Integer(int(res))
    else:
        return Double(res)


def _at_random(ivkbl, rcvr, args):
    assert isinstance(rcvr, Integer)
    return Integer(int(
        rcvr.get_embedded_integer() * ivkbl.get_universe().random.random()))


def _plus(rcvr, arg):
    return rcvr.prim_add(arg)


def _minus(rcvr, arg):
    return rcvr.prim_subtract(arg)


def _mult(rcvr, arg):
    return rcvr.prim_multiply(arg)


def _double_div(rcvr, arg):
    return rcvr.prim_double_div(arg)


def _int_div(rcvr, arg):
    return rcvr.prim_int_div(arg)


def _mod(rcvr, arg):
    return rcvr.prim_modulo(arg)


def _remainder(rcvr, arg):
    return rcvr.prim_remainder(arg)


def _and(rcvr, arg):
    return rcvr.prim_and(arg)


def _equals(rcvr, arg):
    return rcvr.prim_equals(arg)


def _unequals(rcvr, arg):
    return rcvr.prim_unequals(arg)


def _less_than(rcvr, arg):
    return rcvr.prim_less_than(arg)


def _less_than_or_equal(rcvr, arg):
    return rcvr.prim_less_than_or_equal(arg)


def _greater_than(rcvr, arg):
    return rcvr.prim_greater_than(arg)


def _from_string(rcvr, param):
    if not isinstance(param, String):
        return nilObject

    int_value = int(param.get_embedded_string())
    return Integer(int_value)


def _left_shift(left, right):
    assert isinstance(right, Integer)

    l = left.get_embedded_integer()
    r = right.get_embedded_integer()

    assert isinstance(l, int)
    assert isinstance(r, int)

    try:
        if r >= LONG_BIT:
            raise OverflowError()
        result = ovfcheck(l << r)
        return Integer(result)
    except OverflowError:
        return BigInteger(
            rbigint.fromint(l).lshift(r))


def _unsigned_right_shift(left, right):
    assert isinstance(right, Integer)

    l = left.get_embedded_integer()
    r = right.get_embedded_integer()

    u_l = rffi.cast(lltype.Unsigned, l)
    u_r = rffi.cast(lltype.Unsigned, r)

    return Integer(rffi.cast(lltype.Signed, u_l >> u_r))


def _bit_xor(left, right):
    assert isinstance(right, Integer)
    return Integer(left.get_embedded_integer() ^ right.get_embedded_integer())


def _abs(rcvr):
    return Integer(abs(rcvr.get_embedded_integer()))


def _as_32_bit_signed_value(rcvr):
    val = rffi.cast(lltype.Signed, rffi.cast(rffi.INT, rcvr.get_embedded_integer()))
    return Integer(val)


def _as_32_bit_unsigned_value(rcvr):
    val = rffi.cast(lltype.Signed, rffi.cast(rffi.UINT, rcvr.get_embedded_integer()))
    return Integer(val)


def _equals_equals(rcvr, op2):
    if isinstance(op2, Integer) or isinstance(op2, BigInteger):
        return rcvr.prim_equals(op2)
    else:
        return falseObject


def _to(rcvr, arg):
    assert isinstance(rcvr, Integer)
    assert isinstance(arg, Integer)
    return Array.from_integers(range(rcvr.get_embedded_integer(), arg.get_embedded_integer() + 1))


def _max(rcvr, arg):
    assert isinstance(rcvr, Integer)
    assert isinstance(arg, Integer)
    return Integer(
        max(rcvr.get_embedded_integer(), arg.get_embedded_integer()))


class IntegerPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(BinaryPrimitive("==",  self._universe, _equals_equals))

        self._install_instance_primitive(UnaryPrimitive("asString", self._universe, _as_string))
        self._install_instance_primitive(UnaryPrimitive("sqrt",     self._universe, _sqrt))
        self._install_instance_primitive(Primitive("atRandom", self._universe, _at_random))

        self._install_instance_primitive(BinaryPrimitive("+",  self._universe, _plus))
        self._install_instance_primitive(BinaryPrimitive("-",  self._universe, _minus))

        self._install_instance_primitive(BinaryPrimitive("*",  self._universe, _mult))
        self._install_instance_primitive(BinaryPrimitive("//", self._universe, _double_div))
        self._install_instance_primitive(BinaryPrimitive("/",  self._universe, _int_div))
        self._install_instance_primitive(BinaryPrimitive("%",  self._universe, _mod))
        self._install_instance_primitive(BinaryPrimitive("rem:", self._universe, _remainder))
        self._install_instance_primitive(BinaryPrimitive("&",  self._universe, _and))
        self._install_instance_primitive(BinaryPrimitive("=",  self._universe, _equals))
        self._install_instance_primitive(BinaryPrimitive("<",  self._universe, _less_than))
        self._install_instance_primitive(BinaryPrimitive("<=", self._universe, _less_than_or_equal))
        self._install_instance_primitive(BinaryPrimitive(">",  self._universe, _greater_than))
        self._install_instance_primitive(BinaryPrimitive("<>", self._universe, _unequals))
        self._install_instance_primitive(BinaryPrimitive("~=", self._universe, _unequals))

        self._install_instance_primitive(BinaryPrimitive("<<", self._universe, _left_shift))
        self._install_instance_primitive(BinaryPrimitive("bitXor:", self._universe, _bit_xor))
        self._install_instance_primitive(BinaryPrimitive(">>>", self._universe, _unsigned_right_shift))
        self._install_instance_primitive(UnaryPrimitive("as32BitSignedValue", self._universe, _as_32_bit_signed_value))
        self._install_instance_primitive(UnaryPrimitive("as32BitUnsignedValue", self._universe, _as_32_bit_unsigned_value))

        self._install_instance_primitive(BinaryPrimitive("max:", self._universe, _max))
        self._install_instance_primitive(UnaryPrimitive("abs", self._universe, _abs))
        self._install_instance_primitive(BinaryPrimitive("to:", self._universe, _to))

        self._install_class_primitive(BinaryPrimitive("fromString:", self._universe, _from_string))
