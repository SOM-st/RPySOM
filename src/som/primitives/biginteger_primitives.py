from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive
from som.vmobjects.integer     import integer_value_fits
 
import math

def _asString(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_string(str(rcvr.get_embedded_biginteger()))


def _sqrt(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_double(
        math.sqrt(rcvr.get_embedded_biginteger()))


def _plus(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() + right_obj.get_embedded_value()
    if integer_value_fits(result):
        return ivkbl.get_universe().new_integer(result)
    else:
        return ivkbl.get_universe().new_biginteger(result)


def _minus(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() - right_obj.get_embedded_value()
    if integer_value_fits(result):
        return ivkbl.get_universe().new_integer(result)
    else:
        return ivkbl.get_universe().new_biginteger(result)


def _mult(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() * right_obj.get_embedded_value()
    if integer_value_fits(result):
        return ivkbl.get_universe().new_integer(result)
    else:
        return ivkbl.get_universe().new_biginteger(result)


def _div(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation and perform conversion to Integer if required
    result = left.get_embedded_biginteger() / right_obj.get_embedded_value()
    if integer_value_fits(result):
        return ivkbl.get_universe().new_integer(result)
    else:
        return ivkbl.get_universe().new_biginteger(result)


def _mod(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation:
    return ivkbl.get_universe().new_biginteger(left.get_embedded_biginteger()
                                               % right_obj.get_embedded_value())


def _and(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation:
    return ivkbl.get_universe().new_biginteger(left.get_embedded_biginteger()
                                               & right_obj.get_embedded_value())


def _equals(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation:
    if left.get_embedded_biginteger() == right_obj.get_embedded_value():
        return ivkbl.get_universe().trueObject
    else:
        return ivkbl.get_universe().falseObject


def _lessThan(ivkbl, rcvr, args):
    right_obj = args[0]
    left      = rcvr

    # Do operation:
    if left.get_embedded_biginteger() < right_obj.get_embedded_value():
        return ivkbl.get_universe().trueObject
    else:
        return ivkbl.get_universe().falseObject


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
