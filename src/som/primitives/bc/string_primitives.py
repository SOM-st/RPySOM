from rpython.rlib.objectmodel import compute_hash

from som.primitives.primitives import Primitives
from som.vmobjects.primitive import Primitive
from som.vm.globals import trueObject, falseObject
from som.vmobjects.string import String
from som.vmobjects.symbol import Symbol


def _concat(ivkbl, frame, interpreter):
    argument = frame.pop()
    rcvr     = frame.pop()
    frame.push(interpreter.get_universe().new_string(rcvr.get_embedded_string()
                                           + argument.get_embedded_string()))


def _asSymbol(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().symbol_for(rcvr.get_embedded_string()))


def _length(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_integer(len(rcvr.get_embedded_string())))


def _equals(ivkbl, frame, interpreter):
    op1 = frame.pop()
    op2 = frame.pop()  # rcvr

    if isinstance(op1, String):
        if isinstance(op1, Symbol) and isinstance(op2, Symbol):
            if op1 is op2:
                frame.push(trueObject)
            else:
                frame.push(falseObject)
            return
        if isinstance(op2, String):
            if op1.get_embedded_string() == op2.get_embedded_string():
                frame.push(trueObject)
                return

    frame.push(falseObject)


def _substring(ivkbl, frame, interpreter):
    end   = frame.pop()
    start = frame.pop()
    rcvr  = frame.pop()

    s      = start.get_embedded_integer() - 1
    e      = end.get_embedded_integer()
    string = rcvr.get_embedded_string()

    if s < 0 or s >= len(string) or e > len(string) or e < s:
        frame.push(interpreter.get_universe().new_string("Error - index out of bounds"))
    else:
        frame.push(interpreter.get_universe().new_string(string[s:e]))


def _hashcode(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_integer(
        compute_hash(rcvr.get_embedded_string())))


def _is_whitespace(ivkbl, frame, interpreter):
    self = frame.pop()
    s = self.get_embedded_string()

    for c in s:
        if not c.isspace():
            frame.push(falseObject)
            return

    if len(s) > 0:
        frame.push(trueObject)
    else:
        frame.push(falseObject)


def _is_letters(ivkbl, frame, interpreter):
    self = frame.pop()
    s = self.get_embedded_string()

    for c in s:
        if not c.isalpha():
            frame.push(falseObject)
            return

    if len(s) > 0:
        frame.push(trueObject)
    else:
        frame.push(falseObject)


def _is_digits(ivkbl, frame, interpreter):
    self = frame.pop()
    s = self.get_embedded_string()

    for c in s:
        if not c.isdigit():
            frame.push(falseObject)
            return

    if len(s) > 0:
        frame.push(trueObject)
    else:
        frame.push(falseObject)


class StringPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("concatenate:",          self._universe, _concat))
        self._install_instance_primitive(Primitive("asSymbol",              self._universe, _asSymbol))
        self._install_instance_primitive(Primitive("length",                self._universe, _length))
        self._install_instance_primitive(Primitive("=",                     self._universe, _equals))
        self._install_instance_primitive(Primitive("primSubstringFrom:to:", self._universe, _substring))
        self._install_instance_primitive(Primitive("hashcode",              self._universe, _hashcode))

        self._install_instance_primitive(Primitive("isWhiteSpace", self._universe, _is_whitespace))
        self._install_instance_primitive(Primitive("isLetters", self._universe, _is_letters))
        self._install_instance_primitive(Primitive("isDigits", self._universe, _is_digits))
