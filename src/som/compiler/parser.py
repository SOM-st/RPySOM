from rpython.rlib.rbigint import rbigint
from rpython.rlib.rstring import ParseStringOverflowError
from rtruffle.source_section import SourceSection

from ..interpreter.nodes.block_node       import BlockNode, BlockNodeWithContext
from ..interpreter.nodes.global_read_node import UninitializedGlobalReadNode
from ..interpreter.nodes.literal_node     import LiteralNode
from ..interpreter.nodes.message.uninitialized_node import UninitializedMessageNode
from ..interpreter.nodes.return_non_local_node import ReturnNonLocalNode
from ..interpreter.nodes.sequence_node    import SequenceNode

from .lexer                     import Lexer
from .method_generation_context import MethodGenerationContext
from .symbol                    import Symbol, symbol_as_str


class ParseError(BaseException):
    def __init__(self, message, expected_sym, parser):
        self._message           = message
        self._source_coordinate = parser._lexer.get_source_coordinate()
        self._text              = parser._text
        self._raw_buffer        = parser._lexer.get_raw_buffer()
        self._file_name         = parser._file_name
        self._expected_sym      = expected_sym
        self._found_sym         = parser._sym

    def _is_printable_symbol(self):
        return (self._found_sym == Symbol.Integer or
                self._found_sym == Symbol.Double  or
                self._found_sym >= Symbol.STString)

    def _expected_sym_str(self):
        return symbol_as_str(self._expected_sym)

    def __str__(self):
        msg = "%(file)s:%(line)d:%(column)d: error: " + self._message
        if self._is_printable_symbol():
            found = "%s (%s)" % (symbol_as_str(self._found_sym), self._text)
        else:
            found = symbol_as_str(self._found_sym)
        msg += ": %s" % self._raw_buffer

        expected = self._expected_sym_str()

        return (msg % {
            'file'       : self._file_name,
            'line'       : self._source_coordinate.get_start_line(),
            'column'     : self._source_coordinate.get_start_column(),
            'expected'   : expected,
            'found'      : found})


class ParseErrorSymList(ParseError):

    def __init__(self, message, expected_syms, parser):
        ParseError.__init__(self, message, 0, parser)
        self._expected_syms = expected_syms

    def _expected_sym_str(self):
        return  ", ".join([symbol_as_str(x) for x in self._expected_syms])


class Parser(object):
    
    _single_op_syms        = [Symbol.Not,  Symbol.And,  Symbol.Or,    Symbol.Star,
                              Symbol.Div,  Symbol.Mod,  Symbol.Plus,  Symbol.Equal,
                              Symbol.More, Symbol.Less, Symbol.Comma, Symbol.At,
                              Symbol.Per,  Symbol.NONE]
    
    _binary_op_syms        = [Symbol.Or,   Symbol.Comma, Symbol.Minus, Symbol.Equal,
                              Symbol.Not,  Symbol.And,   Symbol.Or,    Symbol.Star,
                              Symbol.Div,  Symbol.Mod,   Symbol.Plus,  Symbol.Equal,
                              Symbol.More, Symbol.Less,  Symbol.Comma, Symbol.At,
                              Symbol.Per,  Symbol.NONE]
    
    _keyword_selector_syms = [Symbol.Keyword, Symbol.KeywordSequence]
  
    def __init__(self, reader, file_name, universe):
        self._universe = universe
        self._source_reader = reader
        self._file_name = file_name
        self._lexer    = Lexer(reader)
        self._sym      = Symbol.NONE
        self._text     = None
        self._next_sym = Symbol.NONE
        self._get_symbol_from_lexer()

    def classdef(self, cgenc):
        cgenc.set_name(self._universe.symbol_for(self._text))
        self._expect(Symbol.Identifier)
        self._expect(Symbol.Equal)
 
        self._superclass(cgenc)
  
        self._expect(Symbol.NewTerm)
        self._instance_fields(cgenc)
        
        while (self._sym_is_identifier() or self._sym == Symbol.Keyword or
               self._sym == Symbol.OperatorSequence or
               self._sym_in(self._binary_op_syms)):
            mgenc = MethodGenerationContext(self._universe)
            mgenc.set_holder(cgenc)
            mgenc.add_argument("self")
         
            method_body = self._method(mgenc)
            cgenc.add_instance_method(mgenc.assemble(method_body))

        if self._accept(Symbol.Separator):
            cgenc.set_class_side(True)
            self._class_fields(cgenc)
            
            while (self._sym_is_identifier()      or
                   self._sym == Symbol.Keyword    or
                   self._sym == Symbol.OperatorSequence or
                   self._sym_in(self._binary_op_syms)):
                mgenc = MethodGenerationContext(self._universe)
                mgenc.set_holder(cgenc)
                mgenc.add_argument("self")
         
                method_body = self._method(mgenc)
                cgenc.add_class_method(mgenc.assemble(method_body))
        
        self._expect(Symbol.EndTerm)

    def _superclass(self, cgenc):
        if self._sym == Symbol.Identifier:
            super_name = self._universe.symbol_for(self._text)
            self._accept(Symbol.Identifier)
        else:
            super_name = self._universe.symbol_for("Object")
        
        cgenc.set_super_name(super_name)
 
        # Load the super class, if it is not nil (break the dependency cycle)
        if super_name.get_string() != "nil":
            super_class = self._universe.load_class(super_name)
            if not super_class:
                raise ParseError("Super class %s could not be loaded"
                                 % super_name.get_string(), Symbol.NONE, self)
            cgenc.set_instance_fields_of_super(
                super_class.get_instance_fields())
            cgenc.set_class_fields_of_super(
                super_class.get_class(self._universe).get_instance_fields())
        else:
            # TODO: figure out what this is
            #raise Exception("What is going on here, not in Java, and I don't think we still got a 'class' field")
            # WARNING:
            # We hardcode here the field names for Class
            # since Object class superclass = Class
            # We avoid here any kind of dynamic solution to avoid further
            # complexity. However, that makes it static, it is going to make it
            #  harder to change the definition of Class and Object
            field_names_of_class = ["class", "superClass", "name",
                                    "instanceFields", "instanceInvokables"]
            field_names = self._universe.new_array_with_strings(field_names_of_class)
            cgenc.set_class_fields_of_super(field_names)

    def _sym_in(self, symbol_list):
        return self._sym in symbol_list

    def _sym_is_identifier(self):
        return self._sym == Symbol.Identifier or self._sym == Symbol.Primitive

    def _accept(self, s):
        if self._sym == s:
            self._get_symbol_from_lexer()
            return True
        return False

    def _accept_one_of(self, symbol_list):
        if self._sym_in(symbol_list):
            self._get_symbol_from_lexer()
            return True
        return False
  
    def _expect(self, s):
        if self._accept(s):
            return True
        raise ParseError("Unexpected symbol. Expected %(expected)s, but found "
                         "%(found)s", s, self)

    def _expect_one_of(self, symbol_list):
        if self._accept_one_of(symbol_list):
            return True
        raise ParseErrorSymList("Unexpected symbol. Expected one of "
                                "%(expected)s, but found %(found)s",
                                symbol_list, self)

    def _instance_fields(self, cgenc):
        if self._accept(Symbol.Or):
            while self._sym_is_identifier():
                var = self._variable()
                cgenc.add_instance_field(self._universe.symbol_for(var))
            self._expect(Symbol.Or)
 
    def _class_fields(self, cgenc):
        if self._accept(Symbol.Or):
            while self._sym_is_identifier():
                var = self._variable()
                cgenc.add_class_field(self._universe.symbol_for(var))
            self._expect(Symbol.Or)

    def _get_source_section(self, coord):
        return SourceSection(
            self._source_reader, "method", coord,
            self._lexer.get_number_of_characters_read(),
            self._file_name)

    def _assign_source(self, node, coord):
        node.assign_source_section(self._get_source_section(coord))
        return node

    def _method(self, mgenc):
        self._pattern(mgenc)
        self._expect(Symbol.Equal)
        if self._sym == Symbol.Primitive:
            mgenc.set_primitive()
            return self._primitive_block()
        else:
            return self._method_block(mgenc)

    def _primitive_block(self):
        self._expect(Symbol.Primitive)
        return None

    def _pattern(self, mgenc):
        if self._sym_is_identifier():
            self._unary_pattern(mgenc)
        elif self._sym == Symbol.Keyword:
            self._keyword_pattern(mgenc)
        else:
            self._binary_pattern(mgenc)

    def _unary_pattern(self, mgenc):
        mgenc.set_signature(self._unary_selector())

    def _binary_pattern(self, mgenc):
        mgenc.set_signature(self._binary_selector())
        mgenc.add_argument_if_absent(self._argument())
 
    def _keyword_pattern(self, mgenc):
        kw = self._keyword()
        mgenc.add_argument_if_absent(self._argument())
        
        while self._sym == Symbol.Keyword:
            kw += self._keyword()
            mgenc.add_argument_if_absent(self._argument())
            
        mgenc.set_signature(self._universe.symbol_for(kw))

    def _method_block(self, mgenc):
        self._expect(Symbol.NewTerm)
        method_body = self._block_contents(mgenc)
        self._expect(Symbol.EndTerm)
        return method_body

    def _unary_selector(self):
        return self._universe.symbol_for(self._identifier())
 
    def _binary_selector(self):
        s = self._text
 
        if    self._accept(Symbol.Or):                     pass
        elif  self._accept(Symbol.Comma):                  pass
        elif  self._accept(Symbol.Minus):                  pass
        elif  self._accept(Symbol.Equal):                  pass
        elif  self._accept_one_of(self._single_op_syms):   pass
        elif  self._accept(Symbol.OperatorSequence):       pass
        else: self._expect(Symbol.NONE)
  
        return self._universe.symbol_for(s)
 
    def _identifier(self):
        s = self._text
        is_primitive = self._accept(Symbol.Primitive)
        if not is_primitive:
            self._expect(Symbol.Identifier)
        return s

    def _keyword(self):
        s = self._text
        self._expect(Symbol.Keyword)
        return s

    def _argument(self):
        return self._variable()

    def _block_contents(self, mgenc):
        if self._accept(Symbol.Or):
            self._locals(mgenc)
            self._expect(Symbol.Or)
  
        return self._block_body(mgenc)

    def _locals(self, mgenc):
        while self._sym_is_identifier():
            mgenc.add_local_if_absent(self._variable())

    def _block_body(self, mgenc):
        coordinate = self._lexer.get_source_coordinate()
        expressions = []

        while True:
            if self._accept(Symbol.Exit):
                expressions.append(self._result(mgenc))
                return self._create_sequence_node(coordinate, expressions)
            elif self._sym == Symbol.EndBlock:
                return self._create_sequence_node(coordinate, expressions)
            elif self._sym == Symbol.EndTerm:
                # the end of the method has been found (EndTerm) - make it
                # implicitly return "self"
                self_exp = self._variable_read(mgenc, "self")
                self_coord = self._lexer.get_source_coordinate()
                self._assign_source(self_exp, self_coord)
                expressions.append(self_exp)
                return self._create_sequence_node(coordinate, expressions)

            expressions.append(self._expression(mgenc))
            self._accept(Symbol.Period)

    def _create_sequence_node(self, coordinate, expressions):
        if not expressions:
            nil_exp = UninitializedGlobalReadNode(
                self._universe.symbol_for("nil"), self._universe)
            return self._assign_source(nil_exp, coordinate)
        if len(expressions) == 1:
            return expressions[0]

        return SequenceNode(expressions[:], self._get_source_section(coordinate))

    def _result(self, mgenc):
        exp   = self._expression(mgenc)
        coord = self._lexer.get_source_coordinate()

        self._accept(Symbol.Period)

        if mgenc.is_block_method():
            node = ReturnNonLocalNode(mgenc.get_outer_self_context_level(),
                                      exp, self._universe)
            mgenc.make_catch_non_local_return()
            return self._assign_source(node, coord)
        else:
            return exp

    def _expression(self, mgenc):
        self._peek_for_next_symbol_from_lexer()
 
        if self._next_sym == Symbol.Assign:
            return self._assignation(mgenc)
        else:
            return self._evaluation(mgenc)

    def _assignation(self, mgenc):
        return self._assignments(mgenc)

    def _assignments(self, mgenc):
        coord = self._lexer.get_source_coordinate()

        if not self._sym_is_identifier():
            raise ParseError("Assignments should always target variables or"
                             " fields, but found instead a %(found)s",
                             Symbol.Identifier, self)

        variable = self._assignment()
        self._peek_for_next_symbol_from_lexer()

        if self._next_sym == Symbol.Assign:
            value = self._assignments(mgenc)
        else:
            value = self._evaluation(mgenc)

        exp = self._variable_write(mgenc, variable, value)
        return self._assign_source(exp, coord)
 
    def _assignment(self):
        var_name = self._variable()
        self._expect(Symbol.Assign)
        return var_name

    def _evaluation(self, mgenc):
        exp = self._primary(mgenc)
 
        if (self._sym_is_identifier()            or
            self._sym == Symbol.Keyword          or 
            self._sym == Symbol.OperatorSequence or
            self._sym_in(self._binary_op_syms)):
            exp = self._messages(mgenc, exp)
        return exp
 
    def _primary(self, mgenc):
        if self._sym_is_identifier():
            coordinate = self._lexer.get_source_coordinate()
            var_name = self._variable()
            var_read = self._variable_read(mgenc, var_name)
            return self._assign_source(var_read, coordinate)

        if self._sym == Symbol.NewTerm:
            return self._nested_term(mgenc)

        if self._sym == Symbol.NewBlock:
            coordinate = self._lexer.get_source_coordinate()
            bgenc = MethodGenerationContext(self._universe)
            bgenc.set_is_block_method(True)
            bgenc.set_holder(mgenc.get_holder())
            bgenc.set_outer(mgenc)
 
            block_body   = self._nested_block(bgenc)
            block_method = bgenc.assemble(block_body)
            mgenc.add_embedded_block_method(block_method)

            if bgenc.requires_context():
                result = BlockNodeWithContext(block_method, self._universe)
            else:
                result = BlockNode(block_method, self._universe)
            return self._assign_source(result, coordinate)

        return self._literal()
 
    def _variable(self):
        return self._identifier()
 
    def _messages(self, mgenc, receiver):
        msg = receiver

        while self._sym_is_identifier():
            msg = self._unary_message(msg)

        while (self._sym == Symbol.OperatorSequence or
               self._sym_in(self._binary_op_syms)):
            msg = self._binary_message(mgenc, msg)
    
        if self._sym == Symbol.Keyword:
            msg = self._keyword_message(mgenc, msg)
        
        return msg

    def _unary_message(self, receiver):
        coord = self._lexer.get_source_coordinate()
        selector = self._unary_selector()
        msg = UninitializedMessageNode(selector, self._universe, receiver, [])
        return self._assign_source(msg, coord)

    def _binary_message(self, mgenc, receiver):
        coord    = self._lexer.get_source_coordinate()
        selector = self._binary_selector()
        operand  = self._binary_operand(mgenc)

        msg = UninitializedMessageNode(selector, self._universe, receiver,
                                       [operand])
        return self._assign_source(msg, coord)

    def _binary_operand(self, mgenc):
        operand = self._primary(mgenc)
 
        while self._sym_is_identifier():
            operand = self._unary_message(operand)
        return operand

    def _keyword_message(self, mgenc, receiver):
        coord = self._lexer.get_source_coordinate()
        arguments = []
        keyword   = []

        while self._sym == Symbol.Keyword:
            keyword.append(self._keyword())
            arguments.append(self._formula(mgenc))

        selector = self._universe.symbol_for("".join(keyword))
        msg = UninitializedMessageNode(selector, self._universe, receiver,
                                       arguments[:])
        return self._assign_source(msg, coord)

    def _formula(self, mgenc):
        operand = self._binary_operand(mgenc)

        while (self._sym == Symbol.OperatorSequence or
               self._sym_in(self._binary_op_syms)):
            operand = self._binary_message(mgenc, operand)
        return operand

    def _nested_term(self, mgenc):
        self._expect(Symbol.NewTerm)
        exp = self._expression(mgenc)
        self._expect(Symbol.EndTerm)
        return exp

    def _literal(self):
        if self._sym == Symbol.Pound:
            return self._literal_symbol()
        if self._sym == Symbol.STString:
            return self._literal_string()
        return self._literal_number()

    def _literal_number(self):
        coord = self._lexer.get_source_coordinate()

        if self._sym == Symbol.Minus:
            lit = self._negative_decimal()
        else:
            lit = self._literal_decimal(False)

        return self._assign_source(lit, coord)
  
    def _literal_decimal(self, negate_value):
        if self._sym == Symbol.Integer:
            return self._literal_integer(negate_value)
        else:
            assert self._sym == Symbol.Double
            return self._literal_double(negate_value)

    def _negative_decimal(self):
        self._expect(Symbol.Minus)
        return self._literal_decimal(True)
 
    def _literal_integer(self, negate_value):
        try:
            i = int(self._text)
            if negate_value:
                i = 0 - i
            result = self._universe.new_integer(i)
        except ParseStringOverflowError:
            bigint = rbigint.fromstr(self._text)
            if negate_value:
                bigint.sign = -1
            result = self._universe.new_biginteger(bigint)
        except ValueError:
            raise ParseError("Could not parse integer. "
                             "Expected a number but got '%s'" % self._text,
                             Symbol.NONE, self)
        self._expect(Symbol.Integer)
        return LiteralNode(result)

    def _literal_double(self, negate_value):
        try:
            f = float(self._text)
            if negate_value:
                f = 0.0 - f
        except ValueError:
            raise ParseError("Could not parse double. "
                             "Expected a number but got '%s'" % self._text,
                             Symbol.NONE, self)
        self._expect(Symbol.Double)
        return LiteralNode(self._universe.new_double(f))
 
    def _literal_symbol(self):
        coord = self._lexer.get_source_coordinate()

        self._expect(Symbol.Pound)
        if self._sym == Symbol.STString:
            s    = self._string()
            symb = self._universe.symbol_for(s)
        else:
            symb = self._selector()
      
        lit = LiteralNode(symb)
        return self._assign_source(lit, coord)

    def _literal_string(self):
        coord = self._lexer.get_source_coordinate()
        s = self._string()
     
        string = self._universe.new_string(s)
        lit = LiteralNode(string)
        return self._assign_source(lit, coord)
     
    def _selector(self):
        if (self._sym == Symbol.OperatorSequence or
            self._sym_in(self._single_op_syms)):
            return self._binary_selector()
        if (self._sym == Symbol.Keyword or
            self._sym == Symbol.KeywordSequence):
            return self._keyword_selector()
        return self._unary_selector()
 
    def _keyword_selector(self):
        s = self._text
        self._expect_one_of(self._keyword_selector_syms)
        symb = self._universe.symbol_for(s)
        return symb
 
    def _string(self):
        s = self._text
        self._expect(Symbol.STString)
        return s

    def _nested_block(self, mgenc):
        self._expect(Symbol.NewBlock)

        mgenc.add_argument_if_absent("$blockSelf")

        if self._sym == Symbol.Colon:
            self._block_pattern(mgenc)

        # generate Block signature
        block_sig = ("$blockMethod@" +
                     str(self._lexer.get_current_line_number()) +
                     "@" + str(self._lexer.get_current_column()))
        arg_size = mgenc.get_number_of_arguments()
        block_sig += ":" * (arg_size - 1)

        mgenc.set_signature(self._universe.symbol_for(block_sig))
 
        expressions = self._block_contents(mgenc)
        self._expect(Symbol.EndBlock)
        return expressions
 
    def _block_pattern(self, mgenc):
        self._block_arguments(mgenc)
        self._expect(Symbol.Or)

    def _block_arguments(self, mgenc):
        self._expect(Symbol.Colon)
        mgenc.add_argument_if_absent(self._argument())
  
        while self._sym == Symbol.Colon:
            self._accept(Symbol.Colon)
            mgenc.add_argument_if_absent(self._argument())
 
    def _variable_read(self, mgenc, variable_name):
        # 'super' needs to be handled separately
        if variable_name == "super":
            variable = mgenc.get_variable("self")
            return variable.get_super_read_node(
                mgenc.get_outer_self_context_level(),
                mgenc.get_holder().get_name(),
                mgenc.get_holder().is_class_side(),
                self._universe)

        # first lookup in local variables, or method arguments
        variable = mgenc.get_variable(variable_name)
        if variable:
            return variable.get_read_node(
                mgenc.get_context_level(variable_name))

        # otherwise, it might be an object field
        var_symbol = self._universe.symbol_for(variable_name)
        field_read = mgenc.get_object_field_read(var_symbol)
        if field_read:
            return field_read

        # nope, so, it is a global?
        return mgenc.get_global_read(var_symbol)

    def _variable_write(self, mgenc, variable_name, exp):
        variable = mgenc.get_local(variable_name)
        if variable:
            return variable.get_write_node(
                mgenc.get_context_level(variable_name), exp)

        field_name = self._universe.symbol_for(variable_name)
        field_write = mgenc.get_object_field_write(field_name, exp)
        if field_write:
            return field_write
        else:
            raise RuntimeError("Neither a variable nor a field found in current"
                               " scope that is named " + variable_name +
                               ". Arguments are read-only.")

    def _get_symbol_from_lexer(self):
        self._sym  = self._lexer.get_sym()
        self._text = self._lexer.get_text()
    
    def _peek_for_next_symbol_from_lexer(self):
        self._next_sym = self._lexer.peek()

