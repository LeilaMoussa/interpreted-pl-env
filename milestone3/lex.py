import sys
import re
import json
import constants  # User-defined module in this directory.

# Get the lexical description rules and tokens, along with the symbol table
# initialized with reserved words, from constants.
groups = constants.get_groups()
symbol_table = constants.init_symbol_table()

# Literal table starts out as an empty dictionary.
literal_table = {}

# It's necessary to bundle each regex along with its token and ID,
# to identify exactly what we matched to and be able to print output.
master_regex = '|'.join(f'(?P<{group}__{_id}>{regex})' for (regex, group, _id) in groups)

# According to out understanding, it is at this stage that literals
# are assigned addresses. Addresses start at data location 0001.
address = 1

def open_output_file():
    # Since we're appending to the file, we need to make sure that if it exists,
    # it's empty first.
    # We're appending because we'd like partial results even in case of failure, for some reason,
    # or to see progress in the middle.
    op = open('./lex_output/tokens.txt', 'w')
    op.write('')
    op.close()
    op = open('./lex_output/tokens.txt', 'a')
    return op

def handle_literal(token_type: str, token_val: str):
    global address
    # Duplicates could not exist anyway in a dictionary, but this check serves to
    # guarantee that memory (our VM's memory that will be populated at the level of the
    # interpreter) isn't wasted in the case of duplicate literals.
    if token_val not in literal_table: literal_table[token_val] = address
    address += 1

def handle_symbol(token_val: str):
    # Duplicate symbols are not handled, necessarily, because scoping is still ahead of us.
    # Other than a a symbol being a user-defined identifier, we have no information at this stage
    # about its attributes (type, value, parameters for a function, etc.).
    symbol_table[token_val] = {'symbol_type': 'IDENT', 'attributes': {}}

def lex(code_line: str, line_number: int):
    # Given a line of code, find all matches.
    for res in re.finditer(master_regex, code_line):
        write = True
        # Get the token type and ID from the groupname.
        [token_type, token_id] = res.lastgroup.split('__')
        token_val = res.group()
        # We are handling reserved words by first checking whether they exist in the symbol table as a reserved word
        # as opposed to matching them as identifiers first then checking if they're reserved.
        # This is because our reserved words cannot be described in the same way as our identifiers.
        if token_val in symbol_table and symbol_table[token_val]['symbol_type'] == 'RESERVED':
            pass
        elif token_type == 'IDENT':
            # If we've encountered an identifier (variable, constant, or function),
            # handle them at the level of the symbol table.
            handle_symbol(token_val)
        elif token_type[-3:] == 'LIT':
            # If it's a literal (NUM_LIT, CHAR_LIT, STR_LIT), handle it at the level of the literal table.
            handle_literal(token_type, token_val)
        elif token_type == 'CMNT' or token_type == 'WHTSPC':
            # `write` flag controls says whether a token is to be skipped or written to output file.
            # Comments and whitespaces are skipped.
            write = False
        elif not res:
            # If a lexeme cannot be matched, there must be an error, so terminate the program immediately.
            raise RuntimeError(f'INVALID LEXEME FOUND ON LINE {line_number}: {token_val}! Aborting.')
        # If a match has been found, yield a corresponding message.
        yield write and f'Line {line_number} Token #{token_id} ({token_type}) : {token_val}\n'
        
def main(filepath: str, default: bool) -> None:
    if default:
        # Only retrieve default code if we have to.
        code = constants.get_default_code()
    else:
        try:
            # Get the input code.
            input_file = open(filepath, 'r')
            code = input_file.read().strip()
        except:
            sys.exit('Given HLPL file does not exist. Aborting.')

    # Open the output file.
    tokens_file = open_output_file()
    # We'd like to keep track of line numbers, so we're scanning the code line by line.
    code = code.split('\n')
    for number, line in enumerate(code):
        # Resulting tokens on that line are written to the file immediately
        [tokens_file.write(result) for result in lex(line, number+1) if result]
    tokens_file.close()

    # At this point, the literal table and symbol table have been filled,
    # now save them as JSON files in the output folder.
    with open('./lex_output/symbol.json', 'w') as op:
        op.write(json.dumps(symbol_table, indent=4))
    with open('./lex_output/literal.json', 'w') as op:
        op.write(json.dumps(literal_table, indent=4))

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        # If no input file was given as a CL arg, default code from constants.py is used.
        print('No HLPL input file provided, proceeding with default code.')
        default = True
    else:
        # Otherwise, we proceed with that file.
        filepath = sys.argv[1]
    main(filepath, default)
    print("Lexing done. Open tokens.txt.")
