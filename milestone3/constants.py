def get_groups() -> list:
    return [
        ('([a-z]|_)+', 'IDENT', 1),
        ('(-?)[0-9]+', 'NUM_LIT', 2),
        ("'.?'", 'CHAR_LIT', 3),
        ('".*"', 'STR_LIT', 4),
        ('add', 'ADD', 5),   # !!!
        ('sub', 'SUB', 6),
        ('mult', 'MULT', 7),
        ('div', 'DIV', 8),
        (':=', 'ASGN', 9),
        ('&', 'AND', 10),
        ('\|', 'OR', 11),
        ('\^', 'NOT', 12),
        ('isGreater', 'GT', 13),
        ('isEqual', 'EQ', 14),
        ('\.', 'ENDSTAT', 15),
        (',', 'COMMA', 16),
        ('\(', 'LPAREN', 17),
        ('\)', 'RPAREN', 18),
        ('\[', 'LBRACK', 19),
        ('\]', 'RBRACK', 20),
        ('=>', 'ARROW', 21),
        ('#', 'IDX', 22),
        # ('~[^~]*~', 'CMNT', 23),
        ('~.*', 'CMNT', 23),
        ('\s', 'WHTSPC', 24),
        ('func', 'FUNC', 25),
        ('entry', 'MAIN', 26),
        ('var', 'VAR', 27),
        ('fix', 'CONST', 28),
        ('num', 'NUM', 29),
        ('ascii', 'CHAR', 30),
        ('num@', 'NUM_ADDR', 31),
        ('ascii@', 'CHAR_ADDR', 32),
        ('num#', 'NUM_ARR', 33),
        ('ascii#', 'STRING', 34),
        ('give', 'RETURN', 35),
        ('check', 'IF', 36),
        ('other', 'ELSE', 37),
        ('iterif', 'LOOP', 38),
        ('read', 'IN', 39),
        ('write', 'OUT', 40),
        ]

def get_keywords():
    return ('func', 'entry', 'var', 'fix', 'num', 'ascii',
            'num@', 'ascii@', 'num#', 'ascii#', 'give', 'check',
            'other', 'iterif', 'read', 'write')

def get_default_code() -> str:
    return 'fix num a := 2.'
