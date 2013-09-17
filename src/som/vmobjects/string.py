from som.vmobjects.object import Object

class String(Object):
    
    def __init__(self, nilObject):
        super(String, self).__init__(nilObject)
        self._string = None
    
    def get_embedded_string(self):
        return self._string
    
    def set_embedded_string(self, value):
        self._string = value
    
    def __str__(self):
        return "\"" + self._string + "\""
