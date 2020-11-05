"""Parser logic that parses statement nodes."""

from myparser.utils import (add_range, log_error, match_token, token_is, ParserError)
from myparser.declaration import parse_declaration
from myparser.expression import parse_expression
import tree.tree as nodes
import token_kinds



@add_range
def parse_statement(index):
    """Parse a statement. Try each possible type of statement, catching/logging exceptions upon parse failures. On the
    last try, raise the exception on to the caller.
    """
    for func in (parse_compound_statement, parse_return, parse_if_statement):
        try:
            return func(index)
        except ParserError as e:
            log_error(e)

    return parse_expr_statement(index)


@add_range
def parse_compound_statement(index):
    """Parse a compound statement. A compound statement is a collection of several statements/declarations, enclosed in
    braces.
    """
    index = match_token(index, token_kinds.open_brack, ParserError.GOT)

    # Read block items (statements/declarations) until there are no more.
    items = []
    while True:
        try:
            item, index = parse_statement(index)
            items.append(item)
            continue
        except ParserError as e:
            log_error(e)

        try:
            item, index = parse_declaration(index)
            items.append(item)
            continue
        except ParserError as e:
            log_error(e)
            # When both of our parsing attempts fail, break out of the loop
            break

    index = match_token(index, token_kinds.close_brack, ParserError.GOT)

    return nodes.Compound(items), index


@add_range
def parse_return(index):
    """Parse a return statement.
        Ex: return 5;
    """
    index = match_token(index, token_kinds.return_kw, ParserError.GOT)
    if token_is(index, token_kinds.semicolon):
        return nodes.Return(None), index

    node, index = parse_expression(index)

    index = match_token(index, token_kinds.semicolon, ParserError.AFTER)
    return nodes.Return(node), index


@add_range
def parse_if_statement(index):
    """Parse an if statement."""

    index = match_token(index, token_kinds.if_kw, ParserError.GOT)
    index = match_token(index, token_kinds.open_paren, ParserError.AFTER)
    conditional, index = parse_expression(index)
    index = match_token(index, token_kinds.close_paren, ParserError.AFTER)
    statement, index = parse_statement(index)

    # If there is an else that follows, parse that too.
    is_else = token_is(index, token_kinds.else_kw)
    if not is_else:
        else_statement = None
    else:
        index = match_token(index, token_kinds.else_kw, ParserError.GOT)
        else_statement, index = parse_statement(index)

    return nodes.IfStatement(conditional, statement, else_statement), index


@add_range
def parse_expr_statement(index):
    """Parse a statement that is an expression.
        Ex: a = 3 + 4
    """
    if token_is(index, token_kinds.semicolon):
        return nodes.EmptyStatement(), index + 1

    node, index = parse_expression(index)
    index = match_token(index, token_kinds.semicolon, ParserError.AFTER)
    return nodes.ExprStatement(node), index
