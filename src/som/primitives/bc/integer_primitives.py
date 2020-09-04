from rpython.rlib.rarithmetic import ovfcheck, LONG_BIT
from rpython.rlib.rbigint import rbigint
from rpython.rtyper.lltypesystem import rffi
from rpython.rtyper.lltypesystem import lltype
from rpython.rlib import jit

from som.primitives.primitives import Primitives
from som.vm.universe import Universe
from som.vmobjects.integer     import Integer
from som.vmobjects.primitive   import Primitive, UnaryPrimitive, BinaryPrimitive
from som.vmobjects.double      import Double
from som.vmobjects.string      import String
from som.vmobjects.block_bc import block_evaluate, BcBlock
from som.vm.globals import nilObject, falseObject

import math


def _as_string(rcvr):
    return rcvr.prim_as_string()


def _as_32bit_signed_value(rcvr):
    val = rffi.cast(lltype.Signed, rffi.cast(rffi.INT, rcvr.get_embedded_integer()))
    return Integer(val)


def _as_32bit_unsigned_value(rcvr):
    val = rffi.cast(lltype.Signed, rffi.cast(rffi.UINT, rcvr.get_embedded_integer()))
    return Integer(val)


def _sqrt(rcvr):
    res = math.sqrt(rcvr.get_embedded_integer())
    if res == float(int(res)):
        return Integer(int(res))
    else:
        return Double(res)


def _at_random(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(Integer(int(
        rcvr.get_embedded_integer() * interpreter.get_universe().random.random())))


def _plus(left, right):
    return left.prim_add(right)


def _minus(left, right):
    return left.prim_subtract(right)


def _mult(left, right):
    return left.prim_multiply(right)


def _double_div(left, right):
    return left.prim_double_div(right)


def _int_div(left, right):
    return left.prim_int_div(right)


def _mod(left, right):
    return left.prim_modulo(right)


def _remainder(left, right):
    return left.prim_remainder(right)


def _and(left, right):
    return left.prim_and(right)


def _equals_equals(left, right):
    if isinstance(right, Integer):
        return left.prim_equals(right)
    else:
        return falseObject


def _equals(left, right):
    return left.prim_equals(right)


def _unequals(left, right):
    return left.prim_unequals(right)


def _less_than(left, right):
    return left.prim_less_than(right)


def _less_than_or_equal(left, right):
    return left.prim_less_than_or_equal(right)


def _greater_than(left, right):
    return left.prim_greater_than(right)


def _from_string(rcvr, param):
    if not isinstance(param, String):
        return nilObject

    int_value = int(param.get_embedded_string())
    return Integer(int_value)


def _left_shift(left, right):
    assert isinstance(right, Integer)

    l = left.get_embedded_integer()
    r = right.get_embedded_integer()
    try:
        if not (l == 0 or 0 <= r < LONG_BIT):
            raise OverflowError
        result = ovfcheck(l << r)
        return Integer(result)
    except OverflowError:
        from som.vmobjects.biginteger import BigInteger
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
    result = left.get_embedded_integer() ^ right.get_embedded_integer()
    return Integer(result)


def _abs(rcvr):
    return Integer(abs(rcvr.get_embedded_integer()))


def _max(left, right):
    assert isinstance(left, Integer)
    assert isinstance(right, Integer)
    return Integer(
        max(left.get_embedded_integer(), right.get_embedded_integer()))


def get_printable_location(interpreter, block_method):
    from som.vmobjects.method_bc import BcMethod
    assert isinstance(block_method, BcMethod)
    return "to:do: [%s>>%s]" % (block_method.get_holder().get_name().get_embedded_string(),
                                block_method.get_signature().get_embedded_string())


jitdriver_int = jit.JitDriver(
    name='to:do: with int',
    greens=['interpreter', 'block_method'],
    reds='auto',
    # virtualizables=['frame'],
    is_recursive=True,
    get_printable_location=get_printable_location)

jitdriver_double = jit.JitDriver(
    name='to:do: with double',
    greens=['interpreter', 'block_method'],
    reds='auto',
    # virtualizables=['frame'],
    is_recursive=True,
    get_printable_location=get_printable_location)


def _to_do_int(i, by_increment, top, frame, context, interpreter, block_method):
    assert isinstance(i, int)
    assert isinstance(top, int)
    while i <= top:
        jitdriver_int.jit_merge_point(interpreter=interpreter,
                                      block_method=block_method)

        b = BcBlock(block_method, context)
        frame.push(b)
        frame.push(Integer(i))
        block_evaluate(b, interpreter, frame)
        frame.pop()
        i += by_increment


def _to_do_double(i, by_increment, top, frame, context, interpreter, block_method):
    assert isinstance(i, int)
    assert isinstance(top, float)
    while i <= top:
        jitdriver_double.jit_merge_point(interpreter=interpreter,
                                         block_method=block_method)

        b = BcBlock(block_method, context)
        frame.push(b)
        frame.push(Integer(i))
        block_evaluate(b, interpreter, frame)
        frame.pop()
        i += by_increment


def _to_do(ivkbl, frame, interpreter):
    block = frame.pop()
    limit = frame.pop()
    self  = frame.pop()  # we do leave it on there

    block_method = block.get_method()
    context      = block.get_context()

    i = self.get_embedded_integer()
    if isinstance(limit, Double):
        _to_do_double(i, 1, limit.get_embedded_double(), frame, context, interpreter,
                      block_method)
    else:
        _to_do_int(i, 1, limit.get_embedded_integer(), frame, context, interpreter,
                   block_method)

    frame.push(self)


def _to_by_do(ivkbl, frame, interpreter):
    block = frame.pop()
    by_increment = frame.pop()
    limit = frame.pop()
    self  = frame.pop()  # we do leave it on there

    block_method = block.get_method()
    context      = block.get_context()

    i = self.get_embedded_integer()
    if isinstance(limit, Double):
        _to_do_double(i, by_increment.get_embedded_integer(), limit.get_embedded_double(), frame, context, interpreter,
                      block_method)
    else:
        _to_do_int(i, by_increment.get_embedded_integer(), limit.get_embedded_integer(), frame, context, interpreter,
                   block_method)

    frame.push(self)


class IntegerPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(BinaryPrimitive("==", self._universe, _equals_equals))

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
        self._install_instance_primitive(
            UnaryPrimitive("as32BitSignedValue", self._universe, _as_32bit_signed_value))
        self._install_instance_primitive(
            UnaryPrimitive("as32BitUnsignedValue", self._universe, _as_32bit_unsigned_value))

        self._install_instance_primitive(BinaryPrimitive("max:", self._universe, _max))
        self._install_instance_primitive(UnaryPrimitive("abs", self._universe, _abs))

        self._install_instance_primitive(Primitive("to:do:", self._universe, _to_do))
        self._install_instance_primitive(Primitive("to:by:do:", self._universe, _to_by_do))

        self._install_class_primitive(BinaryPrimitive("fromString:", self._universe, _from_string))
