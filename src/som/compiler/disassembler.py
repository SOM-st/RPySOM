from som.vm.universe import Universe
from som.interpreter.bytecodes import Bytecodes

class Disassembler(object):

    @classmethod
    def dump(cls, clazz):
        for i in range(0, clazz.get_number_of_instance_invokables()):
            inv = clazz.get_instance_invokable(i)

            # output header and skip if the Invokable is a Primitive
            Universe.error_print(str(clazz.get_name()) + ">>" +
                                 str(inv.get_signature()) + " = ")

            if inv.is_primitive():
                Universe.error_println("<primitive>")
                continue
      
            # output actual method
            cls.dump_method(inv, "\t")

    @classmethod
    def dump_method(cls, m, indent):
        Universe.error_println("(")

        # output stack information
        Universe.error_println("%s<%d locals, %d stack, %d bc_count>" % (indent,
                               m.get_number_of_locals().get_embedded_integer(),
                               m.get_maximum_number_of_stack_elements().get_embedded_integer(),
                               m.get_number_of_bytecodes()))

        # output bytecodes
        b = 0
        while b < m.get_number_of_bytecodes():
            Universe.error_print(indent)
            
            # bytecode index
            if b < 10:  Universe.error_print(" ")
            if b < 100: Universe.error_print(" ")
            Universe.error_print(" %d:" % b)

            # mnemonic
            bytecode = m.get_bytecode(b)
            Universe.error_print(Bytecodes.as_str(bytecode) + "  ")

            # parameters (if any)
            if Bytecodes.get_bytecode_length(bytecode) == 1:
                Universe.error_println()
                b += 1
                continue
      
            if bytecode == Bytecodes.push_local:
                Universe.error_println("local: " + str(m.get_bytecode(b + 1)) +
                                       ", context: " + str(m.get_bytecode(b + 2)))
            elif bytecode == Bytecodes.push_argument:
                Universe.error_println("argument: " + str(m.get_bytecode(b + 1)) +
                                       ", context " + str(m.get_bytecode(b + 2)))
            elif bytecode == Bytecodes.push_field:
                Universe.error_println("(index: " + str(m.get_bytecode(b + 1)) +
                                       ") field: " + str(m.get_holder().get_instance_field_name(m.get_bytecode(b + 1))))
            elif bytecode == Bytecodes.push_block:
                Universe.error_print("block: (index: " + str(m.get_bytecode(b + 1)) + ") ")
                cls.dump_method(m.get_constant(b), indent + "\t")
            elif bytecode == Bytecodes.push_constant:
                constant = m.get_constant(b)
                Universe.error_println("(index: " + str(m.get_bytecode(b + 1)) +
                                       ") value: (" + 
                                       str(constant.get_class().get_name()) +
                                       ") " + str(constant))
            elif bytecode == Bytecodes.push_global:
                Universe.error_println("(index: " + str(m.get_bytecode(b + 1)) +
                                       ") value: " + str(m.get_constant(b)))
            elif bytecode == Bytecodes.pop_local:
                Universe.error_println("local: "     + str(m.get_bytecode(b + 1)) +
                                       ", context: " + str(m.get_bytecode(b + 2)))
            elif bytecode == Bytecodes.pop_argument:
                Universe.error_println("argument: "  + str(m.get_bytecode(b + 1)) +
                                       ", context: " + str(m.get_bytecode(b + 2)))
            elif bytecode == Bytecodes.pop_field:
                Universe.error_println("(index: "  + str(m.get_bytecode(b + 1)) +
                                       ") field: " + str(m.get_holder().get_instance_field_name(m.get_bytecode(b + 1))))
            elif bytecode == Bytecodes.send:
                Universe.error_println("(index: "      + str(m.get_bytecode(b + 1)) +
                                       ") signature: " + str(m.get_constant(b)))
            elif bytecode == Bytecodes.super_send:
                Universe.error_println("(index: "      + str(m.get_bytecode(b + 1)) +
                                       ") signature: " + str(m.get_constant(b)))
            else:
                Universe.error_println("<incorrect bytecode>")
      
            b += Bytecodes.get_bytecode_length(m.get_bytecode(b))
    
        Universe.error_println(indent + ")")
