try:
    from rpython.rlib import rgc
except ImportError:
    def collect():
        pass
