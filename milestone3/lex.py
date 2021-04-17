import sys
import io
import re

tokens = {
    'IDENT': 1,
    'KEYWORDS': 2,
    'NUM_LIT': 3,
    'CHAR_LIT': 4,
    'STR_LIT': 5,
    'OPERATOR': 6, # Wondering whether to separate the opeators: ASSIGN, ARITHMETIC, CMP...
    'PUNC': 7,
    'COMM': 8,
    'WHTSPC': 9,
    # need parentheses and brackets
    }

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


literal_table = {}  # doesn't have to be dict(), can use other classes


rules = {
    '([a-z]|_)+': 'IDENT',
    # So no RE for KWs?
    '(-?)[0-9]+': 'NUM_LIT',
    '".?"': 'CHAR_LIT',
    '".*"': 'STR_LIT',
    'add|sub|mult|div|\:=|\&|\||\^': 'OPERATOR',
    '[.,]': 'PUNC',
    '~[^~]*~': 'COMM',
    '\s': 'WHTSPC'  # Matches all types of whitespace: [ \t\n\r\f\v]
    }

next_token = ''

def create_token():
    pass

def lex(data: str):
    master_regex = '|'.join(f'(?P<{group}>{regex})' for (regex, group) in rules.items())
    # print(master_regex)
    for res in re.finditer(master_regex, data):
        print(res.group(), res.lastgroup)

def main(filepath: str):
    token_stream = io.StringIO()
    try:
        input_file = open(filepath, 'r')
        data = input_file.read()
        # print(data)
        lex(data)
    except:
        sys.exit('File does not exist.')

    # Handy methods:
    # token_stream.write('first token ')
    # contents = token_stream.getvalue()

    token_stream.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('No HLPL input file provided, aborting.')
    filepath = sys.argv[1]
    main(filepath)
