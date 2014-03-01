# Symbol is a 'lightweight' enum, in Python 3.4, we could use Enum as superclass
class Symbol(object):
    NONE             = -1
    Integer          =  0
    Not              =  1
    And              =  2
    Or               =  3
    Star             =  4
    Div              =  5
    Mod              =  6
    Plus             =  7
    Minus            =  8
    Equal            =  9
    More             = 10
    Less             = 11
    Comma            = 12
    At               = 13
    Per              = 14
    NewBlock         = 15
    EndBlock         = 16
    Colon            = 17
    Period           = 18
    Exit             = 19
    Assign           = 20
    NewTerm          = 21
    EndTerm          = 22
    Pound            = 23
    Primitive        = 24
    Separator        = 25
    STString         = 26
    Identifier       = 27
    Keyword          = 28
    KeywordSequence  = 29
    OperatorSequence = 30


def _sorted_symbols(cls):
    "NOT_RPYTHON"
    """This function is only called a single time, at load time of this module.
       For RPypthon, this means, during translation of the module.
    """
    return [key for value, key in \
            sorted([(value, key) for key, value in cls.__dict__.items()]) \
            if isinstance(value, int)
    ]
_symbols = _sorted_symbols(Symbol)


def symbol_as_str(symbol):
    index = symbol + 1
    if index > len(_symbols):
        raise ValueError('No Symbol defined for the value %d.' % symbol)
    else:
        return _symbols[index]
