""" Main executable for JackShenC compiler. For usage, run "./main.py --help" """

import argparse
import sys
import lexer

from errors import error_collector, CompilerError
from il_gen import ILCode, SymbolTable, Context
from myparser.myparser import parse
from asm_gen import ASMCode, MASMCode, ASMGen


def main():
    """ Run the main compiler script """

    arguments = get_arguments()

    code, filename = read_file(arguments)
    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    token_list = lexer.tokenize(code, filename)
    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    ast_root = parse(token_list)
    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    il_code = ILCode()
    symbol_table = SymbolTable()
    ast_root.make_il(il_code, symbol_table, Context())
    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    # Display the IL generated if indicated on the command line.
    if arguments.show_il: print(str(il_code))

    # Display the tokens generated if indicated on the command line.
    if arguments.show_tokens: print(token_list)

    # Display the AST generated if indicated on the command line.
    if arguments.show_tree: print(ast_root)

    asm_code, masm_code = ASMCode(), MASMCode()
    ASMGen(il_code, symbol_table, asm_code, arguments).make_asm()
    ASMGen(il_code, symbol_table, masm_code, arguments).make_asm()
    masm_source = masm_code.full_code()

    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    masm_filename = "TestProgram.asm"
    write_asm(masm_source, masm_filename)
    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    error_collector.show()
    # print("Token list: ", token_list)
    input("The program finished successfully!\nPress Any Key To Exit...")

    return 0


def get_arguments():
    """Get the command-line arguments. This function sets up the argument myparser and returns an object storing the
    argument values (as returned by argparse.parse_args()).
    """
    parser = argparse.ArgumentParser(description="Compile C files.")

    # The file name of the C file to compile.
    parser.add_argument("-filename", dest="filename", action="store_true")

    # Boolean flag for whether to print the generated IL
    parser.add_argument("-show-il", help="display generated IL", dest="show_il", action="store_true")

    # Boolean flag for whether to print the generated tokens
    parser.add_argument("-show-tokens", help="display generated tokens", dest="show_tokens", action="store_true")

    # Boolean flag for whether to print the generated AST
    parser.add_argument("-show-tree", help="display generated AST", dest="show_tree", action="store_true")

    # Boolean flag for whether to print register allocator performance info
    parser.add_argument("-show-reg-alloc-perf", help="display register allocator performance info",
                        dest="show_reg_alloc_perf", action="store_true")

    # Boolean flag for whether to allocate any variables in registers
    parser.add_argument("-variables-on-stack", help="allocate all variables on the stack",
                        dest="variables_on_stack", action="store_true")

    parser.set_defaults(filename="TestProgram.c")
    parser.set_defaults(show_il=False)
    parser.set_defaults(show_tokens=False)
    parser.set_defaults(show_tree=False)

    return parser.parse_args()


def read_file(arguments):
    """ Read the file(s) in arguments and return the file contents """
    try:
        with open(arguments.filename) as c_file:
            return c_file.read(), arguments.filename
    except IOError:
        descr = "could not read file: '{}'"
        error_collector.add(CompilerError(descr.format(arguments.filename)))


def write_asm(asm_source, asm_filename):
    """Save the given assembly source to disk at asm_filename.
        asm_source (str) - Full assembly source code.
        asm_filename (str) - Filename to which to save the generated assembly.
    """
    try:
        with open(asm_filename, "w") as s_file:
            s_file.write(asm_source)
    except IOError:
        descr = "could not write output file '{}'"
        error_collector.add(CompilerError(descr.format(asm_filename)))


if __name__ == "__main__":
    sys.exit(main())
