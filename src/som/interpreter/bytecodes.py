class Bytecodes(object):
    
    # Bytecodes used by the Simple Object Machine (SOM)
    halt             =  0
    dup              =  1
    push_local       =  2
    push_argument    =  3
    push_field       =  4
    push_block       =  5
    push_constant    =  6
    push_global      =  7
    pop              =  8
    pop_local        =  9
    pop_argument     = 10
    pop_field        = 11
    send             = 12
    super_send       = 13
    return_local     = 14
    return_non_local = 15
    
    _num_bytecodes   = 16
    
    _bytecode_length = {halt             : 1,
                        dup              : 1,
                        push_local       : 3,
                        push_argument    : 3,
                        push_field       : 2,
                        push_block       : 2,
                        push_constant    : 2,
                        push_global      : 2,
                        pop              : 1,
                        pop_local        : 3,
                        pop_argument     : 3,
                        pop_field        : 2,
                        send             : 2,
                        super_send       : 2,
                        return_local     : 1,
                        return_non_local : 1 }
    
    _stack_effect_depends_on_message = object()
    
    _bytecode_stack_effect = {halt             :  0,
                              dup              :  1,
                              push_local       :  1,
                              push_argument    :  1,
                              push_field       :  1,
                              push_block       :  1,
                              push_constant    :  1,
                              push_global      :  1,
                              pop              : -1,
                              pop_local        : -1,
                              pop_argument     : -1,
                              pop_field        : -1,
                              send             : _stack_effect_depends_on_message,
                              super_send       : _stack_effect_depends_on_message,
                              return_local     : 0,
                              return_non_local : 0 }
    
    @classmethod
    def get_bytecode_length(cls, bytecode):
        return cls._bytecode_length[bytecode]
    
    @classmethod
    def get_stack_effect(cls, bytecode, number_of_arguments_of_message_send = 0):
        if cls.stack_effect_depends_on_send(bytecode):
            return -number_of_arguments_of_message_send + 1 # +1 in order to account for the return value
        else:
            return cls._stack_effect_depends_on_message[bytecode]
    
    @classmethod
    def stack_effect_depends_on_send(cls, bytecode):
        return cls._stack_effect_depends_on_message[bytecode] is cls._stack_effect_depends_on_message

    @classmethod
    def as_str(cls, bytecode):
        if not isinstance(bytecode, int):
            raise ValueError('bytecode is expected to be an integer.')
        
        for key, val in cls.__dict__:
            if val == bytecode:
                return key.upper()
            
        raise ValueError('No defined defined for the value %d.' % bytecode)
