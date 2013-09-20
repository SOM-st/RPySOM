class Shell(object):

    def __init__(self, universe, interpreter):
        self._universe    = universe
        self._interpreter = interpreter
        self._bootstrap_method = None
  
    def set_bootstrap_method(self, method):
        self._bootstrap_method = method

    def start(self):
        counter = 0
        it = self._universe.nilObject

        from som.vm.universe import std_println
        std_println("SOM Shell. Type \"quit\" to exit.\n");

        # Create a fake bootstrap frame
        current_frame = self._interpreter.push_new_frame(self._bootstrap_method)

        # Remember the first bytecode index, e.g. index of the halt instruction
        bytecode_index = current_frame.get_bytecode_index()

        while True:
            try:
                # Read a statement from the keyboard
                stmt = raw_input("---> ")
                if stmt == "quit":
                    return

                # Generate a temporary class with a run method
                stmt = ("Shell_Class_" + str(counter) + 
                        " = ( run: it = ( | tmp | tmp := (" + stmt +
                        " ). 'it = ' print. ^tmp println ) )")
                counter += 1

                # Compile and load the newly generated class
                my_class = self._universe.load_shell_class(stmt)

                # If success
                if my_class:
                    current_frame = self._interpreter.get_frame()

                    # Go back, so we will evaluate the bootstrap frames halt
                    # instruction again
                    current_frame.set_bytecode_index(bytecode_index)

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

                    # Start the interpreter
                    self._interpreter.start()

                    # Save the result of the run method
                    it = current_frame.pop()
            except Exception, e:
                import traceback
                traceback.print_exc()
                self._universe.error_println("Caught exception: " + str(e))
                self._universe.error_println(str(
                            self._interpreter.get_frame().get_previous_frame()))
