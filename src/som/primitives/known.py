from rpython.rlib.unroll import unrolling_iterable
"""Captures the known primitives at load time of this module, i.e., at compile
   time with RPython.
"""

EXPECTED_NUMBER_OF_PRIMITIVE_FILES = 13


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
    directory = py.path.local(__file__).dirpath()
    files = filter(lambda ent: ent.basename.endswith("_primitives.py"),
                   directory.listdir())
    mods = map(lambda mod: import_module("som.primitives." + mod.purebasename),
               files)
    all_members = map(lambda module: inspect.getmembers(module),
                      mods)
    all_members = reduce(lambda all, each: all + each, all_members)
    all_prims = filter(_is_primitives_class, all_members)
    prim_pairs = map(lambda (name, cls):
                (name[:name.find("Primitives")], cls),
                all_prims)
    print ""
    print "SOM PRIMITIVE DISCOVERY: following primitives found:"
    for name, clazz in prim_pairs:
        print "   - %s" % name
    print "Expected number of primitive files: %d, found %d" % (EXPECTED_NUMBER_OF_PRIMITIVE_FILES, len(prim_pairs))
    if EXPECTED_NUMBER_OF_PRIMITIVE_FILES != len(prim_pairs):
        print "ERROR: did not find the expected number of primitive files!"
        import sys
        sys.exit(1)
    return prim_pairs


_primitives = unrolling_iterable(_setup_primitives())


def primitives_for_class(cls):
    name = cls.get_name().get_string()
    for key, primitives in _primitives:
        if key == name:
            return primitives
    raise PrimitivesNotFound
