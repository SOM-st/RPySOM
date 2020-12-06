try:
    from rpython.rlib.unroll import unrolling_iterable
except ImportError:
    def unrolling_iterable(values):
        return values
