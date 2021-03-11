""" The Spot object definition and some predefined spots, like registers """


class Spot:
    """Spot in the machine where an IL value can be.
        spot_type (enum) - One of the values below describing the general type of spot this is.
        detail - Additional information about this spot. The this attribute's type and meaning depend on the spot_type.
    """

    def __init__(self, detail):
        """ Initialize a spot """
        self.detail = detail

    def asm_str(self, size):
        """Make the ASM form of this spot, for the given size in bytes.
        This function raises NotImplementedError for unsupported sizes.
            Examples:
                spots.EAX.asm_str(4) -> "eax"
                spots.EAX.asm_str(8) -> "eax" -> actually "rax", but for MASM32 I changed it.
                spot(STACK, -16).asm_str(4) -> "DWORD [ebp-16]"
                spot(LITERAL, 14).asm_str(4) -> "14"
            size (int) - Size in bytes of the data stored at this spot.
            return (str) - ASM form of this spot.
        """
        raise NotImplementedError

    def rbp_offset(self):
        """Return this spot's offset from EBP. If this is a memory spot which resides at a certain negative offset
        away from EBP, then return that offset. This is used by the register allocator to figure out how much memory to
        allocate for this spot. If this is not a memory spot relative to EBP, just return 0.
        """
        return 0

    def shift(self, chunk, count=None):
        """Return a new spot shifted relative to this one. For non-memory spots, this function returns itself and throws
        an error if given chunk != 0 or count != None.
        """
        if chunk or count:
            raise NotImplementedError("cannot shift this spot type")
        return self

    def __repr__(self):
        return self.detail

    def __eq__(self, other):
        """ Test equality by comparing Spot type and detail """
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.detail == other.detail

    def __hash__(self):
        """ Hash based on type and detail """
        return hash((self.__class__.__name__, self.detail))


class RegSpot(Spot):
    """ Spot representing a machine register """

    # Mapping from the 32-bit register name to the 32-bit, 16-bit and 8-bit register names for each register.
    reg_map = {"eax": ["eax", "eax", "ax", "al"],
               "ebx": ["ebx", "ebx", "bx", "bl"],
               "ecx": ["ecx", "ecx", "cx", "cl"],
               "edx": ["edx", "edx", "dx", "dl"],
               "esi": ["esi", "esi", "si", "si"],
               "edi": ["edi", "edi", "di", "di"],
               "ebp": ["ebp", "ebp", "", ""],
               "esp": ["esp", "esp", "", ""]}

    def __init__(self, name):
        """Initialize this spot.
            name - string representation of the 32-bit register (e.g. "eax").
        """
        super().__init__(name)
        self.name = name

    def asm_str(self, size):
        if size == 0 or size == 8: i = 0
        elif size == 1: i = 3
        elif size == 2: i = 2
        elif size == 4: i = 1
        else: raise NotImplementedError("unexpected register size")

        return self.reg_map[self.name][i]


class MemSpot(Spot):
    """Spot representing a region in memory, like on stack or .data section.
        base - can be either a string or a Spot. The string form is used when this spot represents an external variable.
        The Spot form is used when this spot represents an offset in memory, like [ebp-5].
    """

    size_map = {1: "BYTE PTR ", 2: "WORD PTR ", 4: "DWORD PTR ", 8: "DWORD PTR "}

    def __init__(self, base, offset=0, block=0, count=None):
        super().__init__((base, offset, block, count))

        self.base = base
        self.offset = offset
        self.block = block
        self.count = count

    def asm_str(self, size):
        if isinstance(self.base, Spot): base_str = self.base.asm_str(0)
        else: base_str = self.base

        total_offset = self.offset
        if not self.count: total_offset = self.offset + self.block

        if total_offset == 0: simple = base_str
        elif total_offset > 0: simple = f"{base_str}+{int(total_offset)}"
        else: simple = f"{base_str}-{int(-total_offset)}"

        if self.count and self.block > 0: final = f"{simple}+{self.block}*{self.count.asm_str(4)}"
        elif self.count and self.block < 0: final = f"{simple}-{-self.block}*{self.count.asm_str(4)}"
        else: final = simple

        size_desc = self.size_map.get(size, "")
        return f"{size_desc}[{final}]"

    def rbp_offset(self):
        if self.base == EBP: return -self.offset
        else: return 0

    def shift(self, block, count=None):
        """Return a new memory spot shifted relative to this one.
            block - A Python integer representing the size of each block of offset.
            count - If provided, a register spot storing the number of blocks to be offset. If this value is provided,
            then `block` must be in {1, 2, 4, 8}.
        """
        if count and self.count:
            raise NotImplementedError("cannot shift by count")

        if count:
            new_offset = self.offset + self.block
            new_block = block
            new_count = count
        else:
            new_offset = self.offset + block
            new_block = self.block
            new_count = self.count

        return MemSpot(self.base, new_offset, new_block, new_count)


class LiteralSpot(Spot):
    """Spot representing a literal value. This is a kind of tricky, since a literal value isn't `really` a storage spot.
    The value attribute is the integer representation of the value of this literal.
    """

    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def asm_str(self, size):
        return str(self.value)


EAX = RegSpot("eax")
ECX = RegSpot("ecx")
EDX = RegSpot("edx")
ESI = RegSpot("esi")
EDI = RegSpot("edi")

registers = [EAX, ECX, EDX, ESI, EDI]

EBP = RegSpot("ebp")
ESP = RegSpot("esp")
