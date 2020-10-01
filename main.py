"""Main executable for JackShenC (Jack Shendrikov C Compiler)
For usage, run "./main.py --help"."""
# Add argument parsing to main executable
import argparse
import subprocess
import token_kinds

from code_gen import CodeStore
from masm_gen import MasmStore
from errors import CompilerError
from lexer import Lexer
from myparser import Parser


def main():
    """Load the input files and dispatch to the compile function for the main processing.
    The main function handles interfacing with the user, like reading the command line arguments, printing errors,
    and generating output files. The compilation logic is in the compile_code function to facilitate testing.
    """
    arguments = get_arguments()

    # Open and Read C file
    try:
        with open(arguments.file_name) as c_file:
            code_lines = [(line_text.strip(), arguments.file_name, line_num + 1)
                          for line_num, line_text in enumerate(c_file)]
    except IOError:
        raise CompilerError("could not read file: '{}'".format(arguments.file_name))

    # Compile the code
    asm_source = compile_code(code_lines)

    # Open asm file
    try:
        with open("out.s", "w") as s_file: s_file.write(asm_source[0])
        with open("masm.asm", "w") as m_file: m_file.write(asm_source[1])
    except IOError:
        raise CompilerError("could not write output file '{}'".format("out.s"))

    assemble_and_link("out", "out.s", "out.o")


def get_arguments():
    """Set up the argument parser and return an object storing the argument values.

    return - an object storing argument values, as returned by argparse.parse_args()
    """

    parser = argparse.ArgumentParser(description="Compile C files.")

    # The file name of the C file to compile. The file name gets saved to the
    # file_name attribute of the returned object, but this parameter appears as
    # "filename" (no underscore) on the command line.
    parser.add_argument("file_name", metavar="filename")
    return parser.parse_args()


def compile_code(source):
    """Compile the provided source code lines into assembly.

    source_lines (List(tuple)) - annotated lines of source code.
    return (str) - The asm output
    """

    lexer = Lexer(token_kinds.symbol_kinds, token_kinds.keyword_kinds)
    token_list = lexer.tokenize(source)

    parser = Parser()
    ast_root = parser.parse(token_list)

    code_store = CodeStore()
    ast_root.make_code(code_store)

    masm_store = MasmStore()
    ast_root.make_masm(masm_store)

    return code_store.full_code(), masm_store.full_code()


def assemble_and_link(binary_name, asm_name, obj_name):
    """Assemble and link the assembly file into an object file and binary. If the assembly/linking fails, raise an error

    binary_name (str) - name of the binary file to output
    asm_name (str) - name of the assembly file to read in
    obj_name (str) - name of the obj file to output
    """
    # TODO: return errors in a universal way
    subprocess.run(["nasm", "-f", "elf64", "-o", obj_name, asm_name]).check_returncode()
    subprocess.run(["ld", obj_name, "-o", binary_name]).check_returncode()


if __name__ == "__main__":
    try:
        main()
    except CompilerError as e:
        print(e.__str__())
