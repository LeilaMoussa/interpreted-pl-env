import sys
import io
import re
import constants

groups = constants.get_groups()
reserved = constants.get_keywords()

symbol_table = {}
literal_table = {}

master_regex = '|'.join(f'(?P<{group}__{_id}>{regex})' for (regex, group, _id) in groups)

def handle_literal(token_type: str, token_val: str):
    pass

def handle_symbol(token_type: str):
    pass

def lex(code_line: str, line_number: int):
    '''Generator function'''
    address = 1
    for res in re.finditer(master_regex, code_line):
        write = True
        [token_type, token_id] = res.lastgroup.split('__')
        token_val = res.group()
        if token_val in reserved:
            pass
        elif token_type == 'IDENT':
            # to know what to do, i need to know whether this is a declaration, an assignment...
            # a variable, a function...
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
        # (token_stream.write(result) for result in lex(line, number+1) if result)
        for result in lex(line, number+1):
            if result:
                token_stream.write(result)
    
    contents = token_stream.getvalue()
    # print(contents)
    with open('tokens.txt', 'w') as op:
        op.write(contents)

    # save tables as files

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
