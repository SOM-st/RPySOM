try:
    from rpython.rlib import rgc
except ImportError:
    "NOT_RPYTHON"
    def collect():
        pass
