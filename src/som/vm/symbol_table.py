class SymbolTable(object):
    
    def __init__(self):
        self._map = {}
    
    def lookup(self, string):
        # Lookup the given string in the hash map
        return self._map.get(string, None)

    def insert(self, symbol):
        # Insert the given symbol into the hash map by associating the
        # symbol associated string to the symbol itself
        self._map[symbol.get_string()] = symbol
