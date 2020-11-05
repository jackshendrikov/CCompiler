"""Main executable for JackShenC compiler. For usage, run "./main.py --help"."""
import subprocess
import argparse
import sys

from errors import error_collector, CompilerError
from il_gen import ILCode, SymbolTable, Context
from asm_gen import ASMCode, ASMGen, MASMCode
from myparser.myparser import parse
from lexer import tokenize


def main():
    """Run the main compiler script."""

    arguments = get_arguments()
    code, filename = read_file(arguments)
    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    token_list = tokenize(code, filename)
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
    ast_root.make_il(il_code, SymbolTable(), Context())
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
    ASMGen(il_code, asm_code, arguments).make_asm()
    ASMGen(il_code, masm_code, arguments).make_asm()
    asm_source, masm_source = asm_code.full_code(), masm_code.full_code()

    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    masm_filename = "5-25-Python-IO-82-Shendrikov.asm"
    write_asm(masm_source, masm_filename)
    if not error_collector.ok():
        error_collector.show()
        input("\nPress Any Key To Exit...")
        return 1

    # asm_filename = "out.s"
    # write_asm(asm_source, asm_filename)
    # if not error_collector.ok():
    #     error_collector.show()
    #     return 1
    #
    # assemble_and_link("out", asm_filename, "out.o")
    # if not error_collector.ok():
    #     error_collector.show()
    #     return 1

    error_collector.show()
    print("Token list: ", token_list)
    input("\nThe program finished successfully!\nPress Any Key To Exit...")

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

    parser.set_defaults(filename="5-25-Python-IO-82-Shendrikov.txt")
    parser.set_defaults(show_il=False)
    parser.set_defaults(show_tokens=False)
    parser.set_defaults(show_tree=False)

    return parser.parse_args()


def read_file(arguments):
    """Read the file(s) in arguments and return the file contents."""
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


def assemble_and_link(binary_name, asm_name, obj_name):
    """Assemble and link the assembly file into an object file and binary. If the assembly/linking fails,
    raise an exception.
        binary_name (str) - Name of the binary file to output.
        asm_name (str) - Name of the assembly file to read in.
        obj_name (str) - Name of the obj file to output.
    """
    try:
        subprocess.check_call(["nasm", "-f", "elf64", "-o", obj_name, asm_name])
    except subprocess.CalledProcessError:
        error_collector.add(CompilerError("assembler returned non-zero status"))
    else:
        try:
            subprocess.check_call(["ld", "-dynamic-linker", "/lib64/ld-linux-x86-64.so.2",
                                   "/usr/lib/x86_64-linux-gnu/crt1.o", "/usr/lib/x86_64-linux-gnu/crti.o",
                                   "-lc", obj_name, "/usr/lib/x86_64-linux-gnu/crtn.o", "-o", binary_name])
        except subprocess.CalledProcessError:
            error_collector.add(CompilerError("linker returned non-zero status"))


if __name__ == "__main__":
    sys.exit(main())
