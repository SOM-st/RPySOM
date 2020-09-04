from som.primitives.primitives import Primitives
from som.vm.globals import nilObject, falseObject, trueObject
from som.vmobjects.primitive   import Primitive

from som.vm.universe import std_print, std_println

from rpython.rlib import rgc, jit
import time


def _load(ivkbl, rcvr, args):
    argument = args[0]
    result = ivkbl.get_universe().load_class(argument)
    return result if result else nilObject


def _exit(ivkbl, rcvr, args):
    error = args[0]
    return ivkbl.get_universe().exit(error.get_embedded_integer())


def _global(ivkbl, rcvr, args):
    argument = args[0]
    result = ivkbl.get_universe().get_global(argument)
    return result if result else nilObject


def _has_global(ivkbl, rcvr, args):
    if ivkbl.get_universe().has_global(args[0]):
        return trueObject
    else:
        return falseObject


def _global_put(ivkbl, rcvr, args):
    value    = args[1]
    argument = args[0]
    ivkbl.get_universe().set_global(argument, value)
    return value


def _print_string(ivkbl, rcvr, args):
    argument = args[0]
    std_print(argument.get_embedded_string())
    return rcvr


def _print_newline(ivkbl, rcvr, args):
    std_println()
    return rcvr


def _time(ivkbl, rcvr, args):
    from som.vmobjects.integer import Integer
    since_start = time.time() - ivkbl.get_universe().start_time
    return Integer(int(since_start * 1000))


def _ticks(ivkbl, rcvr, args):
    from som.vmobjects.integer import Integer
    since_start = time.time() - ivkbl.get_universe().start_time
    return Integer(int(since_start * 1000000))


@jit.dont_look_inside
def _fullGC(ivkbl, rcvr, args):
    rgc.collect()
    return trueObject


class SystemPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("load:", self._universe, _load))
        self._install_instance_primitive(Primitive("exit:", self._universe, _exit))
        self._install_instance_primitive(Primitive("hasGlobal:", self._universe, _has_global))
        self._install_instance_primitive(Primitive("global:", self._universe, _global))
        self._install_instance_primitive(Primitive("global:put:", self._universe, _global_put))
        self._install_instance_primitive(Primitive("printString:", self._universe, _print_string))
        self._install_instance_primitive(Primitive("printNewline", self._universe, _print_newline))
        self._install_instance_primitive(Primitive("time", self._universe, _time))
        self._install_instance_primitive(Primitive("ticks", self._universe, _ticks))
        self._install_instance_primitive(Primitive("fullGC", self._universe, _fullGC))
