import sys
import io
import re
import json
import constants

groups = constants.get_groups()
symbol_table = constants.init_symbol_table()

literal_table = {}

master_regex = '|'.join(f'(?P<{group}__{_id}>{regex})' for (regex, group, _id) in groups)

address = 1

def handle_literal(token_type: str, token_val: str):
    global address
    literal_table[token_val] = address  # lol
    # i can understand why a char or string literal would be saved, but why save an integer?
    address += 1

def handle_symbol(token_val: str):
    # need surrounding tokens
    # if the previous token was FUNC, i also need all the tokens up to the last LPAREN
    # even tricker: i need the next tokens: return type
    # if not a func, i need the 2 previous tokens
    # if they have the pattern of a declaration, add the corresponding information
    # in any case, i also need the next tokens in the case of an assignment or constant initialization
    symbol_table[token_val] = {'symbol_type': 'IDENT', 'attributes': {}}
    pass

def lex(code_line: str, line_number: int):
    '''Generator function'''
    for res in re.finditer(master_regex, code_line):
        write = True
        [token_type, token_id] = res.lastgroup.split('__')
        token_val = res.group()
        if token_val in symbol_table and symbol_table[token_val]['symbol_type'] == 'RESERVED':
            pass
        elif token_type == 'IDENT':
            handle_symbol(token_val)
        elif token_type[-3:] == 'LIT':
            handle_literal(token_type, token_val)
        elif token_type == 'CMNT' or token_type == 'WHTSPC':
            write = False
        yield write and f'Line {line_number} Token #{token_id} ({token_type}) : {token_val}\n'
        
def main(filepath: str, default: bool) -> None:
    # print(master_regex)
    token_stream = io.StringIO()    # kinda useless if i'm using it like this?
    
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
        [token_stream.write(result) for result in lex(line, number+1) if result]
    
    contents = token_stream.getvalue()
    # print(contents)
    with open('./lex_output/tokens.txt', 'w') as op:
        op.write(contents)

    # save tables as files
    # print("sym table", symbol_table)
    # print('lit table', literal_table)
    with open('./lex_output/symbol.json', 'w') as op:
        op.write(json.dumps(symbol_table, indent=4))

    with open('./lex_output/literal.json', 'w') as op:
        op.write(json.dumps(literal_table, indent=4))

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
    print("Lexing done. Open tokens.txt.")
