"""Objects for the IL->ASM stage of the compiler."""

from il_gen import ILValue
from spots import Spot
from re import findall


class ASMCode:
    """Stores the ASM code generated from the IL code.
        lines (List) - Lines of ASM code recorded. The commands are stored as tuples in this list, where the first value
        is the name of the command and the next values are the command arguments.
    """

    def __init__(self):
        """Initialize ASMCode."""
        self.lines = []

    def add_command(self, command, arg1=None, arg2=None):
        """Add a command to the code.
            command (str) - Name of the command to add.
            arg1 (str) - First argument of the command.
            arg2 (str) - Second argument of the command.
        """
        self.lines.append((command, arg1, arg2))

    @staticmethod
    def to_label(label):
        """Given a label integer, produce the full label name."""
        return "__JackShenC_label" + str(label)

    def add_label(self, label):
        """Add a label to the code.
            label (str) - The label string to add.
        """
        self.lines.append(label)

    def full_code(self):
        """Produce the full assembly code.
            return (str) - The assembly code, ready for saving to disk and assembling.
        """

        def to_string(line):
            """Convert the provided tuple/string into a string of nasm code. Does not terminate with a newline."""
            if isinstance(line, str):
                return line + ":"
            else:
                line_str = "\t" + line[0]
                if line[1]: line_str += " " + line[1]
                if line[2]: line_str += ", " + line[2]
                return line_str

        # This code starts every nasm program so far
        header = ["global main", "", "main:"]

        return "\n".join(header + [to_string(line) for line in self.lines])


class MASMCode(ASMCode):
    def full_code(self):
        """Produce the full assembly code.
            return (str) - The assembly code, ready for saving to disk and assembling.
        """

        def to_string(line):
            """Convert the provided tuple/string into a string of masm code. Does not terminate with a newline."""
            if isinstance(line, str):
                return line + ":"
            else:
                line_str = "\t" + line[0]
                if line[1]: line_str += " " + line[1]
                if line[2]: line_str += ", " + line[2]
                return line_str

        # This code starts every masm program
        header = [".386",
                  ".model flat, stdcall",
                  "option casemap:none\n",
                  "include \\masm32\\include\\windows.inc",
                  "include \\masm32\\include\\kernel32.inc",
                  "include \\masm32\\include\\masm32.inc",
                  "include \\masm32\\include\\user32.inc",
                  "includelib \\masm32\\lib\\kernel32.lib",
                  "includelib \\masm32\\lib\\masm32.lib",
                  "includelib \\masm32\\lib\\user32.lib\n",
                  "NumbToStr PROTO :DWORD, :DWORD",
                  "main PROTO\n",
                  ".const",
                  "?BASE\n",
                  ".data",
                  "Caption db \"Result\", 0",
                  "Output db 11 dup(?), 0\n",
                  ".code",
                  "NumbToStr PROC uses eax x:DWORD, buffer:DWORD",
                  "\tmov ebx, buffer",
                  "\tmov ecx, 10",
                  "@loop:",
                  "\txor edx, edx",
                  "\tdiv BASE",
                  "\tdec ecx",
                  "\tadd edx, 48",
                  "\tjl @store",
                  "@store:",
                  "\tmov BYTE PTR [ebx+ecx], dl",
                  "\tcmp ecx, 0",
                  "\tjnz @loop",
                  "\tret",
                  "NumbToStr ENDP\n",
                  "main PROC"]

        footer = ["main ENDP",
                  "\nstart:",
                  "\tinvoke main",
                  "\tinvoke NumbToStr, eax, ADDR Output",
                  "\tinvoke MessageBoxA, 0, ADDR Output, ADDR Caption, 0",
                  "\tinvoke ExitProcess, 0",
                  "end start\n"]

        masm_code = "\n".join(header + [to_string(line) for line in self.lines] + footer)

        # Generate the base of the output number
        if len(findall(r'[01]+B', masm_code)) > 0 or len(findall(r'-[01]+B', masm_code)) > 0:
            masm_code = masm_code.replace('?BASE', 'BASE dd 2')
        else:
            masm_code = masm_code.replace('?BASE', 'BASE dd 10')

        return masm_code


class ASMGen:
    """Contains the main logic for generation of the ASM from the IL.
        il_code (ILCode) - IL code to convert to ASM.
        asm_code (ASMCode) - ASMCode object to populate with ASM.
    """

    def __init__(self, il_code, asm_code, masm_code):
        """Initialize ASMGen."""
        self.il_code = il_code
        self.asm_code = asm_code
        self.masm_code = masm_code

    def make_asm(self):
        """Generate NASM code. Uses the ASMCode and ILCode objects passed to the constructor."""
        # Generate spotmap where each value is stored somewhere on the stack.
        all_values = self.all_il_values()

        offset, spotmap = 0, {}
        for value in all_values:
            if value.value_type == ILValue.LITERAL:
                spotmap[value] = Spot(Spot.LITERAL, value.value)
            else:
                offset += value.ctype.size
                spotmap[value] = Spot(Spot.STACK, -offset)

        # Back up rbp and move rsp
        self.asm_code.add_command("push", "rbp")
        self.asm_code.add_command("mov", "rbp", "rsp")
        self.asm_code.add_command("sub", "rsp", str(offset))

        # Generate all asm code
        for command in self.il_code:
            command.make_asm(spotmap, self.asm_code)

    def make_masm(self):
        """Generate MASM code. Uses the ASMCode and ILCode objects passed to the constructor."""
        # Generate spotmap where each value is stored somewhere on the stack.
        all_values = self.all_il_values()

        offset, spotmap = 0, {}
        for value in all_values:
            if value.value_type == ILValue.LITERAL:
                spotmap[value] = Spot(Spot.LITERAL, value.value)
            else:
                offset += value.ctype.size
                spotmap[value] = Spot(Spot.STACK, -offset)

        # Back up ebp and move esp
        self.masm_code.add_command("push", "ebp")
        self.masm_code.add_command("mov", "ebp", "esp")
        self.masm_code.add_command("sub", "esp", str(offset))

        # Generate all masm code
        for command in self.il_code:
            command.make_masm(spotmap, self.masm_code)

    def all_il_values(self):
        """Return a list of all IL values that appear in the IL code."""
        all_values = []
        for command in self.il_code:
            for value in command.input_values() + command.output_values():
                if value not in all_values:
                    all_values.append(value)

        return all_values
