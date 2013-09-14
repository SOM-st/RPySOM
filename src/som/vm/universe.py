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
                self._setup_classpath(arguments[i + 1])
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
    
    def _setup_classpath(self, cp):
        self._classpath = cp.split(os.pathsep)
    
    # take argument of the form "../foo/Test.som" and return
    # "../foo", "Test", "som"
    def _get_path_class_ext(self, path):
        (path, file_name) = os.path.split(path)
        (file_name, ext)  = os.path.splitext(file_name)
        return (path, file_name, ext[1:])

    def initialize(self, arguments):
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
    
    def new_metaclass_class(self):
        # Allocate the metaclass classes
        result = Class(self)
        result.set_class(Class(self))

        # Setup the metaclass hierarchy
        result.get_class().set_class(result)

        # Return the freshly allocated metaclass class
        return result
