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
    
    _names = ("Integer",
              "Not",
              "And",
              "Or",
              "Star",
              "Div",
              "Mod",
              "Plus",
              "Minus",
              "Equal",
              "More",
              "Less",
              "Comma",
              "At",
              "Per",
              "NewBlock",
              "EndBlock",
              "Colon",
              "Period",
              "Exit",
              "Assign",
              "NewTerm",
              "EndTerm",
              "Pound",
              "Primitive",
              "Separator",
              "STString",
              "Identifier",
              "Keyword",
              "KeywordSequence",
              "OperatorSequence")

def symbol_as_str(symbol):
    if symbol == -1:
        return "NONE"
    else:
        return Symbol._names[symbol]
