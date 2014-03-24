from collections import OrderedDict

from rtruffle.source_section import SourceSection

from .variable                                 import Argument, Local

from ..interpreter.nodes.field_node            import create_write_node, \
                                                      create_read_node
from ..interpreter.nodes.global_read_node      import \
    UninitializedGlobalReadNode
from ..interpreter.nodes.return_non_local_node import CatchNonLocalReturnNode
from ..interpreter.invokable                   import Invokable

from ..vmobjects.primitive                     import empty_primitive


class MethodGenerationContext(object):
    
    def __init__(self):
        self._holder_genc = None
        self._outer_genc  = None
        self._block_method = False
        self._signature   = None
        self._arguments   = OrderedDict()
        self._locals      = OrderedDict()
        self._primitive   = False  # to be changed

        self._embedded_block_methods = []

        self._throws_non_local_return             = False
        self._needs_to_catch_non_local_returns    = False
        self._accesses_variables_of_outer_context = False
  
    def set_holder(self, cgenc):
        self._holder_genc = cgenc

    def add_embedded_block_method(self, block_method):
        self._embedded_block_methods.append(block_method)

    def is_primitive(self):
        return self._primitive

    def make_catch_non_local_return(self):
        self._throws_non_local_return = True
        ctx = self._get_outer_context()

        assert ctx is not None
        ctx._needs_to_catch_non_local_returns = True

    def requires_context(self):
        return (self._throws_non_local_return or
                self._accesses_variables_of_outer_context)

    def _get_outer_context(self):
        ctx = self._outer_genc
        while ctx._outer_genc is not None:
            ctx = ctx._outer_genc
        return ctx

    def needs_to_catch_non_local_return(self):
        return self._needs_to_catch_non_local_returns

    def assemble_primitive(self, universe):
        return empty_primitive(self._signature.get_string(), universe)

    @staticmethod
    def _separate_variables(variables, only_local_access,
                            non_local_access):
        for var in variables:
            if var.is_accessed_out_of_context():
                non_local_access.append(var)
            else:
                only_local_access.append(var)

    def _add_argument_initialization(self, method_body):
        return method_body
        # TODO: see whether that has any for of benefit, or whether that is
        # really just for the partial evaluator, that knows a certain pattern

        # writes = [LocalVariableWriteNode(arg.get_frame_idx(),
        #                                  ArgumentReadNode(arg.get_frame_idx()))
        #           for arg in self._arguments.values()]
        # return ArgumentInitializationNode(writes, method_body,
        #                                   method_body.get_source_section())

    def assemble(self, universe, method_body):
        only_local_access = []
        non_local_access = []
        self._separate_variables(self._arguments.values(), only_local_access,
                                 non_local_access)
        self._separate_variables(self._locals.values(), only_local_access,
                                 non_local_access)

        if self.needs_to_catch_non_local_return():
            method_body = CatchNonLocalReturnNode(method_body,
                                                  method_body.get_source_section())

        method_body = self._add_argument_initialization(method_body)
        method = Invokable(self._get_source_section_for_method(method_body),
                           method_body, len(self._locals), universe)
        return universe.new_method(self._signature, method, False,
                                   # copy list to make it immutable for RPython
                                   self._embedded_block_methods[:])

    def _get_source_section_for_method(self, expr):
        src_body = expr.get_source_section()
        assert isinstance(src_body, SourceSection)
        src_method = SourceSection(identifier = "%s>>%s" % (
            self._holder_genc.get_name().get_string(), self._signature),
                                   source_section = src_body)
        return src_method

    def set_primitive(self, boolean):
        self._primitive = boolean

    def set_signature(self, sig):
        self._signature = sig

    def add_argument(self, arg):
        if ("self" == arg or "$blockSelf" == arg) and len(self._arguments) > 0:
            raise RuntimeError("The self argument always has to be the first "
                               "argument of a method")
        argument = Argument(arg, len(self._arguments) - 1)
        self._arguments[arg] = argument

    def add_argument_if_absent(self, arg):
        if arg in self._arguments:
            return
        self.add_argument(arg)

    def add_local_if_absent(self, local):
        if local in self._locals:
            return
        self.add_local(local)

    def add_local(self, local):
        l = Local(local, len(self._locals))
        self._locals[local] = l

    def is_block_method(self):
        return self._block_method

    def set_is_block_method(self, boolean):
        self._block_method = boolean

    def get_holder(self):
        return self._holder_genc
  
    def set_outer(self, mgenc):
        self._outer_genc = mgenc

    def get_outer_self_context_level(self):
        level = 0
        ctx = self._outer_genc
        while ctx is not None:
            ctx = ctx._outer_genc
            level += 1
        return level

    def get_context_level(self, var_name):
        if var_name in self._locals or var_name in self._arguments:
            return 0
        assert self._outer_genc is not None
        return 1 + self._outer_genc.get_context_level(var_name)

    def get_variable(self, var_name):
        if var_name in self._locals:
            return self._locals[var_name]

        if var_name in self._arguments:
            return self._arguments[var_name]

        if self._outer_genc:
            outer_var = self._outer_genc.get_variable(var_name)
            if outer_var:
                self._accesses_variables_of_outer_context = True
                return outer_var
        return None

    def get_local(self, var_name):
        if var_name in self._locals:
            return self._locals[var_name]

        if self._outer_genc:
            outer_local = self._outer_genc.get_local(var_name)
            if outer_local:
                self._accesses_variables_of_outer_context = True
                return outer_local
        return None

    def _get_self_read(self):
        return self.get_variable("self").get_read_node(
            self.get_context_level("self"))

    def get_object_field_read(self, field_name):
        if not self.has_field(field_name):
            return None
        return create_read_node(self._get_self_read(),
                             self.get_field_index(field_name))

    def get_global_read(self, var_name, universe):
        return UninitializedGlobalReadNode(var_name, universe)

    def get_object_field_write(self, field_name, exp, universe):
        if not self.has_field(field_name):
            return None
        return create_write_node(self._get_self_read(),
                              self.get_field_index(field_name),
                              exp)

    def has_field(self, field):
        return self._holder_genc.has_field(field)

    def get_field_index(self, field):
        return self._holder_genc.get_field_index(field)

    def get_number_of_arguments(self):
        return len(self._arguments)

    def get_signature(self):
        return self._signature

    def __str__(self):
        return "MethodGenC(%s>>%s)" % (self._holder_genc.get_name().get_string,
                                       self._signature)
