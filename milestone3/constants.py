def get_groups() -> list:
    return [
        ('func', 'FUNC_KW', 25),
        ('entry', 'MAIN_KW', 26),
        ('var', 'VAR_KW', 27),
        ('fix', 'CONST_KW', 28),
        ('num@', 'NUM_ADDR_KW', 31),
        ('ascii@', 'CHAR_ADDR_KW', 32),
        ('num#', 'NUM_ARR_KW', 33),
        ('ascii#', 'STRING_KW', 34),
        # order is very important here
        ('num', 'NUM_KW', 29),
        ('ascii', 'CHAR_KW', 30),
        ('give', 'RETURN_KW', 35),
        ('check', 'IF_KW', 36),
        ('other', 'ELSE_KW', 37),
        ('iterif', 'LOOP_KW', 38),
        ('read', 'IN_KW', 39),
        ('write', 'OUT_KW', 40),
        
        ('([a-zA-Z]|_)+', 'IDENT', 1),
        ('(-?)[0-9]+', 'NUM_LIT', 2),
        ("'.?'", 'CHAR_LIT', 3),
        ('".*"', 'STR_LIT', 4),
        
        ('\+', 'ADD', 5),
        ('-', 'SUB', 6),
        ('\*', 'MULT', 7),
        ('/', 'DIV', 8),
        (':=', 'ASGN', 9),
        ('&', 'AND', 10),
        ('\|', 'OR', 11),
        ('\^', 'NOT', 12),
        ('>', 'GT', 13),
        ('=', 'EQ', 14),
        
        ('\.', 'ENDSTAT', 15),
        (',', 'COMMA', 16),
        ('\(', 'LPAREN', 17),
        ('\)', 'RPAREN', 18),
        ('\[', 'LBRACK', 19),
        ('\]', 'RBRACK', 20),
        ('=>', 'ARROW', 21),
        ('#', 'IDX', 22),
        
        ('~.*', 'CMNT', 23),
        ('\s', 'WHTSPC', 24),
        ]

def init_symbol_table():
    reserved_keywords = ('func', 'entry', 'var', 'fix', 'num', 'ascii',
            'num@', 'ascii@', 'num#', 'ascii#', 'give', 'check',
            'other', 'iterif', 'read', 'write')
    # a reasonable way to get this list from the above function
    # would be to get the lexemes whose tokens end with KW
    default_kw_val = {'symbol_type': 'RESERVED', }
    return {kw: default_kw_val for kw in reserved_keywords}

def get_symbol_fields():
    # var or fix need: data type, value
    # function needs: parameters (number & types) and return type
    # both need id_type (var, fix, func) and scope
    # what about address?
    # say we have an array, what would be its value: address or actual elements? (i think address)
    # does that mean that its type is actually NUM_ADDRESS not NUM_ARRAY?
    # so our DTs are only: NUM, CHAR, NUM_ADDRESS, CHAR_ADDRESS?
    pass

def get_default_code() -> str:
    return 'fix num a := 2.'
