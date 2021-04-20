''' Command to run this program
python ./lex.py [./sample_program.txt]
Don't pipe with > ! It picks up on the printed content!
'''

import sys
import io
import re
import constants

tokens = constants.get_tokens()
rules = constants.get_rules()
symbol_table = constants.get_symbol_table()

literal_table = {}

master_regex = '|'.join(f'(?P<{group}>{regex})' for (regex, group) in rules.items())

def formulate_output(line: int, token_type: str, token_val: str) -> str:
    ''' Returns a line of the format "Line 1 Token #1: a" '''
    try:
        token_id = tokens[token_type]
    except:
        raise KeyError('Match group not a valid token type.')
    # cuter alternative: default_dict
    return f'Line {line} Token #{token_id} ({token_type}) : {token_val}\n'

def lex(code_line: str, line_number: int):
    '''Generator function'''
    for res in re.finditer(master_regex, code_line):
        token_type = res.lastgroup
        token_val = res.group()
        if token_type == 'IDENT':
            # add to symbol table
            # reserved words are still confusing to me
            pass
        elif token_type == 'NUM_LIT':
            # add to literal table as number
            pass
        elif token_type == 'CHAR_LIT':
            pass
        elif token_type == 'STR_LIT':
            pass
        # i need a cute way of bundling up reserved words, otherwise the code would be ugly
        # opportunity to think of a nicer DS for constants
            
        yield formulate_output(line_number, token_type, token_val)
        
def main(filepath: str, default: bool) -> None:
    # print(master_regex)
    token_stream = io.StringIO()
    if default:
        code = constants.get_default_code()
    else:
        try:
            input_file = open(filepath, 'r')
            code = input_file.read().strip()
        except:
            sys.exit('Given HLPL file does not exist. Aborting.')
            
    code = code.split('\n')
    for number, line in enumerate(code):
        for result in lex(line, number+1):
            token_stream.write(result)
    
    contents = token_stream.getvalue()
    # print(contents)
    with open('lex_output.txt', 'w') as op:
        op.write(contents)

    token_stream.close()

if __name__ == '__main__':
    default = False
    filepath = ''
    
    if len(sys.argv) < 2:
        print('No HLPL input file provided, proceeding with default code.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default)
    print("Lexing done. Open lex_output.txt.")
