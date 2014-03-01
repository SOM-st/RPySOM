class AbstractObject(object):
    
    def __init__(self):
        pass
        
    def send(self, frame, selector_string, arguments, universe):
        # Turn the selector string into a selector
        selector = universe.symbol_for(selector_string)
        invokable = self.get_class(universe).lookup_invokable(selector)
        return invokable.invoke(frame, self, arguments)

    def send_does_not_understand(self, frame, selector, arguments, universe):
        # Compute the number of arguments
        number_of_arguments = selector.get_number_of_signature_arguments()
        arguments_array = universe.new_array_with_length(number_of_arguments)

        for i in range(0, number_of_arguments):
            arguments_array.set_indexable_field(i, arguments[i])
            
        args = [selector, arguments_array]
        return self.send(frame, "doesNotUnderstand:arguments:", args, universe)

    def send_unknown_global(self, frame, global_name, universe):
        arguments = [global_name]
        return self.send(frame, "unknownGlobal:", arguments, universe)

    def send_escaped_block(self, frame, block, universe):
        arguments = [block]
        return self.send(frame, "escapedBlock:", arguments, universe)

    def get_class(self, universe):
        raise NotImplementedError("Subclasses need to implement get_class(universe).")

    def is_invokable(self):
        return False

    def __str__(self):
        from som.vm.universe import get_current
        return "a " + self.get_class(get_current()).get_name().get_string()
