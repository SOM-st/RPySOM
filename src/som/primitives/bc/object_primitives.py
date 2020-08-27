from rpython.rlib.objectmodel import compute_identity_hash

from som.primitives.primitives import Primitives

from som.vmobjects.object    import Object
from som.vmobjects.primitive import Primitive
from som.vmobjects.array     import Array
from som.vm.globals import trueObject, falseObject


def _equals(ivkbl, frame, interpreter):
    op1 = frame.pop()
    op2 = frame.pop()
    if op1 is op2:
        frame.push(trueObject)
    else:
        frame.push(falseObject)


def _hashcode(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_integer(
        compute_identity_hash(rcvr)))


def _objectSize(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    size = 0

    if isinstance(rcvr, Object):
        size = rcvr.get_number_of_fields()
    elif isinstance(rcvr, Array):
        size = rcvr.get_number_of_indexable_fields()

    frame.push(interpreter.get_universe().new_integer(size))


def _perform(ivkbl, frame, interpreter):
    selector = frame.pop()
    rcvr     = frame.get_stack_element(0)

    invokable = rcvr.get_class(interpreter.get_universe()).lookup_invokable(selector)
    invokable.invoke(frame, interpreter)


def _performInSuperclass(ivkbl, frame, interpreter):
    clazz    = frame.pop()
    selector = frame.pop()
    rcvr     = frame.get_stack_element(0)

    invokable = clazz.lookup_invokable(selector)
    invokable.invoke(frame, interpreter)


def _performWithArguments(ivkbl, frame, interpreter):
    args     = frame.pop()
    selector = frame.pop()
    rcvr     = frame.get_stack_element(0)

    for i in range(0, args.get_number_of_indexable_fields()):
        frame.push(args.get_indexable_field(i))

    invokable = rcvr.get_class(interpreter.get_universe()).lookup_invokable(selector)
    invokable.invoke(frame, interpreter)


def _instVarAt(ivkbl, frame, interpreter):
    idx  = frame.pop()
    rcvr = frame.pop()

    frame.push(rcvr.get_field(idx.get_embedded_integer() - 1))


def _instVarAtPut(ivkbl, frame, interpreter):
    val  = frame.pop()
    idx  = frame.pop()
    rcvr = frame.get_stack_element(0)

    rcvr.set_field(idx.get_embedded_integer() - 1, val)


def _halt(ivkbl, frame, interpreter):
    # noop
    print "BREAKPOINT"

def _class(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.get_class(interpreter.get_universe()))


class ObjectPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("==", self._universe, _equals))
        self._install_instance_primitive(Primitive("hashcode", self._universe, _hashcode))
        self._install_instance_primitive(Primitive("objectSize", self._universe, _objectSize))
        self._install_instance_primitive(Primitive("perform:", self._universe, _perform))
        self._install_instance_primitive(Primitive("perform:inSuperclass:", self._universe, _performInSuperclass))
        self._install_instance_primitive(Primitive("perform:withArguments:", self._universe, _performWithArguments))
        self._install_instance_primitive(Primitive("instVarAt:", self._universe, _instVarAt))
        self._install_instance_primitive(Primitive("instVarAt:put:", self._universe, _instVarAtPut))

        self._install_instance_primitive(Primitive("halt", self._universe, _halt))
        self._install_instance_primitive(Primitive("class", self._universe, _class))

