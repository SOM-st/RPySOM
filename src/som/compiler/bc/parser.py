from rpython.rlib.rarithmetic import string_to_int
from rpython.rlib.rbigint import rbigint
from rpython.rlib.rstring import ParseStringOverflowError

from ..lexer import Lexer
from .bytecode_generator import BytecodeGenerator
from .method_generation_context import MethodGenerationContext
from ..parse_error import ParseError, ParseErrorSymList
from ..symbol import Symbol


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
        self._file_name = file_name
        self._lexer    = Lexer(reader)
        self._bc_gen   = BytecodeGenerator()
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
            mgenc = MethodGenerationContext()
            mgenc.set_holder(cgenc)
            mgenc.add_argument("self")

            self._method(mgenc)

            if mgenc.is_primitive():
                cgenc.add_instance_method(
                    mgenc.assemble_primitive(self._universe))
            else:
                cgenc.add_instance_method(
                    mgenc.assemble(self._universe))

        if self._accept(Symbol.Separator):
            cgenc.set_class_side(True)
            self._class_fields(cgenc)

            while (self._sym_is_identifier()      or
                   self._sym == Symbol.Keyword    or
                   self._sym == Symbol.OperatorSequence or
                   self._sym_in(self._binary_op_syms)):
                mgenc = MethodGenerationContext()
                mgenc.set_holder(cgenc)
                mgenc.add_argument("self")

                self._method(mgenc)

                if mgenc.is_primitive():
                    cgenc.add_class_method(
                        mgenc.assemble_primitive(self._universe))
                else:
                    cgenc.add_class_method(
                        mgenc.assemble(self._universe))

        self._expect(Symbol.EndTerm)

    def _superclass(self, cgenc):
        if self._sym == Symbol.Identifier:
            super_name = self._universe.symbol_for(self._text)
            self._accept(Symbol.Identifier)
        else:
            super_name = self._universe.symbol_for("Object")

        cgenc.set_super_name(super_name)

        # Load the super class, if it is not nil (break the dependency cycle)
        if super_name.get_embedded_string() != "nil":
            super_class = self._universe.load_class(super_name)
            if not super_class:
                raise ParseError("Super class %s could not be loaded"
                                 % super_name.get_embedded_string(), Symbol.NONE, self)
            cgenc.set_instance_fields_of_super(
                super_class.get_instance_fields())
            cgenc.set_class_fields_of_super(
                super_class.get_class(self._universe).get_instance_fields())

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

    def _method(self, mgenc):
        self._pattern(mgenc)
        self._expect(Symbol.Equal)
        if self._sym == Symbol.Primitive:
            mgenc.set_primitive()
            self._primitive_block()
        else:
            self._method_block(mgenc)

    def _primitive_block(self):
        self._expect(Symbol.Primitive)

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
        self._block_contents(mgenc)

        # if no return has been generated so far, we can be sure there was no .
        # terminating the last expression, so the last expression's value must
        # be popped off the stack and a ^self be generated
        if not mgenc.is_finished():
            self._bc_gen.emitPOP(mgenc)
            self._bc_gen.emitPUSHARGUMENT(mgenc, 0, 0)
            self._bc_gen.emitRETURNLOCAL(mgenc)
            mgenc.set_finished()

        self._expect(Symbol.EndTerm)

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

        self._block_body(mgenc, False)

    def _locals(self, mgenc):
        while self._sym_is_identifier():
            mgenc.add_local_if_absent(self._variable())

    def _block_body(self, mgenc, seenPeriod):
        if self._accept(Symbol.Exit):
            self._result(mgenc)
        elif self._sym == Symbol.EndBlock:
            if seenPeriod:
                # a POP has been generated which must be elided (blocks always
                # return the value of the last expression, regardless of
                # whether it was terminated with a . or not)
                mgenc.remove_last_bytecode()

            # if this block is empty, we need to return nil
            if mgenc.is_block_method() and not mgenc.has_bytecode():
                nil_sym = self._universe.symbol_for("nil")
                mgenc.add_literal_if_absent(nil_sym)
                self._bc_gen.emitPUSHGLOBAL(mgenc, nil_sym)

            self._bc_gen.emitRETURNLOCAL(mgenc)
            mgenc.set_finished()
        elif self._sym == Symbol.EndTerm:
            # it does not matter whether a period has been seen, as the end of
            # the method has been found (EndTerm) - so it is safe to emit a
            # "return self"
            self._bc_gen.emitPUSHARGUMENT(mgenc, 0, 0)
            self._bc_gen.emitRETURNLOCAL(mgenc)
            mgenc.set_finished()
        else:
            self._expression(mgenc)
            if self._accept(Symbol.Period):
                self._bc_gen.emitPOP(mgenc)
                self._block_body(mgenc, True)

    def _result(self, mgenc):
        self._expression(mgenc)
        self._accept(Symbol.Period)

        if mgenc.is_block_method():
            self._bc_gen.emitRETURNNONLOCAL(mgenc)
        else:
            self._bc_gen.emitRETURNLOCAL(mgenc)

        mgenc.set_finished()

    def _expression(self, mgenc):
        self._peek_for_next_symbol_from_lexer()

        if self._next_sym == Symbol.Assign:
            self._assignation(mgenc)
        else:
            self._evaluation(mgenc)

    def _assignation(self, mgenc):
        l = []

        self._assignments(mgenc, l)
        self._evaluation(mgenc)

        for assignment in l:
            self._bc_gen.emitDUP(mgenc)

        for assignment in l:
            self._gen_pop_variable(mgenc, assignment)

    def _assignments(self, mgenc, l):
        if self._sym_is_identifier():
            l.append(self._assignment(mgenc))
            self._peek_for_next_symbol_from_lexer()
            if self._next_sym == Symbol.Assign:
                self._assignments(mgenc, l)

    def _assignment(self, mgenc):
        v   = self._variable()
        var = self._universe.symbol_for(v)
        mgenc.add_literal_if_absent(var)

        self._expect(Symbol.Assign)
        return v

    def _evaluation(self, mgenc):
        is_super_send = self._primary(mgenc)

        if (self._sym_is_identifier()            or
            self._sym == Symbol.Keyword          or
            self._sym == Symbol.OperatorSequence or
            self._sym_in(self._binary_op_syms)):
            self._messages(mgenc, is_super_send)

    def _primary(self, mgenc):
        is_super_send = False

        if self._sym_is_identifier():
            v = self._variable()
            if v == "super":
                is_super_send = True
                # sends to super push self as the receiver
                v = "self"
            self._gen_push_variable(mgenc, v)

        elif self._sym == Symbol.NewTerm:
            self._nested_term(mgenc)
        elif self._sym == Symbol.NewBlock:
            bgenc = MethodGenerationContext()
            bgenc.set_is_block_method(True)
            bgenc.set_holder(mgenc.get_holder())
            bgenc.set_outer(mgenc)

            self._nested_block(bgenc)

            block_method = bgenc.assemble(self._universe)
            mgenc.add_literal(block_method)
            self._bc_gen.emitPUSHBLOCK(mgenc, block_method)
        else:
            self._literal(mgenc)

        return is_super_send

    def _variable(self):
        return self._identifier()

    def _messages(self, mgenc, is_super_send):
        if self._sym_is_identifier():
            while self._sym_is_identifier():
                # only the first message in a sequence can be a super send
                self._unary_message(mgenc, is_super_send)
                is_super_send = False

            while (self._sym == Symbol.OperatorSequence or
                   self._sym_in(self._binary_op_syms)):
                self._binary_message(mgenc, False)

            if self._sym == Symbol.Keyword:
                self._keyword_message(mgenc, False)

        elif (self._sym == Symbol.OperatorSequence or
              self._sym_in(self._binary_op_syms)):
            while (self._sym == Symbol.OperatorSequence or
                   self._sym_in(self._binary_op_syms)):
                # only the first message in a sequence can be a super send
                self._binary_message(mgenc, is_super_send)
                is_super_send = False

            if self._sym == Symbol.Keyword:
                self._keyword_message(mgenc, False)

        else:
            self._keyword_message(mgenc, is_super_send)

    def _unary_message(self, mgenc, is_super_send):
        msg = self._unary_selector()
        mgenc.add_literal_if_absent(msg)

        if is_super_send:
            self._bc_gen.emitSUPERSEND(mgenc, msg)
        else:
            self._bc_gen.emitSEND(mgenc, msg)

    @staticmethod
    def _is_quick_send(msg):
        m = msg.get_embedded_string()
        return m == "+" or m == "-" or m == "*"

    def _binary_message(self, mgenc, is_super_send):
        msg = self._binary_selector()
        mgenc.add_literal_if_absent(msg)

        self._binary_operand(mgenc)

        if is_super_send:
            self._bc_gen.emitSUPERSEND(mgenc, msg)
        elif self._is_quick_send(msg):
            self._bc_gen.emitQUICKSEND(mgenc, msg)
        else:
            self._bc_gen.emitSEND(mgenc, msg)

    def _binary_operand(self, mgenc):
        is_super_send = self._primary(mgenc)

        while self._sym_is_identifier():
            self._unary_message(mgenc, is_super_send)
            is_super_send = False

        return is_super_send

    def _keyword_message(self, mgenc, is_super_send):
        kw = self._keyword()
        self._formula(mgenc)

        while self._sym == Symbol.Keyword:
            kw += self._keyword()
            self._formula(mgenc)

        msg = self._universe.symbol_for(kw)

        mgenc.add_literal_if_absent(msg)

        if is_super_send:
            self._bc_gen.emitSUPERSEND(mgenc, msg)
        else:
            self._bc_gen.emitSEND(mgenc, msg)

    def _formula(self, mgenc):
        is_super_send = self._binary_operand(mgenc)

        # only the first message in a sequence can be a super send
        if self._sym == Symbol.OperatorSequence or self._sym_in(self._binary_op_syms):
            self._binary_message(mgenc, is_super_send)

        while self._sym == Symbol.OperatorSequence or self._sym_in(self._binary_op_syms):
            self._binary_message(mgenc, False)

    def _nested_term(self, mgenc):
        self._expect(Symbol.NewTerm)
        self._expression(mgenc)
        self._expect(Symbol.EndTerm)

    def _literal(self, mgenc):
        if self._sym == Symbol.Pound:
            self._peek_for_next_symbol_from_lexer_if_necessary()

            if self._next_sym == Symbol.NewTerm:
                self._literal_array(mgenc)
            else:
                self._literal_symbol(mgenc)
        elif self._sym == Symbol.STString:
            self._literal_string(mgenc)
        else:
            self._literal_number(mgenc)

    def _literal_number(self, mgenc):
        if self._sym == Symbol.Minus:
            lit = self._negative_decimal()
        else:
            lit = self._literal_decimal(False)

        mgenc.add_literal_if_absent(lit)
        self._bc_gen.emitPUSHCONSTANT(mgenc, lit)

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
            i = string_to_int(self._text)
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
        return result

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
        return self._universe.new_double(f)

    def _literal_symbol(self, mgenc):
        self._expect(Symbol.Pound)
        if self._sym == Symbol.STString:
            s    = self._string()
            symb = self._universe.symbol_for(s)
        else:
            symb = self._selector()

        mgenc.add_literal_if_absent(symb)
        self._bc_gen.emitPUSHCONSTANT(mgenc, symb)

    def _literal_string(self, mgenc):
        s = self._string()

        string = self._universe.new_string(s)
        mgenc.add_literal_if_absent(string)

        self._bc_gen.emitPUSHCONSTANT(mgenc, string)

    def _literal_array(self, mgenc):
        self._expect(Symbol.Pound)
        self._expect(Symbol.NewTerm)

        array_class_name = self._universe.symbol_for("Array")
        array_size_placeholder = self._universe.symbol_for("ArraySizeLiteralPlaceholder")
        new_message = self._universe.symbol_for("new:")
        at_put_message = self._universe.symbol_for("at:put:")

        mgenc.add_literal_if_absent(array_class_name)
        mgenc.add_literal_if_absent(new_message)
        mgenc.add_literal_if_absent(at_put_message)

        array_size_literal_idx = mgenc.add_literal(array_size_placeholder)

        # create empty array
        self._bc_gen.emitPUSHGLOBAL(mgenc, array_class_name)
        self._bc_gen.emitPUSHCONSTANT_index(mgenc, array_size_literal_idx)
        self._bc_gen.emitSEND(mgenc, new_message)

        i = 1

        while self._sym != Symbol.EndTerm:
            push_idx = self._universe.new_integer(i)
            mgenc.add_literal_if_absent(push_idx)
            self._bc_gen.emitPUSHCONSTANT(mgenc, push_idx)

            self._literal(mgenc)
            self._bc_gen.emitSEND(mgenc, at_put_message)
            i += 1

        mgenc.update_literal(
            array_size_placeholder, array_size_literal_idx, self._universe.new_integer(i - 1))
        self._expect(Symbol.EndTerm)

    def _selector(self):
        if self._sym == Symbol.OperatorSequence or self._sym_in(self._single_op_syms):
            return self._binary_selector()
        if self._sym == Symbol.Keyword or self._sym == Symbol.KeywordSequence:
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
        block_sig = "$blockMethod"
        arg_size = mgenc.get_number_of_arguments()
        block_sig += ":" * (arg_size - 1)

        mgenc.set_signature(self._universe.symbol_for(block_sig))

        self._block_contents(mgenc)

        # if no return has been generated, we can be sure that the last
        # expression in the block was not terminated by ., and can generate
        # a return
        if not mgenc.is_finished():
            if not mgenc.has_bytecode():
                nil_sym = self._universe.symbol_for("nil")
                mgenc.add_literal_if_absent(nil_sym)
                self._bc_gen.emitPUSHGLOBAL(mgenc, nil_sym)
            self._bc_gen.emitRETURNLOCAL(mgenc)
            mgenc.set_finished()

        self._expect(Symbol.EndBlock)

    def _block_pattern(self, mgenc):
        self._block_arguments(mgenc)
        self._expect(Symbol.Or)

    def _block_arguments(self, mgenc):
        self._expect(Symbol.Colon)
        mgenc.add_argument_if_absent(self._argument())

        while self._sym == Symbol.Colon:
            self._expect(Symbol.Colon)
            mgenc.add_argument_if_absent(self._argument())

    def _gen_push_variable(self, mgenc, var):
        # The purpose of this function is to find out whether the variable to be
        # pushed on the stack is a local variable, argument, or object field.
        # This is done by examining all available lexical contexts, starting with
        # the innermost (i.e., the one represented by mgenc).

        # triplet: index, context, isArgument
        triplet = [0, 0, False]

        if mgenc.find_var(var, triplet):
            if triplet[2]:
                self._bc_gen.emitPUSHARGUMENT(mgenc, triplet[0], triplet[1])
            else:
                self._bc_gen.emitPUSHLOCAL(mgenc, triplet[0], triplet[1])
        else:
            identifier = self._universe.symbol_for(var)
            if mgenc.has_field(identifier):
                field_name = identifier
                mgenc.add_literal_if_absent(field_name)
                self._bc_gen.emitPUSHFIELD(mgenc, field_name)
            else:
                globe = identifier
                mgenc.add_literal_if_absent(globe)
                self._bc_gen.emitPUSHGLOBAL(mgenc, globe)

    def _gen_pop_variable(self, mgenc, var):
        # The purpose of this function is to find out whether the variable to be
        # popped off the stack is a local variable, argument, or object field.
        # This is done by examining all available lexical contexts, starting with
        # the innermost (i.e., the one represented by mgenc).

        # triplet: index, context, isArgument
        triplet = [0, 0, False]

        if mgenc.find_var(var, triplet):
            if triplet[2]:
                self._bc_gen.emitPOPARGUMENT(mgenc, triplet[0], triplet[1])
            else:
                self._bc_gen.emitPOPLOCAL(mgenc, triplet[0], triplet[1])
        else:
            self._bc_gen.emitPOPFIELD(mgenc, self._universe.symbol_for(var))

    def _get_symbol_from_lexer(self):
        self._sym  = self._lexer.get_sym()
        self._text = self._lexer.get_text()

    def _peek_for_next_symbol_from_lexer(self):
        self._next_sym = self._lexer.peek()

    def _peek_for_next_symbol_from_lexer_if_necessary(self):
        if not self._lexer.get_peek_done():
            self._peek_for_next_symbol_from_lexer()
