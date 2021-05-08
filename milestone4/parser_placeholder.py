#from ..milestone3.lex import main as generate   # Can't get this to work
import sys
import os
sys.path.append(os.path.abspath('../milestone3'))
from lex import main as generate

def main(file, default, from_parser):
    token_gen = generate(file, default, from_parser)
    for token in token_gen:
        print(token)
    print("Do the parsing...")

if __name__ == '__main__':
    default = False
    filepath = ''
    if len(sys.argv) < 2:
        print('No HLPL input file provided for parsing, proceeding with default code.')
        default = True
    else:
        filepath = sys.argv[1]
    main(filepath, default, from_parser=True)
    print("Parsing done.")
