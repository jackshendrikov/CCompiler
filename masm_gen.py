"""Defines the classes necessary for the code generation step of the compiler."""

from code_gen import CodeStore
from re import findall


class MasmStore(CodeStore):
    def full_code(self):
        """Return as a string the full assembly code generated."""

        def to_string(line):
            """Convert a single line from the `lines` variable into a string of masm code"""
            if isinstance(line, str):
                # It's a label
                return line
            else:
                # It's a command
                return "     " + line[0] + (" " + ", ".join(line[1:]) if len(line) > 1 else "")

        # This code starts every masm program, so we put it here.
        header = [".386",
                  ".model flat, stdcall",
                  "option casemap:none\n",
                  "include     \\masm32\\include\\windows.inc",
                  "include     \\masm32\\include\\kernel32.inc",
                  "include     \\masm32\\include\\masm32.inc",
                  "include     \\masm32\\include\\user32.inc",
                  "includelib  \\masm32\\lib\\kernel32.lib",
                  "includelib  \\masm32\\lib\\masm32.lib",
                  "includelib  \\masm32\\lib\\user32.lib\n",
                  "NumbToStr   PROTO :DWORD, :DWORD",
                  "main        PROTO\n",
                  ".const",
                  "?BASE\n",
                  ".data",
                  "Caption db \"Result\", 0",
                  "Output  db 11 dup(?), 0\n",
                  ".code",
                  "NumbToStr PROC uses eax x:DWORD, buffer:DWORD",
                  "\tmov     ebx, buffer",
                  "\tmov     ecx, 10",
                  "@loop:",
                  "\txor     edx, edx",
                  "\tdiv     BASE",
                  "\tdec     ecx",
                  "\tadd     edx, 48",
                  "\tjl      @store",
                  "@store:",
                  "\tmov     BYTE PTR [ebx+ecx], dl",
                  "\tcmp     ecx, 0",
                  "\tjnz     @loop",
                  "\tret",
                  "NumbToStr ENDP\n"]

        footer = ["\nstart:",
                  "\tinvoke  main",
                  "\tinvoke  NumbToStr, eax, ADDR Output",
                  "\tinvoke  MessageBoxA, 0, ADDR Output, ADDR Caption, 0",
                  "\tinvoke  ExitProcess, 0",
                  "end start\n"]

        masm_code = "\n".join(header + [to_string(line) for line in self.lines] + footer)

        # Generate the base of the output number
        if len(findall(r'[01]+B', masm_code)) > 0:
            masm_code = masm_code.replace('?BASE', 'BASE dd 2')
        else:
            masm_code = masm_code.replace('?BASE', 'BASE dd 10')

        return masm_code
