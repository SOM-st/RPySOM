from rpython.rlib.rfloat import round_double, INFINITY
from math import cos, sin

from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import BcPrimitive as Primitive

import math


def _as_string(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.prim_as_string(interpreter.get_universe()))


def _sqrt(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_double(math.sqrt(
        rcvr.get_embedded_double())))


def _plus(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_add(right, interpreter.get_universe()))


def _minus(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_subtract(right, interpreter.get_universe()))


def _mult(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_multiply(right, interpreter.get_universe()))


def _double_div(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_double_div(right, interpreter.get_universe()))


def _mod(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_modulo(right, interpreter.get_universe()))


def _equals(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_equals(right))


def _less_than(ivkbl, frame, interpreter):
    right = frame.pop()
    rcvr  = frame.pop()
    frame.push(rcvr.prim_less_than(right, interpreter.get_universe()))


def _round(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    int_value = int(round_double(rcvr.get_embedded_double(), 0))
    frame.push(interpreter.get_universe().new_integer(int_value))


def _as_integer(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    int_value = int(rcvr.get_embedded_double())
    frame.push(interpreter.get_universe().new_integer(int_value))


def _cos(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    result = cos(rcvr.get_embedded_double())
    frame.push(interpreter.get_universe().new_double(result))


def _sin(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    result = sin(rcvr.get_embedded_double())
    frame.push(interpreter.get_universe().new_double(result))


def _infinity(ivkbl, frame, interpreter):
    frame.pop()  # self not required
    frame.push(interpreter.get_universe().new_double(INFINITY))


class DoublePrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe, _as_string))
        self._install_instance_primitive(Primitive("round",    self._universe, _round))
        self._install_instance_primitive(Primitive("asInteger", self._universe, _as_integer))
        self._install_instance_primitive(Primitive("sqrt", self._universe, _sqrt))
        self._install_instance_primitive(Primitive("+",  self._universe, _plus))
        self._install_instance_primitive(Primitive("-",  self._universe, _minus))
        self._install_instance_primitive(Primitive("*",  self._universe, _mult))
        self._install_instance_primitive(Primitive("//", self._universe, _double_div))
        self._install_instance_primitive(Primitive("%",  self._universe, _mod))
        self._install_instance_primitive(Primitive("=",  self._universe, _equals))
        self._install_instance_primitive(Primitive("<",  self._universe, _less_than))
        self._install_instance_primitive(Primitive("sin", self._universe, _sin))
        self._install_instance_primitive(Primitive("cos", self._universe, _cos))

        self._install_class_primitive(Primitive("PositiveInfinity", self._universe, _infinity))
