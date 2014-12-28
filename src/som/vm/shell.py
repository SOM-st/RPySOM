from rpython.rlib.objectmodel import we_are_translated

from rlib.osext import raw_input
from som.vm.globals import nilObject


class Shell(object):

    def __init__(self, universe):
        self._universe = universe

    def start(self):
        from som.vm.universe import std_println, error_println
        counter = 0
        it = nilObject

        std_println("SOM Shell. Type \"quit\" to exit.\n")

        while True:
            try:
                # Read a statement from the keyboard
                stmt = raw_input("---> ")
                if stmt == "quit" or stmt == "":
                    return
                elif stmt == "\n":
                    continue

                # Generate a temporary class with a run method
                stmt = ("Shell_Class_" + str(counter) + 
                        " = ( run: it = ( | tmp | tmp := (" + stmt +
                        " ). 'it = ' print. ^tmp println ) )")
                counter += 1

                # Compile and load the newly generated class
                my_class = self._universe.load_shell_class(stmt)

                # If success
                if my_class:
                    # Create and push a new instance of our class on the stack
                    my_object = self._universe.new_instance(my_class)

                    # Lookup the run: method
                    initialize = my_class.lookup_invokable(
                        self._universe.symbol_for("run:"))

                    # Invoke the run method
                    it = initialize.invoke(my_object, [it])
            except Exception as e:
                if not we_are_translated():  # this cannot be done in rpython
                    import traceback
                    traceback.print_exc()
                error_println("Caught exception: %s" % e)
