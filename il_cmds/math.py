"""IL commands for mathematical operations."""

from il_cmds.base import ILCommand
import asm_cmds
import spots


class AddMult(ILCommand):
    """Base class for ADD, MULT, and SUB."""

    # Indicates whether this instruction is commutative. If not, a "neg" instruction is inserted when the order is
    # flipped. Override this value in subclasses.
    comm = False

    # The ASM instruction to generate for this command. Override this value in subclasses.
    Inst = None

    def __init__(self, output, arg1, arg2):
        self.output = output
        self.arg1 = arg1
        self.arg2 = arg2

    def inputs(self):
        return [self.arg1, self.arg2]

    def outputs(self):
        return [self.output]

    def rel_spot_pref(self):
        return {self.output: [self.arg1, self.arg2]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        """Make the ASM for ADD, MULT, and SUB."""
        ctype = self.arg1.ctype
        size = ctype.size

        arg1_spot = spotmap[self.arg1]
        arg2_spot = spotmap[self.arg2]

        # Get temp register for computation.
        temp = get_reg([spotmap[self.output], arg1_spot, arg2_spot])

        if temp == arg1_spot:
            if not self._is_imm64(arg2_spot):
                asm_code.add(self.Inst(temp, arg2_spot, size))
            else:
                temp2 = get_reg([], [temp])
                asm_code.add(asm_cmds.Mov(temp2, arg2_spot, size))
                asm_code.add(self.Inst(temp, temp2, size))
        elif temp == arg2_spot:
            if not self._is_imm64(arg1_spot):
                asm_code.add(self.Inst(temp, arg1_spot, size))
            else:
                temp2 = get_reg([], [temp])
                asm_code.add(asm_cmds.Mov(temp2, arg1_spot, size))
                asm_code.add(self.Inst(temp, temp2, size))

            if not self.comm:
                asm_code.add(asm_cmds.Neg(temp, None, size))

        else:
            if not self._is_imm64(arg1_spot) and not self._is_imm64(arg2_spot):
                asm_code.add(asm_cmds.Mov(temp, arg1_spot, size))
                asm_code.add(self.Inst(temp, arg2_spot, size))
            elif (self._is_imm64(arg1_spot) and
                  not self._is_imm64(arg2_spot)):
                asm_code.add(asm_cmds.Mov(temp, arg1_spot, size))
                asm_code.add(self.Inst(temp, arg2_spot, size))
            elif (not self._is_imm64(arg1_spot) and
                  self._is_imm64(arg2_spot)):
                asm_code.add(asm_cmds.Mov(temp, arg2_spot, size))
                asm_code.add(self.Inst(temp, arg1_spot, size))
                if not self.comm:
                    asm_code.add(asm_cmds.Neg(temp, None, size))

            else:  # both are imm64
                temp2 = get_reg([], [temp])

                asm_code.add(asm_cmds.Mov(temp, arg1_spot, size))
                asm_code.add(asm_cmds.Mov(temp2, arg2_spot, size))
                asm_code.add(self.Inst(temp, temp2, size))

        if temp != spotmap[self.output]:
            asm_code.add(asm_cmds.Mov(spotmap[self.output], temp, size))


class BitwiseAnd(AddMult):
    """BitwiseAnd - make bitwise AND operation with arg1 and arg2, then saves to output.
     IL values output, arg1, arg2 must all have the same type. No type conversion or promotion is done here.
     """
    comm = True
    Inst = asm_cmds.BitwiseAnd


class Add(AddMult):
    """Adds arg1 and arg2, then saves to output.
    IL values output, arg1, arg2 must all have the same type. No type conversion or promotion is done here.
    """
    comm = True
    Inst = asm_cmds.Add


class Subtr(AddMult):
    """Subtracts arg1 and arg2, then saves to output.
    ILValues output, arg1, and arg2 must all have types of the same size.
    """
    comm = False
    Inst = asm_cmds.Sub


class Mult(AddMult):
    """Multiplies arg1 and arg2, then saves to output.
    IL values output, arg1, arg2 must all have the same type. No type conversion or promotion is done here.
    """
    comm = True
    Inst = asm_cmds.Imul


class DivMod(ILCommand):
    """Base class for ILCommand Div and Mod."""

    return_reg = None

    def __init__(self, output, arg1, arg2):
        self.output = output
        self.arg1 = arg1
        self.arg2 = arg2

    def inputs(self):
        return [self.arg1, self.arg2]

    def outputs(self):
        return [self.output]

    def clobber(self):
        return [spots.RAX, spots.RDX]

    def abs_spot_conf(self):
        return {self.arg2: [spots.RDX, spots.RAX]}

    def abs_spot_pref(self):
        return {self.output: [self.return_reg], self.arg1: [spots.RAX]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        ctype = self.arg1.ctype
        size = ctype.size

        output_spot = spotmap[self.output]
        arg1_spot = spotmap[self.arg1]
        arg2_spot = spotmap[self.arg2]

        # Move first operand into RAX if we can do so without clobbering other argument
        moved_to_rax = False
        if spotmap[self.arg1] != spots.RAX and spotmap[self.arg2] != spots.RAX:
            moved_to_rax = True
            asm_code.add(asm_cmds.Mov(spots.RAX, arg1_spot, size))

        # If the divisor is a literal or in a bad register, we must move it to a register.
        if self._is_imm(spotmap[self.arg2]) or spotmap[self.arg2] in [spots.RAX, spots.RDX]:
            r = get_reg([], [spots.RAX, spots.RDX])
            asm_code.add(asm_cmds.Mov(r, arg2_spot, size))
            arg2_final_spot = r
        else:
            arg2_final_spot = arg2_spot

        # If we did not move to RAX above, do so here.
        if not moved_to_rax and arg1_spot != self.return_reg:
            asm_code.add(asm_cmds.Mov(spots.RAX, arg1_spot, size))

        if ctype.signed:
            if ctype.size == 4: asm_code.add(asm_cmds.Cdq())
            elif ctype.size == 8: asm_code.add(asm_cmds.Cqo())
            asm_code.add(asm_cmds.Idiv(arg2_final_spot, None, size))
        else:
            # zero out RDX register
            asm_code.add(asm_cmds.Xor(spots.RDX, spots.RDX, size))
            asm_code.add(asm_cmds.Div(arg2_final_spot, None, size))

        if spotmap[self.output] != self.return_reg:
            asm_code.add(asm_cmds.Mov(output_spot, self.return_reg, size))


class Div(DivMod):
    """Divides given IL values.
    IL values output, arg1, arg2 must all have the same type of size at least int. No type conversion or promotion is
    done here.
    """
    return_reg = spots.RAX


class Mod(DivMod):
    """Divides given IL values.
    IL values output, arg1, arg2 must all have the same type of size at least int. No type conversion or promotion is
    done here.
    """
    return_reg = spots.RDX
