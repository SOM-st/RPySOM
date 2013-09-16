from som.interpreter.interpreter import Interpreter
from som.vm.symbol_table         import SymbolTable
from som.vmobjects.object        import Object
from som.vmobjects.clazz         import Class 

import os

class Universe(object):
    
    def __init__(self):
        self._interpreter    = Interpreter(self)
        self._symbol_table   = SymbolTable()
        
        self._globals        = {}
        
        self._nilObject      = None
        self._trueObject     = None
        self._falseObject    = None
        self._objectClass    = None
        self._classClass     = None
        self._metaclassClass = None
        
        self._nilClass       = None
        self._integerClass   = None
        self._bigintegerClass= None
        self._arrayClass     = None
        self._methodClass    = None
        self._symbolClass    = None
        self._frameClass     = None
        self._primitiveClass = None
        self._systemClass    = None
        self._blockClass     = None
        self._doubleClass    = None
        
        self._last_exit_code = 0
        self._classpath      = None
        self._dump_bytecodes = False        
    
    @property
    def nilObject(self):
        return self._nilObject
        
    
    def _create_bootstrap_method(self):
        # Create a fake bootstrap method to simplify later frame traversal
        bootstrap_method = self.new_method(self.symbol_for("bootstrap"), 1, 0)
        bootstrap_method.set_bytecode(0, Bytecodes.halt)
        bootstrap_method.set_number_of_locals(self.new_integer(0))
        bootstrap_method.set_maximum_number_of_stack_elements(self.new_integer(2))
        bootstrap_method.set_holder(self._systemClass)
    
    def interpret(self, arguments):
        # Check for command line switches
        arguments = self.handleArguments(arguments)

        # Initialize the known universe
        self.initialize(arguments)
        
        self.start()
    
    def handleArguments(self, arguments):
        got_classpath  = False
        remaining_args = []

        i = 0
        while i < len(arguments):
            if arguments[i] == "-cp":
                if i + 1 >= len(arguments):
                    self._print_usage_and_exit()
                self.setup_classpath(arguments[i + 1])
                i += 1    # skip class path
                got_classpath = True
            elif arguments[i] == "-d":
                self._dump_bytecodes = True
            else:
                remaining_args.append(arguments[i])
            i += 1 
    
        if not got_classpath:
            # Get the default class path of the appropriate size
            self._classpath = self._setup_default_classpath(0)

        # check remaining args for class paths, and strip file extension
        i = 0
        while i < len(remaining_args):
            split = self._get_path_class_ext(remaining_args[i])

            if split[0] != "":  # there was a path
                self._classpath.insert(0, split[0])
        
            remaining_args[i] = split[1]
            i += 1
        
        return remaining_args
    
    def setup_classpath(self, cp):
        self._classpath = cp.split(os.pathsep)
    
    # take argument of the form "../foo/Test.som" and return
    # "../foo", "Test", "som"
    def _get_path_class_ext(self, path):
        (path, file_name) = os.path.split(path)
        (file_name, ext)  = os.path.splitext(file_name)
        return (path, file_name, ext[1:])

    def _initialize_object_system(self):
        # Allocate the nil object
        self._nilObject = Object(None)

        # Allocate the Metaclass classes
        self._metaclassClass = self.new_metaclass_class()

        # Allocate the rest of the system classes
        self._objectClass     = self.new_system_class()
        self._nilClass        = self.new_system_class()
        self._classClass      = self.new_system_class()
        self._arrayClass      = self.new_system_class()
        self._symbolClass     = self.new_system_class()
        self._methodClass     = self.new_system_class()
        self._integerClass    = self.new_system_class()
        self._bigintegerClass = self.new_system_class()
        self._frameClass      = self.new_system_class()
        self._primitiveClass  = self.new_system_class()
        self._stringClass     = self.new_system_class()
        self._doubleClass     = self.new_system_class()

        # Setup the class reference for the nil object
        self._nilObject.set_class(self._nilClass)

        # Initialize the system classes
        self._initialize_system_class(self._objectClass,                  None, "Object")
        self._initialize_system_class(self._classClass,      self._objectClass, "Class")
        self._initialize_system_class(self._metaclassClass,   self._classClass, "Metaclass")
        self._initialize_system_class(self._nilClass,        self._objectClass, "Nil")
        self._initialize_system_class(self._arrayClass,      self._objectClass, "Array")
        self._initialize_system_class(self._methodClass,      self._arrayClass, "Method")
        self._initialize_system_class(self._symbolClass,     self._objectClass, "Symbol")
        self._initialize_system_class(self._integerClass,    self._objectClass, "Integer")
        self._initialize_system_class(self._bigintegerClass, self._objectClass, "BigInteger")
        self._initialize_system_class(self._frameClass,       self._arrayClass, "Frame")
        self._initialize_system_class(self._primitiveClass,  self._objectClass, "Primitive")
        self._initialize_system_class(self._stringClass,     self._objectClass, "String")
        self._initialize_system_class(self._doubleClass,     self._objectClass, "Double")

        # Load methods and fields into the system classes
        self._load_system_class(self._objectClass)
        self._load_system_class(self._classClass)
        self._load_system_class(self._metaclassClass)
        self._load_system_class(self._nilClass)
        self._load_system_class(self._arrayClass)
        self._load_system_class(self._methodClass)
        self._load_system_class(self._symbolClass)
        self._load_system_class(self._integerClass)
        self._load_system_class(self._bigintegerClass)
        self._load_system_class(self._frameClass)
        self._load_system_class(self._primitiveClass)
        self._load_system_class(self._stringClass)
        self._load_system_class(self._doubleClass)

        # Load the generic block class
        self._blockClass = self._load_class(self._symbol_for("Block"))

        # Setup the true and false objects
        self._trueObject  = self._new_instance(self._load_class(self.symbol_for("True")))
        self._falseObject = self._new_instance(self._load_class(self.symbol_for("False")))

        # Load the system class and create an instance of it
        self._systemClass = self._load_class(self.symbol_for("System"))
        system_object = self._new_instance(self._systemClass)

        # Put special objects and classes into the dictionary of globals
        self.setGlobal(self.symbol_for("nil"),    self._nilObject)
        self.setGlobal(self.symbol_for("true"),   self._trueObject)
        self.setGlobal(self.symbol_for("false"),  self._falseObject)
        self.setGlobal(self.symbol_for("system"), self._systemObject)
        self.setGlobal(self.symbol_for("System"), self._systemClass)
        self.setGlobal(self.symbol_for("Block"),  self._blockClass)
        return system_object
    
    
    def new_array_with_length(self, length):
        # Allocate a new array and set its class to be the array class
        result = Array(self._nilObject)
        result.set_class(self._arrayClass)

        # Set the number of indexable fields to the given value (length)
        result.set_number_of_indexable_fields_and_clear(length, self._nilObject)

        # Return the freshly allocated array
        return result
  
    def new_array_from_list(self, values):
        # Allocate a new array with the same length as the list
        result = self.new_array_with_length(len(values))

        # Copy all elements from the list into the array
        for i in range(len(values)):
            result.set_indexable_field(i, values[i])
    
        # Return the allocated and initialized array
        return result
  
    def new_array_with_strings(self, strings):
        # Allocate a new array with the same length as the string array
        result = self.new_array_with_length(len(strings))

        # Copy all elements from the string array into the array
        for i in range(len(strings)):
            result.set_indexable_field(i, self.new_string(strings[i]))
    
        # Return the allocated and initialized array
        return result
    
    def new_metaclass_class(self):
        # Allocate the metaclass classes
        result = Class(self)
        result.set_class(Class(self))

        # Setup the metaclass hierarchy
        result.get_class().set_class(result)

        # Return the freshly allocated metaclass class
        return result
    
    def new_system_class(self):
        # Allocate the new system class
        system_class = Class(self)

        # Setup the metaclass hierarchy
        system_class.set_class(Class(self))
        system_class.get_class().set_class(self._metaclassClass)

        # Return the freshly allocated system class
        return system_class
    
    def _initialize_system_class(self, system_class, super_class, name):
        # Initialize the superclass hierarchy
        if super_class:
            system_class.setSuperClass(super_class)
            system_class.get_class().set_super_class(super_class.get_class())
        else:
            system_class.get_class().set_super_class(self._classClass)
    

        # Initialize the array of instance fields
        system_class.set_instance_fields(self.new_array_with_length(0))
        system_class.get_class().set_instance_fields(self.new_array_with_length(0))

        # Initialize the array of instance invokables
        system_class.set_instance_invokables(self.new_array_with_length(0))
        system_class.get_class().set_instance_invokables(self.new_array_with_length(0))

        # Initialize the name of the system class
        system_class.set_name(self.symbol_for(name))
        system_class.get_class().setName(self.symbol_for(name + " class"));

        # Insert the system class into the dictionary of globals
        self.set_global(system_class.get_name(), system_class)
    
    
    def get_global(self, name):
        # Return the global with the given name if it's in the dictionary of globals
        if self.has_global(name):
            return self._globals[name]

        # Global not found
        return None

    def set_global(self, name, value):
        # Insert the given value into the dictionary of globals
        self._globals[name] = value
  

    def has_global(self, name):
        # Returns if the universe has a value for the global of the given name
        return name in self._globals
