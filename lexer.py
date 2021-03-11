"""Objects for the lexing phase of the compiler. The lexing phase takes the entire contents of a raw input file and
generates a flat list of tokens present in that input file.
"""

from errors import CompilerError, Position, Range, error_collector
from token_kinds import symbol_kinds, keyword_kinds
from tokens import Token
from re import match
import token_kinds

STR_EX = []


class Tagged:
    """Class representing tagged characters.
        c (char) - the character that is tagged.
        p (Position) - position of the tagged character.
        r (Range) - a length-one range for the character.
    """

    def __init__(self, c, p):
        """ Initialize object """
        self.c = c
        self.p = p
        self.r = Range(p, p)


def tokenize(code, filename):
    """Convert given code into a flat list of Tokens.
        lines - List of list of Tagged objects, where each embedded list is a separate line in the input program.
        return - List of Token objects.
    """
    # Store tokens as they are generated
    tokens = []

    lines = split_to_tagged_lines(code, filename)
    join_extended_lines(lines)

    in_comment = False
    for line in lines:
        try:
            line_tokens, in_comment = tokenize_line(line, in_comment)
            tokens += line_tokens
        except CompilerError as e:
            error_collector.add(e)

    return tokens


def split_to_tagged_lines(text, filename):
    """Split the input text into tagged lines. No newline escaping or other preprocessing is done by this function.
        text (str) - Input file contents as a string.
        filename (str) - Input file name.
        return - Tagged lines. List of list of Tagged objects, where each second order list is a separate line in the
        input program. No newline characters.
    """
    lines = text.splitlines()
    tagged_lines = []
    for line_num, line in enumerate(lines):
        tagged_line = []
        for col, char in enumerate(line):
            p = Position(filename, line_num + 1, col + 1, line)
            tagged_line.append(Tagged(char, p))
        tagged_lines.append(tagged_line)

        line_num += 1

    return tagged_lines


def join_extended_lines(lines):
    """Join together any lines which end in an escaped newline. This function modifies the given lines object in place.
        lines - List of list of Tagged objects, where each embedded list is a separate line in the input program.
    """

    i = 0
    while i < len(lines):
        if lines[i] and lines[i][-1].c == "\\":
            # There is a next line to collapse into this one
            if i + 1 < len(lines):
                del lines[i][-1]  # remove trailing backslash
                lines[i] += lines[i + 1]  # concatenate with next line
                del lines[i + 1]  # remove next line

                # Decrement i, so this line is checked for a new trailing backslash.
                i -= 1

            # There is no next line to collapse into this one
            else:
                del lines[i][-1]  # remove trailing backslash

        i += 1


def tokenize_line(line, in_comment):
    """Tokenize the given single line.
        line - List of Tagged objects.
        in_comment - Whether the first character in this line is part of a C-style comment body.
        return - List of Token objects, and boolean indicating whether the next character is part of a comment body.
    """
    tokens = []

    # line[block_start:block_end] is the section of the line currently being considered for conversion into a token;
    # this string will be called the 'block'. Everything before the block has already been tokenized, and everything
    # after has not yet been examined
    block_start = 0
    block_end = 0

    while block_end < len(line):
        symbol_kind = match_symbol_kind_at(line, block_end)
        next_ = match_symbol_kind_at(line, block_end + 1)

        if in_comment:
            # If next characters end the comment...
            if symbol_kind == token_kinds.star and next_ == token_kinds.slash:
                in_comment = False
                block_start = block_end + 2
                block_end = block_start
            # Otherwise, just skip one character.
            else:
                block_start = block_end + 1
                block_end = block_start

        # If next characters start a comment, process previous block and set in_comment to true.
        elif symbol_kind == token_kinds.slash and next_ == token_kinds.star:
            add_block(line[block_start:block_end], tokens)
            in_comment = True

        # If next two characters are //, we skip the rest of this line.
        elif symbol_kind == token_kinds.slash and next_ == token_kinds.slash:
            break

        # Skip spaces and process previous block.
        elif line[block_end].c.isspace():
            add_block(line[block_start:block_end], tokens)
            block_start = block_end + 1
            block_end = block_start

        # If next character is a quote, we read the whole string as a token.
        elif symbol_kind in {token_kinds.dquote, token_kinds.squote}:
            if symbol_kind == token_kinds.dquote:
                global STR_EX
                STR_EX.append(1)
                quote_str = '"'
                kind = token_kinds.string
                add_null = True
            else:
                quote_str = "'"
                kind = token_kinds.char_string
                add_null = False

            chars, end = read_string(line, block_end + 1, quote_str, add_null)
            rep = block_to_str(line[block_end:end + 1])
            r = Range(line[block_end].p, line[end].p)

            if kind == token_kinds.char_string and len(chars) == 0:
                err = "empty character constant"
                error_collector.add(CompilerError(err, r))
            elif kind == token_kinds.char_string and len(chars) > 1:
                err = "multiple characters in character constant"
                error_collector.add(CompilerError(err, r))

            tokens.append(Token(kind, chars, rep, r=r))
            block_start = end + 1
            block_end = block_start

        # If next character is another symbol, add previous block and then add the symbol.
        elif symbol_kind:
            symbol_start_index = block_end
            symbol_end_index = block_end + len(symbol_kind.text_repr) - 1

            r = Range(line[symbol_start_index].p, line[symbol_end_index].p)
            symbol_token = Token(symbol_kind, r=r)

            add_block(line[block_start:block_end], tokens)
            tokens.append(symbol_token)

            block_start = block_end + len(symbol_kind.text_repr)
            block_end = block_start

        # Include another character in the block.
        else:
            block_end += 1

    # Flush out anything that is left in the block to the output
    add_block(line[block_start:block_end], tokens)

    return tokens, in_comment


def block_to_str(block):
    """Convert the given block to a string.
        block - list of Tagged characters.
        return - string representation of the list of Tagged characters.
    """
    return "".join(c.c for c in block)


def match_symbol_kind_at(content, start):
    """Return the longest matching symbol token kind.
        content - List of Tagged objects in which to search for match.
        start (int) - Index, inclusive, at which to start searching for a match.
        returns (TokenType or None) - Symbol token found, or None if no token is found.
    """
    for symbol_kind in symbol_kinds:
        try:
            for i, c in enumerate(symbol_kind.text_repr):
                if content[start + i].c != c:
                    break
            else:
                return symbol_kind
        except IndexError:
            pass

    return None


def read_string(line, start, delim, null):
    """Return a lexed string list in input characters. Also returns the index of the string end quote.
    line[start] should be the first character after the opening quote of the string to be lexed. This function continues
    reading characters until an unescaped closing quote is reached. The length returned is the number of input character
    that were read, not the length of the string. The latter is the length of the lexed string list. The lexed string is
    a list of integers, where each integer is the ASCII value (between 0 and 128) of the corresponding character in the
    string. The returned lexed string includes a null-terminator.
        line - List of Tagged objects for each character in the line.
        start - Index at which to start reading the string.
        delim - Delimiter with which the string ends, like `"` or `'`
        null - Whether to add a null-terminator to the returned character list
    """
    i = start
    chars = []

    escapes = {"'": 39,
               '"': 34,
               "?": 63,
               "\\": 92,
               "a": 7,
               "b": 8,
               "f": 12,
               "n": 10,
               "r": 13,
               "t": 9,
               "v": 11}

    octdigits = "01234567"
    hexdigits = "0123456789abcdefABCDEF"

    while True:
        if i >= len(line):
            descr = "missing terminating quote"
            raise CompilerError(descr, line[start - 1].r)
        elif line[i].c == delim:
            if null: chars.append(0)
            return chars, i
        elif i + 1 < len(line) and line[i].c == "\\" and line[i + 1].c in escapes:
            chars.append(escapes[line[i + 1].c])
            i += 2
        elif i + 1 < len(line) and line[i].c == "\\" and line[i + 1].c in octdigits:
            octal = line[i + 1].c
            i += 2
            while i < len(line) and len(octal) < 3 and line[i].c in octdigits:
                octal += line[i].c
                i += 1
            chars.append(int(octal, 8))
        elif i + 2 < len(line) and line[i].c == "\\" and line[i + 1].c == "x" and line[i + 2].c in hexdigits:
            hexa = line[i + 2].c
            i += 3
            while i < len(line) and line[i].c in hexdigits:
                hexa += line[i].c
                i += 1
            chars.append(int(hexa, 16))
        else:
            chars.append(ord(line[i].c))
            i += 1


def add_block(block, tokens):
    """Convert block into a token if possible and add to tokens. If block is non-empty but cannot be made into a token,
    this function records a compiler error. We don't need to check for symbol kind tokens here because they are
    converted before they are shifted into the block.
        block - block to convert into a token, as list of Tagged characters.
        tokens (List[Token]) - List of the tokens so fat parsed.
    """
    if block:
        range_ = Range(block[0].p, block[-1].p)

        keyword_kind = match_keyword_kind(block)
        if keyword_kind:
            tokens.append(Token(keyword_kind, r=range_))
            return

        number_string = match_number_string(block)
        if number_string:
            tokens.append(Token(token_kinds.number, number_string, r=range_))
            return

        identifier_name = match_identifier_name(block)
        if identifier_name:
            tokens.append(Token(
                token_kinds.identifier, identifier_name, r=range_))
            return

        descr = f"unrecognized token at '{block_to_str(block)}'"
        raise CompilerError(descr, range_)


def isbinary(token):
    """Check whether the submitted token is a binary number
        token (int) - the int to check if it binary or not.
    returns (boolean) - True (1) if given int is in binary representation, False (0) if not.
    """
    return 1 if match(r'^0[bB][01]+$', token) else 0


def match_keyword_kind(token_repr):
    """Find the longest keyword token kind with representation token_repr.
        token_repr - Token representation to match exactly, as list of Tagged characters.
        returns (TokenKind, or None) - Keyword token kind that matched.
    """
    token_str = block_to_str(token_repr)
    for keyword_kind in keyword_kinds:
        if keyword_kind.text_repr == token_str:
            return keyword_kind
    return None


def match_number_string(token_repr):
    """Return a string that represents the given constant number.
        token_repr - List of Tagged characters.
        returns (str, or None) - String representation of the number.
    """
    token_str = block_to_str(token_repr)
    if token_str.isdigit():
        return token_str
    elif isbinary(token_str):
        return str(int(token_str, 2))


def match_identifier_name(token_repr):
    """Return a string that represents the name of an identifier.
        token_repr - List of Tagged characters.
        returns (str, or None) - String name of the identifier.
    """
    token_str = block_to_str(token_repr)
    if match(r"[_a-zA-Z][_a-zA-Z0-9]*$", token_str):
        return token_str
    else:
        return None
