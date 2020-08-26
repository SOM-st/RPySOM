from rpython.rlib.unroll import unrolling_iterable

from ..interp_type import is_ast_interpreter, is_bytecode_interpreter

"""Captures the known primitives at load time of this module, i.e., at compile
   time with RPython.
"""


class PrimitivesNotFound(Exception): pass


def _is_primitives_class(e):
    "NOT_RPYTHON"
    from som.primitives.primitives import Primitives
    import inspect
    _, entry = e
    return (inspect.isclass(entry) and
            issubclass(entry, Primitives)
            and entry is not Primitives)


def _setup_primitives():
    "NOT_RPYTHON"
    from importlib import import_module
    import inspect
    import py
    base_package = "som.primitives."
    if is_ast_interpreter():
        base_package += 'ast.'
    if is_bytecode_interpreter():
        base_package += 'bc.'

    directory = py.path.local(__file__).dirpath()
    files = filter(lambda ent: ent.basename.endswith("_primitives.py"),
                   directory.listdir())
    mods = map(lambda mod: import_module(base_package + mod.purebasename),
               files)
    all_members = map(lambda module: inspect.getmembers(module),
                      mods)
    all_members = reduce(lambda all, each: all + each, all_members)
    all_prims = filter(_is_primitives_class, all_members)
    prim_pairs = map(lambda (name, cls):
                (name[:name.find("Primitives")], cls),
                all_prims)
    return prim_pairs


_primitives = unrolling_iterable(_setup_primitives())


def primitives_for_class(cls):
    name = cls.get_name().get_embedded_string()
    for key, primitives in _primitives:
        if key == name:
            return primitives
    raise PrimitivesNotFound
