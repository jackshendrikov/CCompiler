"""This module defines and implements classes representing assembly commands. The ASMCommand object is the base class
for most ASM commands. Some commands inherit from ASMCommandMultiSize or JumpCommand instead.
"""


class ASMCommand:
    """Base class for a standard ASMCommand, like `add` or `imul`. This class is used for ASM commands which take
    arguments of the same size.
    """

    name = None

    def __init__(self, dest=None, source=None, size=None):
        self.dest = dest.asm_str(size) if dest else None
        self.source = source.asm_str(size) if source else None
        self.size = size

    def __str__(self):
        s = "\t" + self.name
        if self.dest: s += " " + self.dest
        if self.source: s += ", " + self.source
        return s


class ASMCommandMultiSize:
    """Base class for an ASMCommand which takes arguments of different sizes. For example, `movsx` and `movzx`."""

    name = None

    def __init__(self, dest, source, source_size, dest_size):
        self.dest = dest.asm_str(source_size)
        self.source = source.asm_str(dest_size)
        self.source_size = source_size
        self.dest_size = dest_size

    def __str__(self):
        s = "\t" + self.name
        if self.dest: s += " " + self.dest
        if self.source: s += ", " + self.source
        return s


class JumpCommand:
    """Base class for jump commands."""

    name = None

    def __init__(self, target):
        self.target = target

    def __str__(self):
        s = "\t" + self.name + " " + self.target
        return s


class Comment:
    """Class for comments."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "\t;; " + self.msg


class Label:
    """Class for label."""

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label + ":"


class LabelFunc:
    """Class for start of function definition label."""

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label + " PROC"


class LabelEndFunc:
    """Class for end of function label."""

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label + " ENDP\n"


class Lea:
    """Class for lea command."""

    name = "lea"

    def __init__(self, dest, source):
        self.dest = dest
        self.source = source

    def __str__(self):
        return ("\t" + self.name + " " + self.dest.asm_str(4) + ", "
                "" + self.source.asm_str(0))


class Je(JumpCommand): name = "je"
class Jne(JumpCommand): name = "jne"
class Jg(JumpCommand): name = "jg"
class Jge(JumpCommand): name = "jge"
class Jl(JumpCommand): name = "jl"
class Jle(JumpCommand): name = "jle"
class Ja(JumpCommand): name = "ja"
class Jae(JumpCommand): name = "jae"
class Jb(JumpCommand): name = "jb"
class Jbe(JumpCommand): name = "jbe"
class Jmp(JumpCommand): name = "jmp"
class Movsx(ASMCommandMultiSize): name = "movsx"
class Movzx(ASMCommandMultiSize): name = "movzx"
class Mov(ASMCommand): name = "mov"
class BitwiseAnd(ASMCommand): name = "and"
class Add(ASMCommand): name = "add"
class Sub(ASMCommand): name = "sub"
class Neg(ASMCommand): name = "neg"
class Not(ASMCommand): name = "not"
class Div(ASMCommand): name = "div"
class Imul(ASMCommand): name = "imul"
class Idiv(ASMCommand): name = "idiv"
class Cdq(ASMCommand): name = "cdq"
class Cqo(ASMCommand): name = "cqo"
class Xor(ASMCommand): name = "xor"
class Cmp(ASMCommand): name = "cmp"
class Pop(ASMCommand): name = "pop"
class Push(ASMCommand): name = "push"
class Call(ASMCommand): name = "call"
class Ret(ASMCommand): name = "ret"
class Sar(ASMCommandMultiSize): name = "sar"
class Sal(ASMCommandMultiSize): name = "sal"
