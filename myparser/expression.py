""" Parser logic that parses expression nodes """

from myparser.utils import (add_range, match_token, token_is, ParserError, raise_error, log_error, token_in)
import tree.expr_tree as expr_nodes
import tree.decl_tree as decl_nodes
import myparser.utils as utils
import token_kinds


@add_range
def parse_expression(index):
    """ Parse expression """
    return parse_series(index, parse_assignment, {token_kinds.comma: expr_nodes.MultiExpr})


@add_range
def parse_assignment(index):
    """ Parse an assignment expression """

    left, index = parse_conditional(index)

    if index < len(utils.tokens):
        op = utils.tokens[index]
        kind = op.kind
    else:
        op = None
        kind = None

    node_types = {token_kinds.equals: expr_nodes.Equals,
                  token_kinds.plusequals: expr_nodes.PlusEquals,
                  token_kinds.minusequals: expr_nodes.MinusEquals,
                  token_kinds.starequals: expr_nodes.StarEquals,
                  token_kinds.divequals: expr_nodes.DivEquals,
                  token_kinds.modequals: expr_nodes.ModEquals,
                  token_kinds.bitwise_and_equals: expr_nodes.BitwiseAndEquals}

    if kind in node_types:
        right, index = parse_assignment(index + 1)
        return node_types[kind](left, right, op), index
    else:
        return left, index


@add_range
def parse_conditional(index):
    """ Parse a conditional expression """
    return parse_logical_or(index)


@add_range
def parse_logical_or(index):
    """ Parse logical or expression """
    return parse_series(index, parse_logical_and, {token_kinds.bool_or: expr_nodes.BoolOr})


@add_range
def parse_logical_and(index):
    """ Parse logical and expression """
    return parse_series(index, parse_equality, {token_kinds.bool_and: expr_nodes.BoolAnd})


@add_range
def parse_equality(index):
    """ Parse equality expression """
    return parse_series(index, parse_relational, {token_kinds.twoequals: expr_nodes.Equality,
                                                  token_kinds.notequal: expr_nodes.Inequality})


@add_range
def parse_relational(index):
    """ Parse relational expression """
    return parse_series(index, parse_bitwise_and, {token_kinds.lt: expr_nodes.LessThan,
                                                    token_kinds.gt: expr_nodes.GreaterThan,
                                                    token_kinds.ltoe: expr_nodes.LessThanOrEq,
                                                    token_kinds.gtoe: expr_nodes.GreaterThanOrEq})


@add_range
def parse_bitwise_and(index):
    """ Parse additive expression """
    return parse_series(index, parse_additive, {token_kinds.amp: expr_nodes.BitwiseAnd})


@add_range
def parse_bitwise(index):
    return parse_series(index, parse_additive, {token_kinds.lbitshift: expr_nodes.LBitShift,
                                                token_kinds.rbitshift: expr_nodes.RBitShift})


@add_range
def parse_additive(index):
    """ Parse additive expression """
    return parse_series(index, parse_multiplicative, {token_kinds.plus: expr_nodes.Plus,
                                                      token_kinds.minus: expr_nodes.Minus})


@add_range
def parse_multiplicative(index):
    """ Parse multiplicative expression """
    return parse_series(index, parse_unary, {token_kinds.star: expr_nodes.Mult, token_kinds.slash: expr_nodes.Div,
                                             token_kinds.mod: expr_nodes.Mod})


@add_range
def parse_cast(index):
    """ Parse cast expression """
    from myparser.declaration import (parse_abstract_declarator, parse_spec_qual_list)

    with log_error():
        match_token(index, token_kinds.open_paren, ParserError.AT)
        specs, index = parse_spec_qual_list(index + 1)
        node, index = parse_abstract_declarator(index)
        match_token(index, token_kinds.close_paren, ParserError.AT)

        decl_node = decl_nodes.Root(specs, [node])
        expr_node, index = parse_cast(index + 1)
        return expr_nodes.Cast(decl_node, expr_node), index

    return parse_unary(index)


@add_range
def parse_unary(index):
    """ Parse unary expression """

    unary_args = {token_kinds.incr: (parse_unary, expr_nodes.PreIncr),
                  token_kinds.decr: (parse_unary, expr_nodes.PreDecr),
                  token_kinds.amp: (parse_cast, expr_nodes.AddrOf),
                  token_kinds.star: (parse_cast, expr_nodes.Deref),
                  token_kinds.bool_not: (parse_cast, expr_nodes.BoolNot),
                  token_kinds.plus: (parse_cast, expr_nodes.UnaryPlus),
                  token_kinds.minus: (parse_cast, expr_nodes.UnaryMinus),
                  token_kinds.compl: (parse_cast, expr_nodes.Compl)}

    if token_in(index, unary_args):
        parse_func, NodeClass = unary_args[utils.tokens[index].kind]
        subnode, index = parse_func(index + 1)
        return NodeClass(subnode), index
    else:
        return parse_postfix(index)


@add_range
def parse_postfix(index):
    """ Parse postfix expression """
    cur, index = parse_primary(index)

    while True:
        old_range = cur.r

        if token_is(index, token_kinds.open_sq_brack):
            index += 1
            arg, index = parse_expression(index)
            cur = expr_nodes.ArraySubsc(cur, arg)
            match_token(index, token_kinds.close_sq_brack, ParserError.GOT)
            index += 1

        elif token_is(index, token_kinds.dot) or token_is(index, token_kinds.arrow):
            index += 1
            match_token(index, token_kinds.identifier, ParserError.AFTER)
            member = utils.tokens[index]

            if token_is(index - 1, token_kinds.dot): cur = expr_nodes.ObjMember(cur, member)
            else: cur = expr_nodes.ObjPtrMember(cur, member)

            index += 1

        elif token_is(index, token_kinds.open_paren):
            args = []
            index += 1

            if token_is(index, token_kinds.close_paren):
                return expr_nodes.FuncCall(cur, args), index + 1

            while True:
                arg, index = parse_assignment(index)
                args.append(arg)

                if token_is(index, token_kinds.comma): index += 1
                else: break

            index = match_token(
                index, token_kinds.close_paren, ParserError.GOT)

            return expr_nodes.FuncCall(cur, args), index

        elif token_is(index, token_kinds.incr):
            index += 1
            cur = expr_nodes.PostIncr(cur)
        elif token_is(index, token_kinds.decr):
            index += 1
            cur = expr_nodes.PostDecr(cur)
        else:
            return cur, index

        cur.r = old_range + utils.tokens[index - 1].r


@add_range
def parse_primary(index):
    """ Parse primary expression """
    if token_is(index, token_kinds.open_paren):
        node, index = parse_expression(index + 1)
        index = match_token(index, token_kinds.close_paren, ParserError.GOT)
        return expr_nodes.ParenExpr(node), index
    elif token_is(index, token_kinds.number):
        return expr_nodes.Number(utils.tokens[index]), index + 1
    elif token_is(index, token_kinds.identifier) and not utils.symbols.is_typedef(utils.tokens[index]):
        return expr_nodes.Identifier(utils.tokens[index]), index + 1
    elif token_is(index, token_kinds.string):
        return expr_nodes.String(utils.tokens[index].content), index + 1
    elif token_is(index, token_kinds.char_string):
        chars = utils.tokens[index].content
        return expr_nodes.Number(chars[0]), index + 1
    else:
        raise_error("expected expression", index, ParserError.GOT)


def parse_series(index, parse_base, separators):
    """ Parse a series of symbols joined together with given separator(s).
        index (int) - Index at which to start searching.

        parse_base (function) - A parse_* function that parses the base symbol.

        separators (Dict(TokenKind -> Node)) - The separators that join instances of the base symbol. Each separator
        corresponds to a Node, which is the Node produced to join two expressions connected with that separator.
    """
    cur, index = parse_base(index)
    while True:
        for s in separators:
            if token_is(index, s):
                break
        else:
            return cur, index

        tok = utils.tokens[index]
        new, index = parse_base(index + 1)
        cur = separators[s](cur, new, tok)
