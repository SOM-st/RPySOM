from rpython.rlib.streamio import Stream, StreamError

class StringStream(Stream):
    def __init__(self, string):
        self._string = string
        self.pos     = 0
        self.max     = len(string) - 1

    def write(self, data):
        raise StreamError("StringStream is not writable")
    def truncate(self, size):
        raise StreamError("StringStream is immutable")

    def peek(self):
        if self.pos < self.max:
            return self._string[self.pos:]
        else:
            return ''

    def tell(self):
        return self.pos

    def seek(self, offset, whence):
        if whence == 0:
            self.pos = max(0, offset)
        elif whence == 1:
            self.pos = max(0, self.pos + offset)
        elif whence == 2:
            self.pos = max(0, self.max + offset)
        else:
            raise StreamError("seek(): whence must be 0, 1 or 2")

    def read(self, n):
        assert isinstance(n, int)
        end = self.pos + n
        data = self._string[self.pos:end]
        self.pos += len(data)
        return data