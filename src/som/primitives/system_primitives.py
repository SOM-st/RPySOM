from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive

from som.vm.universe import std_print, std_println

import time

_start_time = time.time() # a float of the time in seconds

def _load(ivkbl, frame, interpreter):
    argument = frame.pop()
    frame.pop() # not required
    result = interpreter.get_universe().load_class(argument)
    frame.push(result if result else interpreter.get_universe().nilObject)

def _exit(ivkbl, frame, interpreter):
    error = frame.pop()
    interpreter.get_universe().exit(error.get_embedded_integer())

def _global(ivkbl, frame, interpreter):
    argument = frame.pop()
    frame.pop() # not required
    result = interpreter.get_universe().get_global(argument)
    frame.push(result if result else interpreter.get_universe().nilObject)

def _global_put(ivkbl, frame, interpreter):
    value    = frame.pop()
    argument = frame.pop()
    interpreter.get_universe().set_global(argument, value)

def _print_string(ivkbl, frame, interpreter):
    argument = frame.pop()
    std_print(argument.get_embedded_string())

def _print_newline(ivkbl, frame, interpreter):
    std_println()

def _time(ivkbl, frame, interpreter):
    frame.pop() # ignore
    _time = time.time() - _start_time
    frame.push(interpreter.get_universe().new_integer(_time * 1000))

def _ticks(ivkbl, frame, interpreter):
    frame.pop() # ignore
    _time = time.time() - _start_time
    frame.push(interpreter.get_universe().new_integer(_time * 1000000))

def _fullGC(ivkbl, frame, interpreter):
    # naught - GC is entirely left to Python
    pass

class SystemPrimitives(Primitives):
    
    def install_primitives(self):
        self._install_instance_primitive(Primitive("load:", self._universe, _load))
        self._install_instance_primitive(Primitive("exit:", self._universe, _exit))
        self._install_instance_primitive(Primitive("global:", self._universe, _global))
        self._install_instance_primitive(Primitive("global:put:", self._universe, _global_put))
        self._install_instance_primitive(Primitive("printString:", self._universe, _print_string))
        self._install_instance_primitive(Primitive("printNewline", self._universe, _print_newline))
        self._install_instance_primitive(Primitive("time", self._universe, _time))
        self._install_instance_primitive(Primitive("ticks", self._universe, _ticks))
        self._install_instance_primitive(Primitive("fullGC", self._universe, _fullGC))
