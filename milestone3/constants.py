# note: i don't like the repetitiveness (repeating token names in 2 places)
# makes it hard to fix stuff
# considering one big DS, maybe list of tuples

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
    'WHTSPC': 24,
    'FUNC': 25,
    'MAIN': 26,  # call it ENTRY instead?
    'VAR': 27,
    'CONST': 28,
    'NUM': 29,
    'CHAR': 30,
    'NUM_ADDR': 31,
    'CHAR_ADDR': 32,
    'NUM_ARR': 33,
    'CHAR_ARR': 34,
    'RETURN': 35,  # call it GIVE instead?
    'IF': 36,
    'ELSE': 37,
    'LOOP': 38,
    'IN': 39,
    'OUT': 40,
    }

def get_symbol_table() -> dict:
    return {}
    ## something = {
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
    ##    }

def get_rules() -> dict:
    return {
    '([a-z]|_)+': 'IDENT',
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
    '\s': 'WHTSPC',  # Matches all types of whitespace: [ \t\n\r\f\v]
    'func': 'FUNC',
    'entry': 'MAIN',
    'var': 'VAR',
    'fix': 'CONST',
    'num': 'NUM',
    'ascii': 'CHAR',
    'num@': 'NUM_ADDR',
    'ascii@': 'CHAR_ADDR',
    'give': 'RETURN',
    'check': 'IF',
    'other': 'ELSE',
    'iterif': 'LOOP',
    'read': 'IN',
    'write': 'OUT',
    }

def get_default_code() -> str:
    return 'fix num a := 2.'
