from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.integer     import integer_value_fits
 
import math

def _asString(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_string(str(rcvr.get_embedded_biginteger())))


def _sqrt(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_double(
                       math.sqrt(rcvr.get_embedded_biginteger())))


def _plus(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() + right_obj.get_embedded_value()
    if integer_value_fits(result):
        frame.push(interpreter.get_universe().new_integer(result))
    else:
        frame.push(interpreter.get_universe().new_biginteger(result))


def _minus(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() - right_obj.get_embedded_value()
    if integer_value_fits(result):
        frame.push(interpreter.get_universe().new_integer(result))
    else:
        frame.push(interpreter.get_universe().new_biginteger(result))


def _mult(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() * right_obj.get_embedded_value()
    if integer_value_fits(result):
        frame.push(interpreter.get_universe().new_integer(result))
    else:
        frame.push(interpreter.get_universe().new_biginteger(result))


def _div(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() / right_obj.get_embedded_value()
    if integer_value_fits(result):
        frame.push(interpreter.get_universe().new_integer(result))
    else:
        frame.push(interpreter.get_universe().new_biginteger(result))


def _mod(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation:
    frame.push(interpreter.get_universe().new_biginteger(left.get_embedded_biginteger() % right_obj.get_embedded_value()))

def _and(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation:
    frame.push(interpreter.get_universe().new_biginteger(left.get_embedded_biginteger() & right_obj.get_embedded_value()))


def _equals(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation:
    if left.get_embedded_biginteger() == right_obj.get_embedded_value():
        frame.push(interpreter.get_universe().trueObject)
    else:
        frame.push(interpreter.get_universe().falseObject)


def _lessThan(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()

    # Do operation:
    if left.get_embedded_biginteger() < right_obj.get_embedded_value():
        frame.push(interpreter.get_universe().trueObject)
    else:
        frame.push(interpreter.get_universe().falseObject)


class BigIntegerPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        self._install_instance_primitive(Primitive("sqrt",     self._universe, _sqrt))
        self._install_instance_primitive(Primitive("+",        self._universe, _plus))
        self._install_instance_primitive(Primitive("-",        self._universe, _minus))
        self._install_instance_primitive(Primitive("*",        self._universe, _mult))
        self._install_instance_primitive(Primitive("/",        self._universe, _div))
        self._install_instance_primitive(Primitive("%",        self._universe, _mod))
        self._install_instance_primitive(Primitive("&",        self._universe, _and))
        self._install_instance_primitive(Primitive("=",        self._universe, _equals))
        self._install_instance_primitive(Primitive("<",        self._universe, _lessThan))
