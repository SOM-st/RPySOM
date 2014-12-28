
def _create_empty_obj():
    # Try to work around the include cycle
    from som.vmobjects.object import Object
    return Object(None, None)

# The nil object
nilObject = _create_empty_obj()
