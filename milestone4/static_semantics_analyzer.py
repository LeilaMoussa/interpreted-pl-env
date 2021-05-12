from parse import main as get_cst
import sys, os
import json
from cst import *
from ast import *
sys.path.append(os.path.abspath('../milestone3'))

symbol_table = {}
literal_table = {}
current_scope = None

# Input: CST. Format is very crucial. Preferred option: run parser from here, like we did with lexer

# 1) Define before use
# 2) Type checking
# 3) CST --> AST: should be done simultaneously with other tasks?

# FIRST PRIORITY is to get the AST. Think of the most convenient format for the generator.

# most likely gonna do multiple passes over the tree, but idk about order

def check_declare(tree):
    pass

def check_types(tree):
    pass

def get_ast(cst: ProgramNode):
    pass

def main():
    global symbol_table, literal_table
    # get symbol and literal tables from ../milestone3/lex_output/
    with open('../milestone3/lex_output/symbol_table.json') as f:
        symbol_table = json.load(f)
    with open('../milestone3/lex_output/literal_table.json') as f:
        literal_table = json.load(f)

    cst = get_cst()
    if cst:
        ast = get_ast()
        ast.display()

    # traverse AST: postfix traversal
    # for each var/const declaration and function definition, add info to ST
    # for each subsequent reference, check to see if under the current scope,
    #   the declaration/definition exists

    # think of operations involving type checking, and whenever one is encountered, retrieve
    # operands
    # also: function params & args need to match in number and type

if __name__ == '__main__':
    main()