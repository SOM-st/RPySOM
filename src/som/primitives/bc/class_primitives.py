from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import BcPrimitive as Primitive


def _new(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_instance(rcvr))


def _name(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_name())


def _super_class(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_super_class())


def _methods(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_instance_invokables())


def _fields(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_instance_fields())


class ClassPrimitives(Primitives):
    def install_primitives(self):
        self._install_instance_primitive(Primitive("new",        self._universe, _new))
        self._install_instance_primitive(Primitive("name",       self._universe, _name))
        self._install_instance_primitive(Primitive("superclass", self._universe, _super_class))
        self._install_instance_primitive(Primitive("methods",    self._universe, _methods))
        self._install_instance_primitive(Primitive("fields",     self._universe, _fields))
