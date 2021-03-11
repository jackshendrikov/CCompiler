""" IL commands for mathematical operations """

from il_cmds.base import ILCommand
import asm_cmds
import spots


class AddMult(ILCommand):
    """ Base class for ADD, MULT, and SUB """

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

    def rel_spot_preference(self):
        return {self.output: [self.arg1, self.arg2]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        """ Make the ASM for ADD, MULT, and SUB """
        ctype = self.arg1.ctype
        size = ctype.size

        arg1_spot = spotmap[self.arg1]
        arg2_spot = spotmap[self.arg2]

        # Get temp register for computation.
        temp = get_reg([spotmap[self.output], arg1_spot, arg2_spot])

        if temp == arg1_spot:
            asm_code.add(self.Inst(temp, arg2_spot, size))
        elif temp == arg2_spot:
            asm_code.add(self.Inst(temp, arg1_spot, size))
            if not self.comm: asm_code.add(asm_cmds.Neg(temp, None, size))

        else:
            asm_code.add(asm_cmds.Mov(temp, arg1_spot, size))
            asm_code.add(self.Inst(temp, arg2_spot, size))

        if temp != spotmap[self.output]: asm_code.add(asm_cmds.Mov(spotmap[self.output], temp, size))


class BitwiseAnd(AddMult):
    """ BitwiseAnd - make bitwise AND operation with arg1 and arg2, then saves to output.
     IL values output, arg1, arg2 must all have the same type. No type conversion or promotion is done here.
     """
    comm = True
    Inst = asm_cmds.BitwiseAnd


class Add(AddMult):
    """ Adds arg1 and arg2, then saves to output.
    IL values output, arg1, arg2 must all have the same type. No type conversion or promotion is done here.
    """
    comm = True
    Inst = asm_cmds.Add


class Subtr(AddMult):
    """ Subtracts arg1 and arg2, then saves to output.
    ILValues output, arg1, and arg2 must all have types of the same size.
    """
    comm = False
    Inst = asm_cmds.Sub


class Mult(AddMult):
    """ Multiplies arg1 and arg2, then saves to output.
    IL values output, arg1, arg2 must all have the same type. No type conversion or promotion is done here.
    """
    comm = True
    Inst = asm_cmds.Imul


class BitShiftCmd(ILCommand):
    """ Base class for bitwise shift commands """

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

    def clobber(self):
        return [spots.ECX]

    def abs_spot_preference(self):
        return {self.arg2: [spots.ECX]}

    def rel_spot_preference(self):
        return {self.output: [self.arg1]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        arg1_spot = spotmap[self.arg1]
        arg1_size = self.arg1.ctype.size
        arg2_spot = spotmap[self.arg2]
        arg2_size = self.arg2.ctype.size

        if not self.is_immediate8(arg2_spot) and arg2_spot != spots.ECX:
            if arg1_spot == spots.ECX:
                out_spot = spotmap[self.output]
                temp_spot = get_reg([out_spot, arg1_spot], [arg2_spot, spots.ECX])
                asm_code.add(asm_cmds.Mov(temp_spot, arg1_spot, arg1_size))
                arg1_spot = temp_spot
            asm_code.add(asm_cmds.Mov(spots.ECX, arg2_spot, arg2_size))
            arg2_spot = spots.ECX

        if spotmap[self.output] == arg1_spot: asm_code.add(self.Inst(arg1_spot, arg2_spot, arg1_size, 1))
        else:
            out_spot = spotmap[self.output]
            temp_spot = get_reg([out_spot, arg1_spot], [arg2_spot])
            if arg1_spot != temp_spot: asm_code.add(asm_cmds.Mov(temp_spot, arg1_spot, arg1_size))
            asm_code.add(self.Inst(temp_spot, arg2_spot, arg1_size, 1))
            if temp_spot != out_spot: asm_code.add(asm_cmds.Mov(out_spot, temp_spot, arg1_size))


class RBitShift(BitShiftCmd):
    """ Right bitwise shift operator for IL value.
    Shifts each bit in IL value left operand to the right by position indicated by right operand."""
    Inst = asm_cmds.Sar


class LBitShift(BitShiftCmd):
    """ Left bitwise shift operator for IL value.
    Shifts each bit in IL value left operand to the left by position indicated by right operand."""
    Inst = asm_cmds.Sal


class DivMod(ILCommand):
    """ Base class for ILCommand Div and Mod """

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
        return [spots.EAX, spots.EDX]

    def abs_spot_conflict(self):
        return {self.arg2: [spots.EDX, spots.EAX]}

    def abs_spot_preference(self):
        return {self.output: [self.return_reg], self.arg1: [spots.EAX]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        ctype = self.arg1.ctype
        size = ctype.size

        output_spot = spotmap[self.output]
        arg1_spot = spotmap[self.arg1]
        arg2_spot = spotmap[self.arg2]

        # Move first operand into RAX if we can do so without clobbering other argument
        moved_to_rax = False
        if spotmap[self.arg1] != spots.EAX and spotmap[self.arg2] != spots.EAX:
            moved_to_rax = True
            asm_code.add(asm_cmds.Mov(spots.EAX, arg1_spot, size))

        # If the divisor is a literal or in a bad register, we must move it to a register.
        if self.is_immediate(spotmap[self.arg2]) or spotmap[self.arg2] in [spots.EAX, spots.EDX]:
            r = get_reg([], [spots.EAX, spots.EDX])
            asm_code.add(asm_cmds.Mov(r, arg2_spot, size))
            arg2_final_spot = r
        else:
            arg2_final_spot = arg2_spot

        # If we did not move to RAX above, do so here.
        if not moved_to_rax and arg1_spot != self.return_reg: asm_code.add(asm_cmds.Mov(spots.EAX, arg1_spot, size))

        if ctype.signed:
            if ctype.size == 4: asm_code.add(asm_cmds.Cdq())
            elif ctype.size == 8: asm_code.add(asm_cmds.Cqo())
            asm_code.add(asm_cmds.Idiv(arg2_final_spot, None, size))
        else:
            # zero out RDX register
            asm_code.add(asm_cmds.Xor(spots.EDX, spots.EDX, size))
            asm_code.add(asm_cmds.Div(arg2_final_spot, None, size))

        if spotmap[self.output] != self.return_reg:
            asm_code.add(asm_cmds.Mov(output_spot, self.return_reg, size))


class Div(DivMod):
    """ Divides given IL values.
    IL values output, arg1, arg2 must all have the same type of size at least int. No type conversion or promotion is
    done here.
    """
    return_reg = spots.EAX


class Mod(DivMod):
    """ Divides given IL values.
    IL values output, arg1, arg2 must all have the same type of size at least int. No type conversion or promotion is
    done here.
    """
    return_reg = spots.EDX


class NegNot(ILCommand):
    """ Base class for NEG and NOT """

    # The ASM instruction to generate for this command. Override this value in subclasses.
    Inst = None

    def __init__(self, output, arg):
        self.output = output
        self.arg = arg

    def inputs(self):
        return [self.arg]

    def outputs(self):
        return [self.output]

    def rel_spot_preference(self):
        return {self.output: [self.arg]}

    def make_asm(self, spotmap, home_spots, get_reg, asm_code):
        size = self.arg.ctype.size

        output_spot = spotmap[self.output]
        arg_spot = spotmap[self.arg]

        if output_spot != arg_spot: asm_code.add(asm_cmds.Mov(output_spot, arg_spot, size))
        asm_code.add(self.Inst(output_spot, None, size))


class Neg(NegNot):
    """ Negates given IL value """
    Inst = asm_cmds.Neg


class Not(NegNot):
    """ Logically negates each bit of given IL value """
    Inst = asm_cmds.Not
