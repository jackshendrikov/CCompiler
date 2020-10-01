"""Classes for the nodes that form our abstract syntax tree (AST). Each node corresponds to a rule in the C grammar."""

import token_kinds


def assert_symbol(node, symbol_name):
    """Useful for enforcing tree structure. Raises an exception if the node represents a rule that does not
    produce the expected symbol.
    """
    if node.symbol != symbol_name:
        raise ValueError("Malformed tree: expected symbol ", symbol_name, ", got ", node.symbol)


def assert_kind(token, kind):
    if token.kind != kind:
        raise ValueError("Malformed tree: expected token kind ", kind, ", got ", token.kind)


class Node:
    """A general class for representing a single node in the AST. Inherit all AST nodes from this class.

    symbol (str) - each node must set the value of this class attribute to the non-terminal symbol the
    corresponding rule produces. This helps enforce tree structure so bugs in the parser do not accidentally
    slip into output code.
    """
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class MainNode(Node):
    """General rule for the main function. Ex: int main() { return `return_value`; }

    statements (List[statement]) - a list of the statement in main function
    """
    symbol = "main_function"

    def __init__(self, statements):
        super().__init__()

        for statement in statements: assert_symbol(statement, "statement")
        self.statements = statements

    def make_masm(self, masm_store):
        masm_store.add_label("main PROC")
        for statement in self.statements: statement.make_masm(masm_store)
        masm_store.add_label("main ENDP")

    def make_code(self, code_store):
        code_store.add_label("main")
        code_store.add_command(("push", "rbp"))
        code_store.add_command(("mov", "rbp", "rsp"))
        for statement in self.statements: statement.make_code(code_store)

        # Return 0 at the end, in case the code did not return
        code_store.add_command(("mov", "rax", "0"))
        code_store.add_command(("pop", "rbp"))
        code_store.add_command(("ret",))


class ReturnNode(Node):
    """ Return statement

    return_value (expression) - value to return
    """
    symbol = "statement"

    def __init__(self, return_value):
        super().__init__()

        assert_symbol(return_value, "expression")
        self.return_value = return_value

    def make_masm(self, masm_store):
        # For now, the expression always returns its value in the eax register.
        self.return_value.make_masm(masm_store)
        masm_store.add_command(("ret",))

    def make_code(self, code_store):
        # For now, the expression always returns its value in the rax register.
        # This will be changed shortly, so the "mov rax rax" command will be made more useful.
        self.return_value.make_code(code_store)
        code_store.add_command(("mov", "rax", "rax"))
        code_store.add_command(("pop", "rbp"))
        code_store.add_command(("ret",))


class NumberNode(Node):
    """ Expression that is just a single number.

    number (Token(Number)) - number this expression represents
    """
    symbol = "expression"

    def __init__(self, number):
        super().__init__()

        assert number.kind == token_kinds.number
        self.number = number

    def make_masm(self, masm_store):
        masm_store.add_command(("mov", "eax", self.number.content))

    def make_code(self, code_store):
        code_store.add_command(("mov", "rax", self.number.content))
