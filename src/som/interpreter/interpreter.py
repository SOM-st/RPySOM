from som.interpreter.bytecodes import bytecode_length, Bytecodes
from som.interpreter.control_flow import ReturnException

from rpython.rlib import jit
from som.vmobjects.biginteger import BigInteger
from som.vmobjects.double import Double
from som.vmobjects.integer import Integer


class Interpreter(object):
    
    _immutable_fields_ = ["_universe", "_add_symbol"]
    
    def __init__(self, universe):
        self._universe   = universe
        self._add_symbol      = None
        self._multiply_symbol = None
        self._subtract_symbol = None

    def initialize_known_quick_sends(self):
        self._add_symbol      = self._universe.symbol_for("+")
        self._multiply_symbol = self._universe.symbol_for("*")
        self._subtract_symbol = self._universe.symbol_for("-")
    
    def get_universe(self):
        return self._universe
    
    def _do_dup(self, frame, method):
        # Handle the dup bytecode
        frame.push(frame.get_stack_element(0))

    def _do_push_local(self, bytecode_index, frame, method):
        # Handle the push local bytecode
        frame.push(
            frame.get_local(method.get_bytecode(bytecode_index + 1),
            method.get_bytecode(bytecode_index + 2)))

    def _do_push_argument(self, bytecode_index, frame, method):
        # Handle the push argument bytecode
        frame.push(
            frame.get_argument(method.get_bytecode(bytecode_index + 1),
            method.get_bytecode(bytecode_index + 2)))

    def _do_push_field(self, bytecode_index, frame, method):
        # Handle the push field bytecode
        field_index = method.get_bytecode(bytecode_index + 1)

        # Push the field with the computed index onto the stack
        frame.push(self.get_self(frame).get_field(field_index))

    def _do_push_block(self, bytecode_index, frame, method):
        # Handle the push block bytecode
        block_method = method.get_constant(bytecode_index)

        # Push a new block with the current frame as context onto the
        # stack
        frame.push(self._universe.new_block(block_method, frame))

    def _do_push_constant(self, bytecode_index, frame, method):
        # Handle the push constant bytecode
        frame.push(method.get_constant(bytecode_index))

    def _do_push_global(self, bytecode_index, frame, method):
        # Handle the push global bytecode
        global_name = method.get_constant(bytecode_index)

        # Get the global from the universe
        glob = self._universe.get_global(global_name)

        if glob:
            # Push the global onto the stack
            frame.push(glob)
        else:
            # Send 'unknownGlobal:' to self
            self.get_self(frame).send_unknown_global(frame, global_name, self._universe, self)

    def _do_pop(self, frame):
        # Handle the pop bytecode
        frame.pop()

    def _do_pop_local(self, bytecode_index, frame, method):
        # Handle the pop local bytecode
        frame.set_local(method.get_bytecode(bytecode_index + 1),
                        method.get_bytecode(bytecode_index + 2),
                                   frame.pop())

    def _do_pop_argument(self, bytecode_index, frame, method):
        # Handle the pop argument bytecode
        frame.set_argument(method.get_bytecode(bytecode_index + 1),
                           method.get_bytecode(bytecode_index + 2),
                           frame.pop())

    def _do_pop_field(self, bytecode_index, frame, method):
        # Handle the pop field bytecode
        field_index = method.get_bytecode(bytecode_index + 1)

        # Set the field with the computed index to the value popped from the stack
        self.get_self(frame).set_field(field_index, frame.pop())

    def _do_super_send(self, bytecode_index, frame, method):
        # Handle the super send bytecode
        signature = method.get_constant(bytecode_index)

        # Send the message
        # Lookup the invokable with the given signature
        invokable = method.get_holder().get_super_class().lookup_invokable(signature)

        if invokable:
            # Invoke the invokable in the current frame
            invokable.invoke(frame, self)
        else:
            # Compute the number of arguments
            num_args = signature.get_number_of_signature_arguments()

            # Compute the receiver
            receiver = frame.get_stack_element(num_args - 1)

            receiver.send_does_not_understand(frame, signature, self)

    def _do_return_local(self, frame):
        return frame.top()

    @jit.unroll_safe
    def _do_return_non_local(self, frame):
        # get result from stack
        result = frame.top()

        # Compute the context for the non-local return
        context = frame.get_outer_context()

        # Make sure the block context is still on the stack
        if not context.has_previous_frame():
            # Try to recover by sending 'escapedBlock:' to the sending object
            # this can get a bit nasty when using nested blocks. In this case
            # the "sender" will be the surrounding block and not the object
            # that actually sent the 'value' message.
            block  = frame.get_argument(0, 0)
            sender = frame.get_previous_frame().get_outer_context().get_argument(0, 0)

            # ... and execute the escapedBlock message instead
            sender.send_escaped_block(frame, block, self._universe, self)
            return frame.top()

        raise ReturnException(result, context)

    def _do_add(self, bytecode_index, frame, method):
        rcvr  = frame.get_stack_element(1)
        right = frame.get_stack_element(0)

        if (isinstance(rcvr, Integer) or
                isinstance(rcvr, BigInteger) or
                isinstance(rcvr, Double)):
            frame.pop()
            frame.pop()
            frame.push(rcvr.prim_add(right, self._universe))
        else:
            self._send(method, frame, self._add_symbol,
                       rcvr.get_class(self._universe), bytecode_index)

    def _do_multiply(self, bytecode_index, frame, method):
        rcvr  = frame.get_stack_element(1)
        right = frame.get_stack_element(0)

        if (isinstance(rcvr, Integer) or
                isinstance(rcvr, BigInteger) or
                isinstance(rcvr, Double)):
            frame.pop()
            frame.pop()
            frame.push(rcvr.prim_multiply(right, self._universe))
        else:
            self._send(method, frame, self._multiply_symbol,
                       rcvr.get_class(self._universe), bytecode_index)

    def _do_subtract(self, bytecode_index, frame, method):
        rcvr  = frame.get_stack_element(1)
        right = frame.get_stack_element(0)

        if (isinstance(rcvr, Integer) or
                isinstance(rcvr, BigInteger) or
                isinstance(rcvr, Double)):
            frame.pop()
            frame.pop()
            frame.push(rcvr.prim_subtract(right, self._universe))
        else:
            self._send(method, frame, self._subtract_symbol,
                       rcvr.get_class(self._universe), bytecode_index)

    def _do_send(self, bytecode_index, frame, method):
        # Handle the send bytecode
        signature = method.get_constant(bytecode_index)

        # Get the number of arguments from the signature
        num_args = signature.get_number_of_signature_arguments()

        # Get the receiver from the stack
        receiver = frame.get_stack_element(num_args - 1)

        # Send the message
        self._send(method, frame, signature, receiver.get_class(self._universe),
                   bytecode_index)


    @jit.unroll_safe
    def interpret(self, method, frame):
        current_bc_idx = 0
        while True:
            # since methods cannot contain loops (all loops are done via primitives)
            # profiling only needs to be done on pc = 0
            if current_bc_idx == 0:
                jitdriver.can_enter_jit(bytecode_index=current_bc_idx, interp=self, method=method, frame=frame)
            jitdriver.jit_merge_point(bytecode_index=current_bc_idx,
                          interp=self,
                          method=method,
                          frame=frame)


            bytecode = method.get_bytecode(current_bc_idx)

            # Get the length of the current bytecode
            bc_length = bytecode_length(bytecode)

            # Compute the next bytecode index
            next_bc_idx = current_bc_idx + bc_length

            # Handle the current bytecode
            if   bytecode == Bytecodes.halt:                            # BC: 0
                return frame.get_stack_element(0)
            elif bytecode == Bytecodes.dup:                             # BC: 1
                self._do_dup(frame, method)
            elif bytecode == Bytecodes.push_local:                      # BC: 2
                self._do_push_local(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_argument:                   # BC: 3
                self._do_push_argument(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_field:                      # BC: 4
                self._do_push_field(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_block:                      # BC: 5
                self._do_push_block(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_constant:                   # BC: 6
                self._do_push_constant(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_global:                     # BC: 7
                self._do_push_global(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.pop:                             # BC: 8
                self._do_pop(frame)
            elif bytecode == Bytecodes.pop_local:                       # BC: 9
                self._do_pop_local(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.pop_argument:                    # BC:10
                self._do_pop_argument(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.pop_field:                       # BC:11
                self._do_pop_field(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.send:                            # BC:12
                self._do_send(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.super_send:                      # BC:13
                self._do_super_send(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.return_local:                    # BC:14
                return self._do_return_local(frame)
            elif bytecode == Bytecodes.return_non_local:                # BC:15
                return self._do_return_non_local(frame)
            elif bytecode == Bytecodes.add:
                self._do_add(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.multiply:
                self._do_multiply(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.subtract:
                self._do_subtract(current_bc_idx, frame, method)

            current_bc_idx = next_bc_idx

    def new_frame(self, prev_frame, method, context):
        return self._universe.new_frame(prev_frame, method, context)

    def get_self(self, frame):
        # Get the self object from the interpreter
        return frame.get_outer_context().get_argument(0, 0)

    def _send(self, m, frame, selector, receiver_class, bytecode_index):
        # First try the inline cache
        cached_class = m.get_inline_cache_class(bytecode_index)
        if cached_class == receiver_class:
            invokable = m.get_inline_cache_invokable(bytecode_index)
        else:
            if not cached_class:
                # Lookup the invokable with the given signature
                invokable = receiver_class.lookup_invokable(selector)
                m.set_inline_cache(bytecode_index, receiver_class, invokable)
            else:
                cached_class = m.get_inline_cache_class(bytecode_index + 1) # the bytecode index after the send is used by the selector constant, and can be used safely as another cache item
                if cached_class == receiver_class:
                    invokable = m.get_inline_cache_invokable(bytecode_index + 1)
                else:
                    invokable = receiver_class.lookup_invokable(selector)
                    if not cached_class:
                        m.set_inline_cache(bytecode_index + 1, receiver_class, invokable)

        if invokable:
            invokable.invoke(frame, self)
        else:
            num_args = selector.get_number_of_signature_arguments()

            # Compute the receiver
            receiver = frame.get_stack_element(num_args - 1)
            receiver.send_does_not_understand(frame, selector, self)


def get_printable_location(bytecode_index, interp, method):
    from som.vmobjects.method import Method
    from som.interpreter.bytecodes import bytecode_as_str
    assert isinstance(method, Method)
    bc = method.get_bytecode(bytecode_index)
    return "%s @ %d in %s" % (bytecode_as_str(bc),
                              bytecode_index,
                              method.merge_point_string())

jitdriver = jit.JitDriver(
    greens=['bytecode_index', 'interp', 'method'],
    reds=['frame'],
    # virtualizables=['frame'],
    get_printable_location=get_printable_location,
    # the next line is a workaround around a likely bug in RPython
    # for some reason, the inlining heuristics default to "never inline" when
    # two different jit drivers are involved (in our case, the primitive
    # driver, and this one).

    # the next line says that calls involving this jitdriver should always be
    # inlined once (which means that things like Integer>>< will be inlined
    # into a while loop again, when enabling this drivers).
    should_unroll_one_iteration = lambda bytecode_index, inter, method: True)
        #reds=['tape'])


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()
