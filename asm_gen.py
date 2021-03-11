""" Objects for the IL->ASM stage of the compiler """

from spots import Spot, RegSpot, MemSpot, LiteralSpot
from il_cmds.control import DIRECT_VAL
import itertools
import asm_cmds
import spots


class ASMCode:
    """Stores the ASM code generated from the IL code.
        lines (List) - Lines of ASM code recorded. The commands are stored as tuples in this list, where the first value
        is the name of the command and the next values are the command arguments.
    """

    def __init__(self):
        """ Initialize ASMCode """
        self.lines, self.globals, self.data, self.output, self.string_literals, self.invokes = [], [], [], [], [], []

    def add(self, cmd):
        """Add a command to the code.
            cmd (ASMCommand) - Command to add.
        """
        self.lines.append(cmd)

    label_num = 0
    string_exist = False

    @staticmethod
    def get_label():
        """Return a unique label string."""
        ASMCode.label_num += 1
        return f"__JackShenC_label{ASMCode.label_num}"

    def add_global(self, name):
        """Add a name to the code as global.
            name (str) - The name to add.
        """
        self.globals.append(f"{name} PROTO")

    def add_invoke(self, name):
        """Add a name to the code as invoke.
            name (str) - The name to add.
        """
        self.invokes.append(f"\tinvoke {name}")

    def add_output(self, string):
        self.output.append(f"\t\t\t\"{string}\", 0ah,")

    def add_data(self, name, size):
        self.data.append(f"{name} dd {size}")

    def add_res(self, name):
        self.data.append(f"{name} dd ?, 0")

    def add_string_literal(self, name, chars):
        """Add a string literal to the ASM code."""
        self.string_literals.append(f"{name}")
        data = ",".join(str(char) for char in chars)
        self.string_literals.append(f"\t.byte {data}")


class MASMCode(ASMCode):
    def full_code(self):
        """Produce the full assembly code.
            return (str) - The assembly code, ready for saving to disk and assembling.
        """

        names = []
        names_len = len(DIRECT_VAL) / 2
        if self.string_exist:
            for name in DIRECT_VAL[-int(names_len):]:
                self.add_res(name)
                names.append(str(name))

        header = [".386",
                  ".model flat, stdcall",
                  "option casemap:none\n",
                  "include \\masm32\\include\\windows.inc",
                  "include \\masm32\\include\\masm32.inc",
                  "include \\masm32\\include\\kernel32.inc",
                  "include \\masm32\\include\\user32.inc",
                  "includelib \\masm32\\lib\\masm32.lib",
                  "includelib \\masm32\\lib\\kernel32.lib",
                  "includelib \\masm32\\lib\\user32.lib\n",
                  ".data"] + self.data + ["Caption db \"Test Program\", 0", "Output db   \"" + "—" * 18 +
                                          "\", 0ah,\n\t\t\t\"|" + " " * 25 + " RESULT " + " " * 25 +
                                          "|\", 0ah,\n\t\t\t\"" + "—" * 18 + "\", 0ah, 0ah,"] + sorted(self.output) + \
                 ["\t\t\t\"Author: Shendrikov Yevhenii\", 0", "StrBuf dw ?, 0"]

        if self.string_literals:
            header += self.string_literals + [""]

        header += [''] + self.globals
        header += ['\n.code'] + [str(line) for line in self.lines]

        footer = ["start:", "\tinvoke main"]

        if names_len > 0 and self.string_exist: footer += ["\tinvoke wsprintf, ADDR StrBuf, ADDR Output, " + ', '.join(names)]
        else: footer += ["\tinvoke wsprintf, ADDR StrBuf, ADDR Output, eax"]

        footer += ["\tinvoke MessageBox, 0, ADDR StrBuf, ADDR Caption, MB_ICONINFORMATION",
                   "\tinvoke ExitProcess, 0",
                   "end start"]

        return "\n".join(header + footer)


class NodeGraph:
    """Graph storing conflict and preference information.
        self.real_nodes - list of all real nodes in this graph.
        self.all_nodes - list of all nodes in this graph, including precolored.
        self.conf - dictionary mapping each node to nodes with which it has a conflict edge.
        self.pref - dictionary mapping each node to nodes with which it has a preference edge.
    The conflict and preference relations are symmetric.
    """

    def __init__(self, nodes=None):
        """ Initialize NodeGraph """
        self._real_nodes = nodes if nodes else []
        self._all_nodes = self._real_nodes[:]
        self._conf = {n: [] for n in self._all_nodes}
        self._pref = {n: [] for n in self._all_nodes}

    def is_node(self, n):
        """ Check whether given node is in the graph """
        return n in self._conf and n in self._pref

    def add_imitation_node(self, v):
        """ Add a imitation node to graph """
        self._all_nodes.append(v)
        self._conf[v] = []
        self._pref[v] = []

        # Imitation nodes must mutually conflict
        for n in self._all_nodes:
            if n not in self._real_nodes and n != v: self.add_conflict(n, v)

    def add_conflict(self, n1, n2):
        """ Add a conflict edge between n1 and n2 """
        if n2 not in self._conf[n1]: self._conf[n1].append(n2)
        if n1 not in self._conf[n2]: self._conf[n2].append(n1)

    def add_pref(self, n1, n2):
        """ Add a preference edge between n1 and n2 """
        if n2 not in self._pref[n1]: self._pref[n1].append(n2)
        if n1 not in self._pref[n2]: self._pref[n2].append(n1)

    def pop(self, n):
        """ Remove and return node n from this graph """
        del self._conf[n]
        del self._pref[n]

        if n in self._real_nodes: self._real_nodes.remove(n)
        self._all_nodes.remove(n)

        for v in self._conf:
            if n in self._conf[v]: self._conf[v].remove(n)
        for v in self._pref:
            if n in self._pref[v]: self._pref[v].remove(n)
        return n

    def merge(self, n1, n2):
        """Merge nodes n1 and n2. This function merges n2 into n1. That is, it removes n2 from the graph and n1 gets
        the preference neighbors and conflict neighbors that n2 previously had.
        """

        # Merge conflict lists
        total_conf = self._conf[n1][:]
        for c in self._conf[n2]:
            if c not in total_conf: total_conf.append(c)

        self._conf[n1] = total_conf

        # Restore symmetric invariant
        for c in self._conf[n1]:
            if n2 in self._conf[c]: self._conf[c].remove(n2)
            if n1 not in self._conf[c]: self._conf[c].append(n1)

        # Merge preference lists
        total_pref = self._pref[n1][:]
        for p in self._pref[n2]:
            if p not in total_pref: total_pref.append(p)

        if n1 in total_pref: total_pref.remove(n1)
        if n2 in total_pref: total_pref.remove(n2)
        self._pref[n1] = total_pref

        # Restore symmetric invariant
        for c in self._pref[n1]:
            if n2 in self._pref[c]: self._pref[c].remove(n2)
            if n1 not in self._pref[c]: self._pref[c].append(n1)

        del self._conf[n2]
        del self._pref[n2]
        self._real_nodes.remove(n2)
        self._all_nodes.remove(n2)

    def remove_pref(self, n1, n2):
        """ Remove the preference edge between n1 and n2 """
        self._pref[n1].remove(n2)
        self._pref[n2].remove(n1)

    def prefs(self, n):
        """ Return the list of nodes to which n has a preference edge """
        return self._pref[n]

    def confs(self, n):
        """ Return the list of nodes with which n has a conflict edge """
        return self._conf[n]

    def nodes(self):
        """ Return the real nodes currently in this graph """
        return self._real_nodes

    def all_nodes(self):
        """ Return all nodes in this graph, including pseudonodes """
        return self._all_nodes

    def copy(self):
        """ Return a deep copy of this graph, but with same ILValue objects """
        g = NodeGraph()

        g._real_nodes = self._real_nodes[:]
        g._all_nodes = self._all_nodes[:]
        for n in self._all_nodes:
            g._conf[n] = self._conf[n][:]
            g._pref[n] = self._pref[n][:]

        return g

    def __str__(self):
        """ Return this graph as a string for debugging purposes """
        return ("Conf\n" + "\n".join(str((v, self._conf[v])) for v in self._all_nodes)
                + "\nPref\n" + "\n".join(str((v, self._pref[v])) for v in self._all_nodes))


class ASMGen:
    """Contains the main logic for generation of the ASM from the IL.
        il_code (ILCode) - IL code to convert to ASM.
        asm_code (ASMCode) - ASMCode object to populate with ASM.
        arguments - Arguments passed via command line.
        offset (int) - Current offset from RBP for allocating on stack.
    """

    # List of registers used for allocation, sorted preferred-first
    alloc_registers = spots.registers

    # List of registers used by the get_reg function.
    all_registers = alloc_registers

    def __init__(self, il_code, symbol_table, asm_code, arguments):
        """ Initialize ASMGen """
        self.il_code = il_code
        self.symbol_table = symbol_table
        self.asm_code = asm_code
        self.arguments = arguments

        self.offset = 0

    def make_asm(self):
        """ Generate ASM code """

        global_spotmap = self.get_global_spotmap()

        for func in self.il_code.commands:
            self.asm_code.add(asm_cmds.LabelFunc(func))
            self._make_asm(self.il_code.commands[func], global_spotmap)
            self.asm_code.add(asm_cmds.LabelEndFunc(func))

        if len(self.il_code.string_literals) == 0:
            self.asm_code.output.append("\t\t\t\"Program Result: %d\", 0ah, 0ah,")
        else: ASMCode.string_exist = True
        # my_len, counter = int(len(DIRECT_VAL) / 2), 1
        # if my_len > 1:
        #     for i in range(my_len):
        #         self.asm_code.output.append(f"\t\t\t\"Result{counter}: %d\", 0ah, 0ah,")
        #         counter += 1
        # else: self.asm_code.output.append("\t\t\t\"Program Result: %d\", 0ah, 0ah,")

    def _make_asm(self, commands, global_spotmap):
        """ Generate ASM code for given command list """

        # Get free values
        free_values = self.get_free_values(commands, global_spotmap)

        # If any variable may have its address referenced, assign it a permanent memory spot if it doesn't yet have one.
        move_to_mem = []
        for command in commands:
            refs = command.references().values()
            for line in refs:
                for v in line:
                    if v not in refs: move_to_mem.append(v)

        for v in move_to_mem:
            if v in free_values:
                self.offset += v.ctype.size
                global_spotmap[v] = MemSpot(spots.EBP, -self.offset)
                free_values.remove(v)

        # In addition, move all IL values of strange size to memory because they won't fit in a register.
        for v in free_values:
            if v.ctype.size not in {1, 2, 4, 8}:
                move_to_mem.append(v)

        for v in move_to_mem:
            if v in free_values:
                self.offset += v.ctype.size
                global_spotmap[v] = MemSpot(spots.EBP, -self.offset)
                free_values.remove(v)

            # Perform liveliness analysis
        live_vars = self.get_live_vars(commands, free_values)

        # Generate conflict and preference graph
        g_bak = self.generate_graph(commands, free_values, live_vars)

        spilled_nodes = []

        while True:
            g = g_bak.copy()

            # Remove all nodes that have been spilled for this iteration
            for n in spilled_nodes:
                g.pop(n)

            removed_nodes = []
            merged_nodes = {}

            # Repeat simplification, coalescing, and freeze until freeze does not work.
            while True:
                # Repeat simplification and coalescing until nothing happens.
                while True:
                    simplified = self.simplify_all(removed_nodes, g)
                    merged = self.coalesce_all(merged_nodes, g)

                    if not simplified and not merged: break

                if not self.freeze(g):
                    break

            # If no nodes remain, we are done
            if not g.nodes():
                break
            # If nodes do remain, spill one of them and retry
            else:
                # Spill node with highest number of conflicts. This node will never be a merged node because we merge
                # nodes conservatively, so any recently merged node can be simplified immediately.
                n = max(g.nodes(), key=lambda n: len(g.confs(n)))
                spilled_nodes.append(n)

        # Move any remaining nodes from graph into removed_nodes. This accounts for pseudonodes which cannot be removed
        # in the simplify phase.
        while g.all_nodes():
            removed_nodes.append(g.pop(g.all_nodes()[0]))

        # Pop values off the stack to generate spot assignments.
        spotmap = self.generate_spotmap(removed_nodes, merged_nodes, g_bak)

        # Assign stack values to the spilled nodes
        for v in spilled_nodes:
            self.offset += v.ctype.size
            spotmap[v] = MemSpot(spots.EBP, -self.offset)

        # Merge global spotmap into this spotmap
        for v in global_spotmap:
            spotmap[v] = global_spotmap[v]

        if self.arguments.show_reg_alloc_perf:  # pragma: no cover
            total_prefs = 0
            matched_prefs = 0

            for n1, n2 in itertools.combinations(g_bak.all_nodes(), 2):
                if n2 in g_bak.prefs(n1):
                    total_prefs += 1
                    if spotmap[n1] == spotmap[n2]:
                        matched_prefs += 1

            print("total prefs", total_prefs)
            print("matched prefs", matched_prefs)
            print("total ILValues", len(g_bak.nodes()))
            print("register ILValues", len(g_bak.nodes()) - len(spilled_nodes))

        # Generate assembly code
        self.generate_asm(commands, live_vars, spotmap)

    def get_global_spotmap(self):
        """Generate global spotmap and add global values to ASM. This function generates a spotmap for variables which
        are not specific to a single function. This includes literals and variables with static storage duration.
        """
        global_spotmap = {}

        EXTERNAL = self.symbol_table.EXTERNAL
        DEFINED = self.symbol_table.DEFINED

        num = 0

        for value in (set(self.il_code.literals.keys()) | set(self.il_code.string_literals.keys()) |
                      set(self.symbol_table.storage.keys())):
            num += 1
            spot = self.get_nondynamic_spot(value, num)
            if spot: global_spotmap[value] = spot

        externs = self.symbol_table.linkages[EXTERNAL].values()
        for v in externs:
            if self.symbol_table.def_state.get(v) == DEFINED:
                self.asm_code.add_global(self.symbol_table.names[v])

        return global_spotmap

    def get_nondynamic_spot(self, v, num):
        """Get a spot for non-dynamic values. In particular, assigns a spot to all literals, string literals,
        variables with no storage, and variables with static storage.
            v - value to get a spot for, or None if the value goes in a dynamic spot like a register.
            num - positive integer guaranteed never to be the same for two distinct calls to this function.
        """
        EXTERNAL = self.symbol_table.EXTERNAL
        INTERNAL = self.symbol_table.INTERNAL
        TENTATIVE = self.symbol_table.TENTATIVE

        if v in self.il_code.literals:
            return LiteralSpot(self.il_code.literals[v])

        elif v in self.il_code.string_literals:
            self.asm_code.add_output(bytes(self.il_code.string_literals[v][:-1]).decode())

        # Values with no storage can be referenced directly by name
        elif not self.symbol_table.storage.get(v, True):
            return MemSpot(self.symbol_table.names[v])

        elif self.symbol_table.storage.get(v) == self.symbol_table.STATIC:
            name = self.symbol_table.names[v]
            if self.symbol_table.linkage_type.get(v) != EXTERNAL:
                name = f"{name}.{num}"

            if self.symbol_table.def_state.get(v) == TENTATIVE:
                local = (self.symbol_table.linkage_type[v] == INTERNAL)
                self.asm_code.add_comm(name, v.ctype.size, local)
            else:
                init_val = self.il_code.static_inits.get(v, 0)
                self.asm_code.add_data(name, v.ctype.size, init_val)

            return MemSpot(name)

    @staticmethod
    def get_free_values(commands, global_spotmap):
        """Generate list of free values. Returns a list of the free values, variables which need allocation on the stack
        """
        free_values = []
        for command in commands:
            for value in command.inputs() + command.outputs():
                if value and value not in free_values and value not in global_spotmap:
                    free_values.append(value)

        return free_values

    @staticmethod
    def get_live_vars(commands, free_values):
        """Given a set of free ILValues, find when those ILValues are live.
            free_values - list of ILValues for which to perform liveliness analysis.
            returns - array mapping command indices to a tuple where first element is a list of variables live coming
            into the command and the second is a list of the variables live exiting the command.
        """
        # Preprocess all commands to get a mapping from labels to command number.
        labels = {c.label_name(): i for i, c in enumerate(commands) if c.label_name()}

        # Last iteration of live variables
        prev_live_vars = None

        # This iteration of live variables
        live_vars = [([], []) for i in range(len(commands))]

        while live_vars != prev_live_vars:
            prev_live_vars = live_vars[:]

            # List of currently live variables
            cur_live = []

            # Iterate through commands in backwards order
            for i, command in list(enumerate(commands))[::-1]:
                # If current command is a jump, add the live inputs of all possible targets to the current live list.
                for label in command.targets():
                    i2 = labels[label]
                    for v in prev_live_vars[i2][0]:
                        if v not in cur_live: cur_live.append(v)

                # Variables live on output from this command
                out_live = cur_live[:]

                # Add variables used in this command to current live variables
                for v in command.inputs():
                    if v in free_values and v not in cur_live: cur_live.append(v)

                # Remove variables defined in this command to live variables
                for v in command.outputs():
                    if v in free_values:
                        if v in cur_live: cur_live.remove(v)
                        else:
                            # If variable is defined in command but not live, make it live on output from this command.
                            out_live.append(v)

                # Variables live on input from this command
                in_live = cur_live[:]
                live_vars[i] = (in_live, out_live)

        return live_vars

    @staticmethod
    def generate_graph(commands, free_values, live_vars):
        """Generate the conflict/preference graph.
            free_values - List of ILValues to include in the graph.
            live_vars - Live range information from _get_live_vars.
        """
        g = NodeGraph(free_values)
        for i, command in enumerate(commands):
            # Variables active during input
            for n1, n2 in itertools.combinations(live_vars[i][0], 2): g.add_conflict(n1, n2)

            # Variables active during output
            for n1, n2 in itertools.combinations(live_vars[i][1], 2): g.add_conflict(n1, n2)

            # Relative conflict set of this command
            for n1 in command.rel_spot_conflict():
                for n2 in command.rel_spot_conflict()[n1]:
                    if n1 in free_values and n2 in free_values:
                        g.add_conflict(n1, n2)

            # Absolute conflict set of this command
            for n in command.abs_spot_conflict():
                for s in command.abs_spot_conflict()[n]:
                    if n in free_values:
                        if s not in g.all_nodes():
                            g.add_imitation_node(s)
                        g.add_conflict(n, s)

            # Clobber set of this command
            for s in command.clobber():
                if s not in g.all_nodes(): g.add_imitation_node(s)

                # Add a conflict with dummy node for every variable live during both entry and exit from this command.
                for n in live_vars[i][0]:
                    if n in live_vars[i][1]: g.add_conflict(n, s)

            # Form preferences based on rel_spot_pref
            for v1 in command.rel_spot_preference():
                for v2 in command.rel_spot_preference()[v1]:
                    if g.is_node(v1) and g.is_node(v2): g.add_pref(v1, v2)

            # Form preferences based on abs_spot_pref
            for v in command.abs_spot_preference():
                for s in command.abs_spot_preference()[v]:
                    if v in free_values:
                        if s not in g.all_nodes(): g.add_imitation_node(s)
                        g.add_pref(v, s)
        return g

    def simplify_all(self, removed_nodes, g):
        """Repeat the Simplify step until no more can be done. Returns False if no simplification is done.
            removed_nodes - stack of removed nodes to which this function adds the nodes it removes.
        """

        # Get nodes without preference edges
        no_pref = [v for v in g.nodes() if not g.prefs(v)]

        # Repeat simplification until no more nodes can be removed
        did_something = False
        while True:
            rem = self.simplify_once(no_pref, g)
            if rem:
                removed_nodes.append(rem)
                no_pref.remove(rem)
                did_something = True
            else:
                break

        return did_something

    def simplify_once(self, nodes, g):
        """ Remove and return a node in nodes if it has low conflict degree """
        for v in nodes:
            # If the node has low conflict degree remove it from the graph
            if len(g.confs(v)) < len(self.alloc_registers):
                return g.pop(v)

    def coalesce_all(self, merged_nodes, g):
        """Repeat the coalesce step until no more can be done. Returns False if no simplification is done.
            merged_nodes - Mapping from node to list of nodes. Every node in the list of nodes has been merged into the
            key node.
        """
        did_something = False
        while True:
            merge = self.coalesce_once(g)
            if merge:
                if merge[0] not in merged_nodes: merged_nodes[merge[0]] = []

                merged_nodes[merge[0]].append(merge[1])
                did_something = True
            else:
                break

        return did_something

    def coalesce_once(self, g):
        """Perform one iteration of the coalesce step. Returns the merged pair if a merge was successfully completed.
        The first element is the preserved node, and the second element is the removed node.
        """
        for v1 in g.nodes():
            for v2 in g.prefs(v1):
                # If the two nodes conflict, automatically continue.
                if v1 in g.confs(v2): continue

                total_confs = len(set(g.confs(v1)) | set(g.confs(v2)))

                # If one is a spot, use a special heuristic.
                if isinstance(v1, Spot):
                    v1, v2 = v2, v1
                if isinstance(v2, Spot):
                    for T in g.confs(v1):
                        if v2 in g.confs(T): continue
                        if len(g.confs(T)) < len(self.alloc_registers): continue
                        break
                    else:
                        # We can merge v1 into v2.
                        g.merge(v2, v1)
                        return v2, v1

                # Otherwise, apply regular merging rules.
                elif total_confs < len(self.alloc_registers):
                    g.merge(v1, v2)
                    return v1, v2

    @staticmethod
    def freeze(g):
        """Remove one preference edge. This function finds two nodes, preferably of low conflict degree,
        that are connected by a preference edge. Then, this preference edge is removed from the graph. Returns false if
        nothing is done.
        """

        # Sort a list of nodes by conflict degree
        nodes = sorted(g.all_nodes(), key=lambda n: len(g.confs(n)))
        index_pairs = list(itertools.combinations(list(enumerate(nodes)), 2))

        # Sort pairs to prioritize nodes which appear earlier in `nodes`
        index_pairs.sort(key=lambda p: p[0][0] + p[1][0])

        # Extract just the node pairs
        pairs = [(p[0][1], p[1][1]) for p in index_pairs]

        # Now, the earlier pairs in `pairs` have lower conflict degree and are thus superior candidates for freezing.
        for n1, n2 in pairs:
            if n1 in g.prefs(n2):
                g.remove_pref(n1, n2)
                return True

        return False

    def generate_spotmap(self, removed_nodes, merged_nodes, g):
        """ Pop values off stack to generate spot assignments """

        # Get a set of nodes which interfere with n or anything merged into it
        def get_conflicts(n):
            conflicts = set(g.confs(n))
            for n1 in merged_nodes.get(n, []):
                conflicts |= get_conflicts(n1)
            return conflicts

        # Get a set of nodes which are merged into `n`
        def get_merged(n):
            merged = {n}
            for n1 in merged_nodes.get(n, []):
                merged |= get_merged(n1)
            return merged

        # Build up spotmap
        spotmap = {}
        i = 0
        while removed_nodes:
            i += 1

            # Allocate register to node `n`
            n1 = removed_nodes.pop()
            regs = self.alloc_registers[::-1]

            # If n1 is a Spot (i.e. dummy node), immediately assign it a register.
            if n1 in regs: reg = n1
            else:
                # Don't chose any conflicting spots
                for n2 in get_conflicts(n1):
                    # If n2 is a physical spot
                    if n2 in regs: regs.remove(n2)
                    if n2 in spotmap and spotmap[n2] in regs: regs.remove(spotmap[n2])

                # Based on algorithm, there should always be register remaining
                reg = regs.pop()

            # Assign this register to every node merged into n1
            for n2 in get_merged(n1): spotmap[n2] = reg

        return spotmap

    def generate_asm(self, commands, live_vars, spotmap):
        """ Generate assembly code """

        max_offset = max(spot.rbp_offset() for spot in spotmap.values())
        if max_offset % 16 != 0: max_offset += 16 - max_offset % 16

        # Back up ebp and move esp
        self.asm_code.add(asm_cmds.Push(spots.EBP, None, 8))
        self.asm_code.add(asm_cmds.Mov(spots.EBP, spots.ESP, 8))

        offset_spot = LiteralSpot(str(max_offset))
        self.asm_code.add(asm_cmds.Sub(spots.ESP, offset_spot, 8))

        # Generate code for each command
        for i, command in enumerate(commands):
            self.asm_code.add(asm_cmds.Comment(type(command).__name__.upper()))

            def get_reg(pref=None, conf=None):
                if not pref: pref = []
                if not conf: conf = []

                # Spot is bad if it is containing a variable that is live both entering and exiting this command.
                bad_vars = set(live_vars[i][0]) & set(live_vars[i][1])
                bad_spots = set(spotmap[var] for var in bad_vars)

                # Spot is free if it is where an output is stored.
                for v in command.outputs():
                    bad_spots.discard(spotmap[v])

                # Spot is bad if it is listed as a conflicting spot.
                bad_spots |= set(conf)

                for s in (pref + self.all_registers):
                    if isinstance(s, RegSpot) and s not in bad_spots:
                        return s

                raise NotImplementedError("spill required for get_reg")

            command.make_asm(spotmap, spotmap, get_reg, self.asm_code)
