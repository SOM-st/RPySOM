from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive


def _asString(ivkbl, rcvr, args):
    return ivkbl.get_universe().new_string(rcvr.get_embedded_string())


class SymbolPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe,
                                                   _asString))
