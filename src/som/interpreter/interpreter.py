from som.interpreter.bytecodes import bytecode_length, Bytecodes
from som.vmobjects.clazz import Class

from rpython.rlib import jit

class Interpreter(object):
    
    _immutable_fields_ = ["_universe"]
    
    def __init__(self, universe):
        self._universe = universe
        self._frame    = None
        
        self._bytecode_index = 0
    
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
        frame.push(self.get_self().get_field(field_index))

    def _do_push_block(self, bytecode_index, frame, method):
        # Handle the push block bytecode
        block_method = method.get_constant(bytecode_index)

        # Push a new block with the current frame as context onto the
        # stack
        frame.push(
            self._universe.new_block(block_method, frame,
            block_method.get_number_of_arguments()))

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
            self.get_self().send_unknown_global(global_name, self._universe, self)

    def _do_pop(self, frame, method):
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
        self.get_self().set_field(field_index, frame.pop())

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

            receiver.send_does_not_understand(signature, self._universe, self)

    def _do_return_local(self, frame, method):
        # Handle the return local bytecode
        result = frame.pop()

        # Pop the top frame and push the result
        self._pop_frame_and_push_result(result)

    @jit.unroll_safe
    def _do_return_non_local(self, frame, method):
        # Handle the return non local bytecode
        result = frame.pop()

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

            # pop the frame of the currently executing block...
            self._pop_frame()

            # ... and execute the escapedBlock message instead
            sender.send_escaped_block(block, self._universe, self)
            return

        # Unwind the frames
        while self.get_frame() is not context:
            self._pop_frame()

        # Pop the top frame and push the result
        self._pop_frame_and_push_result(result)

    def _do_send(self, bytecode_index, frame, method):
        # Handle the send bytecode
        signature = method.get_constant(bytecode_index)

        # Get the number of arguments from the signature
        num_args = signature.get_number_of_signature_arguments()

        # Get the receiver from the stack
        receiver = frame.get_stack_element(num_args - 1)

        # Send the message
        self._send(signature, receiver.get_class(self._universe), bytecode_index)

    def _do_jump_if_false(self, bytecode_index, frame, method):
        value = frame.pop()
        if value is self._universe.falseObject:
            self._do_jump(bytecode_index, method)
    
    def _do_jump_if_true(self, bytecode_index, frame, method):
        value = frame.pop()
        if value is self._universe.trueObject:
            self._do_jump(bytecode_index, method)

    def _do_jump(self, bytecode_index, method):
        target = 0
        target |= method.get_bytecode(bytecode_index + 1)
        target |= method.get_bytecode(bytecode_index + 2) << 8
        target |= method.get_bytecode(bytecode_index + 3) << 16
        target |= method.get_bytecode(bytecode_index + 4) << 24
        
        # do the jump
        self._bytecode_index = target
        
    def start(self):
        # Iterate through the bytecodes
        while True:            
            # Get the current bytecode
            current_bc_idx = self._bytecode_index
            method         = self.get_method()
            frame          = self.get_frame()
            
            jitdriver.jit_merge_point(bytecode_index=current_bc_idx,
                          interp=self,
                          method=method,
                          frame=frame)
            
            bytecode = method.get_bytecode(current_bc_idx)
            
            # Get the length of the current bytecode
            bc_length = bytecode_length(bytecode)

            # Compute the next bytecode index
            self._bytecode_index = current_bc_idx + bc_length


            # Handle the current bytecode
            if   bytecode == Bytecodes.halt:
                return frame.get_stack_element(0)
            elif bytecode == Bytecodes.dup:
                self._do_dup(frame, method)
            elif bytecode == Bytecodes.push_local:
                self._do_push_local(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_argument:
                self._do_push_argument(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_field:
                self._do_push_field(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_block:
                self._do_push_block(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_constant:
                self._do_push_constant(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.push_global:
                self._do_push_global(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.pop:
                self._do_pop(frame, method)
            elif bytecode == Bytecodes.pop_local:
                self._do_pop_local(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.pop_argument:
                self._do_pop_argument(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.pop_field:
                self._do_pop_field(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.send:
                self._do_send(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.super_send:
                self._do_super_send(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.return_local:
                self._do_return_local(frame, method)
            elif bytecode == Bytecodes.return_non_local:
                self._do_return_non_local(frame, method)
            elif bytecode == Bytecodes.jump_if_false:
                self._do_jump_if_false(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.jump_if_true:
                self._do_jump_if_true(current_bc_idx, frame, method)
            elif bytecode == Bytecodes.jump:
                self._do_jump(current_bc_idx, method)

    def push_new_frame(self, method, context):
        # Allocate a new frame and make it the current one
        self.set_frame(self._universe.new_frame(self._frame, method, context))

        # Return the freshly allocated and pushed frame
        return self._frame

    def get_frame(self):
        # Get the frame from the interpreter
        return self._frame
    
    def set_frame(self, frame):
        if self._frame:
            self._frame.set_bytecode_index(self._bytecode_index)
        self._frame = frame
        self._bytecode_index = frame.get_bytecode_index()

    def get_method(self):
        # Get the method from the interpreter
        return jit.promote(self.get_frame().get_method())

    def get_self(self):
        # Get the self object from the interpreter
        return self.get_frame().get_outer_context().get_argument(0, 0)

    def _send(self, selector, receiver_class, bytecode_index):
        # First try the inline cache
        m = self.get_method()
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
        
        self._frame.set_bytecode_index(self._bytecode_index)
        if invokable:
            # Invoke the invokable in the current frame
            invokable.invoke(self.get_frame(), self)
        else:
            num_args = selector.get_number_of_signature_arguments()

            # Compute the receiver
            receiver = self._frame.get_stack_element(num_args - 1)
            receiver.send_does_not_understand(selector, self._universe, self)
        self._bytecode_index = self._frame.get_bytecode_index()

    def _pop_frame(self):
        # Save a reference to the top frame
        result = self._frame

        # Pop the top frame from the frame stack
        self.set_frame(self._frame.get_previous_frame())

        # Destroy the previous pointer on the old top frame
        result.clear_previous_frame()

        # Return the popped frame
        return result

    @jit.unroll_safe
    def _pop_frame_and_push_result(self, result):
        # Pop the top frame from the interpreter frame stack and compute the
        # number of arguments
        num_args = self._pop_frame().get_method().get_number_of_arguments()

        # Pop the arguments
        for _ in range(0, num_args):
            self.get_frame().pop()

        # Push the result
        self.get_frame().push(result)

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
    get_printable_location=get_printable_location)
        #reds=['tape'])

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()
