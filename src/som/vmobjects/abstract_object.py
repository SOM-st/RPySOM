from rpython.rlib import jit


class AbstractObject(object):

    def __init__(self):
        pass

    def send(self, selector_string, arguments, universe):
        selector = universe.symbol_for(selector_string)
        invokable = self.get_class(universe).lookup_invokable(selector)
        return invokable.invoke(self, arguments)

    @staticmethod
    # @jit.unroll_safe
    def _prepare_dnu_arguments(arguments, selector, universe):
        # Compute the number of arguments
        selector = jit.promote(selector)
        universe = jit.promote(universe)
        number_of_arguments = selector.get_number_of_signature_arguments() - 1 ## without self
        assert number_of_arguments == len(arguments)

        # TODO: make sure this is still optimizing DNU properly
        # don't want to see any overhead just for using strategies
        arguments_array = universe.new_array_from_list(arguments)
        args = [selector, arguments_array]
        return args

    def send_does_not_understand(self, selector, arguments, universe):
        args = self._prepare_dnu_arguments(arguments, selector, universe)
        return self.send("doesNotUnderstand:arguments:", args, universe)

    def send_unknown_global(self, global_name, universe):
        arguments = [global_name]
        return self.send("unknownGlobal:", arguments, universe)

    def send_escaped_block(self, block, universe):
        arguments = [block]
        return self.send("escapedBlock:", arguments, universe)

    def get_class(self, universe):
        raise NotImplementedError("Subclasses need to implement get_class(universe).")

    def is_invokable(self):
        return False

    def __str__(self):
        from som.vm.universe import get_current
        return "a " + self.get_class(get_current()).get_name().get_embedded_string()
