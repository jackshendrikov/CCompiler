"""IL commands for labels, jumps, and function calls."""

from il_cmds.base import ILCommand
from spots import LiteralSpot
import asm_cmds
import spots


class Label(ILCommand):
    """Label - Analogous to an ASM label."""

    def __init__(self, label):
        """The label argument is an string label name unique to this label."""
        self.label = label

    def inputs(self):
        return []

    def outputs(self):
        return []

    def label_name(self):
        return self.label

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        asm_code.add(asm_cmds.Label(self.label))


class Jump(ILCommand):
    """Jumps unconditionally to a label."""

    def __init__(self, label):
        self.label = label

    def inputs(self):
        return []

    def outputs(self):
        return []

    def targets(self):
        return [self.label]

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        asm_code.add(asm_cmds.Jmp(self.label))


class _GeneralJump(ILCommand):
    """General class for jumping to a label based on condition."""

    # ASM command to output for this jump IL command.
    asm_cmd = None

    def __init__(self, cond, label):
        self.cond = cond
        self.label = label

    def inputs(self):
        return [self.cond]

    def outputs(self):
        return []

    def targets(self):
        return [self.label]

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        size = self.cond.ctype.size

        if isinstance(spotmap[self.cond], LiteralSpot):
            r = get_reg()
            asm_code.add(asm_cmds.Mov(r, spotmap[self.cond], size))
            cond_spot = r
        else:
            cond_spot = spotmap[self.cond]

        zero_spot = LiteralSpot("0")
        asm_code.add(asm_cmds.Cmp(cond_spot, zero_spot, size))
        asm_code.add(self.command(self.label))


class JumpZero(_GeneralJump):
    """Jumps to a label if given condition is zero."""

    command = asm_cmds.Je


class JumpNotZero(_GeneralJump):
    """Jumps to a label if given condition is zero."""

    command = asm_cmds.Jne


class Return(ILCommand):
    """RETURN - returns the given value from function.

    If arg is None, then returns from the function without putting any value in the return register. Today, only
    supports values that fit in one register.
    """

    def __init__(self, arg=None):
        # arg must already be cast to return type
        self.arg = arg

    def inputs(self):
        return [self.arg]

    def outputs(self):
        return []

    def clobber(self):
        return [spots.RAX]

    def abs_spot_pref(self):
        return {self.arg: [spots.RAX]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        if self.arg and spotmap[self.arg] != spots.RAX:
            size = self.arg.ctype.size
            asm_code.add(asm_cmds.Mov(spots.RAX, spotmap[self.arg], size))

        asm_code.add(asm_cmds.Mov(spots.RSP, spots.RBP, 8))
        asm_code.add(asm_cmds.Pop(spots.RBP, None, 8))
        asm_code.add(asm_cmds.Ret())


class Call(ILCommand):
    """Call a given function.
        func - Pointer to function.
        args - Arguments of the function, in left-to-right order. Must match the parameter types the function expects.
        ret - If function has non-void return type, IL value to save the return value. Its type must match the function
        return value.
    """

    arg_regs = [spots.RDI, spots.RSI, spots.RDX, spots.RCX]

    def __init__(self, func, args, ret):
        self.func = func
        self.args = args
        self.ret = ret
        self.void_return = self.func.ctype.arg.ret.is_void()

        if len(self.args) > len(self.arg_regs):
            raise NotImplementedError("too many arguments")

    def inputs(self):
        return [self.func] + self.args

    def outputs(self):
        return [] if self.void_return else [self.ret]

    def clobber(self):
        # All caller-saved registers are clobbered by function call
        return [spots.RAX, spots.RCX, spots.RDX, spots.RSI, spots.RDI]

    def abs_spot_pref(self):
        prefs = {} if self.void_return else {self.ret: [spots.RAX]}
        for arg, reg in zip(self.args, self.arg_regs):
            prefs[arg] = [reg]

        return prefs

    def abs_spot_conf(self):
        # We don't want the function pointer to be in the same register as an argument will be placed into.
        return {self.func: self.arg_regs[0:len(self.args)]}

    def indir_write(self):
        return self.args

    def indir_read(self):
        return self.args

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        func_spot = spotmap[self.func]

        func_size = self.func.ctype.size
        ret_size = self.func.ctype.arg.ret.size

        # Check if function pointer spot will be clobbered by moving the arguments into the correct registers.
        if spotmap[self.func] in self.arg_regs[0:len(self.args)]:
            # Get a register which isn't one of the unallowed registers.
            r = get_reg([], self.arg_regs[0:len(self.args)])
            asm_code.add(asm_cmds.Mov(r, spotmap[self.func], func_size))
            func_spot = r

        for arg, reg in zip(self.args, self.arg_regs):
            if spotmap[arg] == reg:
                continue
            asm_code.add(asm_cmds.Mov(reg, spotmap[arg], arg.ctype.size))

        asm_code.add(asm_cmds.Call(func_spot, None, self.func.ctype.size))

        if not self.void_return and spotmap[self.ret] != spots.RAX:
            asm_code.add(asm_cmds.Mov(spotmap[self.ret], spots.RAX, ret_size))
