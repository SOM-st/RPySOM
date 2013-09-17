import os
from StringIO import StringIO

from som.compiler.parser                   import Parser
from som.compiler.class_generation_context import ClassGenerationContext

def compile_class_from_file(path, filename, system_class, universe):
    return _SourcecodeCompiler().compile(path, filename, system_class, universe)

def compile_class_from_string(stmt, system_class, universe):
    return _SourcecodeCompiler().compile_class_string(stmt, system_class, universe)

class _SourcecodeCompiler(object):
    
    def __init__(self):
        self._parser = None
    
    def compile(self, path, filename, system_class, universe):
        fname = path + os.sep + filename + ".som"
        
        with open(fname, "r") as input_file:
            self._parser = Parser(input_file, universe)
            result = self._compile(system_class, universe)

        cname = result.get_name()
        cnameC = cname.get_string()

        if filename != cnameC:
            raise ValueError("File name " + filename + " does not match class name " + cnameC)
    
        return result

    def compile_class_string(self, stream, system_class, universe):
        self._parser = Parser(StringIO(stream), universe)

        result = self._compile(system_class, universe)
        return result

    def _compile(self, system_class, universe):
        cgc = ClassGenerationContext(universe)

        result = system_class
        self._parser.classdef(cgc)

        if not system_class:
            result = cgc.assemble()
        else:
            cgc.assemble_system_class(result)

        return result
