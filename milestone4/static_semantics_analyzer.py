import parse
import sys, os
sys.path.append(os.path.abspath('../milestone3'))

symbol_table = {}
literal_table = {}
current_scope = None

# Input: CST. Format is very crucial. Preferred option: run parser from here, like we did with lexer

# 1) Define before use
# 2) Type checking
# 3) CST --> AST: should be done simultaneously with other tasks?

def main():
    # get symbol and literal tables from ../milestone3/lex_output/

    # traverse AST: postfix traversal
    # for each var/const declaration and function definition, add info to ST
    # for each subsequent reference, check to see if under the current scope,
    #   the declaration/definition exists

    # think of operations involving type checking, and whenever one is encountered, retrieve
    # operands
    # also: function params & args need to match in number and type
    pass

if __name__ == '__main__':
    main()