from rpython.rlib.objectmodel import we_are_translated

from rlib.osext import raw_input

class Shell(object):

    def __init__(self, universe, interpreter):
        self._universe    = universe
        self._interpreter = interpreter
        self._bootstrap_method = None
  
    def set_bootstrap_method(self, method):
        self._bootstrap_method = method

    def start(self):
        from som.vm.universe import std_println, error_println
        counter = 0
        it = self._universe.nilObject

        std_println("SOM Shell. Type \"quit\" to exit.\n")

        # Create a fake bootstrap frame
        current_frame = self._interpreter.new_frame(None, self._bootstrap_method, None)

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
                    current_frame.reset_stack_pointer()
                    
                    # Create and push a new instance of our class on the stack
                    my_object = self._universe.new_instance(my_class)
                    current_frame.push(my_object)

                    # Push the old value of "it" on the stack
                    current_frame.push(it)

                    # Lookup the run: method
                    initialize = my_class.lookup_invokable(
                                        self._universe.symbol_for("run:"))

                    # Invoke the run method
                    initialize.invoke(current_frame, self._interpreter)

                    # Save the result of the run method
                    it = current_frame.pop()
            except Exception as e:
                if not we_are_translated(): # this cannot be done in rpython
                    import traceback
                    traceback.print_exc()
                error_println("Caught exception: %s" % e)
