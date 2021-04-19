def get_tokens() -> dict:
    return {
    'IDENT': 1,
    'KEYWORDS': 2,
    'NUM_LIT': 3,
    'CHAR_LIT': 4,
    'STR_LIT': 5,
    'ADD': 6,
    'SUB': 7,
    'MULT': 8,
    'DIV': 9,
    'GT': 10,
    'EQ': 11,
    'ASGN': 12,
    'AND': 13,
    'OR': 14,
    'NOT': 15,
    'LPAREN': 16,
    'RPAREN': 17,
    'LBRACK': 18,
    'RBRACK': 19,
    'ENDSTAT': 20,
    'COMMA': 21,
    'ARROW': 22,
    'CMNT': 23,
    'WHTSPC': 24
    }

def get_symbol_table() -> dict:
    return {}
    ##symbol_table = {
    ##    'func': ,
    ##    'entry': ,
    ##    'var': ,
    ##    'fix': ,
    ##    'num': ,
    ##    'ascii': ,
    ##    'num@': ,
    ##    'ascii@': ,
    ##    'num#': ,
    ##    'ascii#': ,
    ##    'give': ,
    ##    'check': ,
    ##    'other': ,
    ##    'iterif': ,
    ##    'read': ,
    ##    'write': ,
    ##    }  # each value is probably a dict as well

def get_rules() -> dict:
    return {
    '([a-z]|_)+': 'IDENT',
    # So no RE for KWs?
    '(-?)[0-9]+': 'NUM_LIT',
    '`.?`': 'CHAR_LIT',  # example: `g`
    '".*"': 'STR_LIT',  # example: "name"
    'add': 'ADD',
    'sub': 'SUB',
    'mult': 'MULT',
    'div': 'DIV',
    ':=': 'ASGN',
    '&': 'AND',
    '\|': 'OR',
    '\^': 'NOT',
    '\.': 'ENDSTAT',
    ',': 'COMMA',
    '\(': 'LPAREN',
    '\)': 'RPAREN',
    '\[': 'LBRACK',
    '\]': 'RBRACK',
    '=>': 'ARROW',
    '~[^~]*~': 'CMNT',
    '\s': 'WHTSPC'  # Matches all types of whitespace: [ \t\n\r\f\v]
    }

def get_default_code() -> str:
    return 'fix num a := 2.'
