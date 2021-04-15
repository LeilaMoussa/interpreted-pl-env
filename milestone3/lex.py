import sys
import io
import re

tokens = {}  # list all our token as named constants and corresponding IDs
next_token = ''
symbol_table = {}
literal_table = {}  # doesn't have to be dict(), can use other classes
# how to define the REs?

def main(filepath: str):
    token_stream = io.StringIO()  # assuming tokens as strings for now, maybe not
    # StringIO() can take initial data as a param
    try:
        input_file = open(filepath, 'r')
        data = input_file.read()
        # print(data)
    except:
        sys.exit('File does not exist.')

    # Handy methods:
    # token_stream.write('first token ')
    # contents = token_stream.getvalue()

    token_stream.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('No input file provided, aborting.')
    filepath = sys.argv[1]
    main(filepath)
