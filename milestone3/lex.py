import sys
import io
import re
import constants

tokens = constants.get_tokens()
symbol_table = constants.get_symbol_table()
rules = constants.get_rules()
default_code = constants.get_default_code()

literal_table = {}

def formulate_output(line: int, token_type: str, token_val: str) -> str:
    ''' Returns a line of the format "Line 1 Token #1: a" '''
    try:
        token_id = tokens[token_type]
    except:
        raise KeyError('Match group not a valid token type.')
    # cuter alternative: default_dict
    return f'Line {line} Token #{token_id}: {token_val}\n'

def lex(code_line: str, line_number: int):
    '''Generator function'''
    master_regex = '|'.join(f'(?P<{group}>{regex})' for (regex, group) in rules.items())
    # print(master_regex)
    for res in re.finditer(master_regex, code_line):
        token_type = res.lastgroup
        token_val = res.group()
        print(token_type, token_val)
        yield formulate_output(line_number, token_type, token_val)
        
def main(filepath: str):
    token_stream = io.StringIO()
    try:
        input_file = open(filepath, 'r')
        code = input_file.read().strip().split('\n')
    except:
        sys.exit('Given HLPL file does not exist. Aborting.')
        
    for number, line in enumerate(code):
        for result in lex(line, number+1):
            token_stream.write(result)
    
    # contents = token_stream.getvalue()

    token_stream.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('No HLPL input file provided, aborting.')
    filepath = sys.argv[1]
    main(filepath)
