"""Defines functions for the lexing phase of the compiler

The lexing phase takes a raw text string as input from the preprocessor and generates a flat list of tokens
present in that text string. Because there's currently no preprocessor implemented, the input text string is simply
the file contents.
"""

from errors import CompilerError
from re import match
from tokens import Token
import token_kinds


def match_char_string(token_repr):
    """Return a string that represents the given constant character, or None if not possible

    token_repr (str) - the string to make into a token
    returns (str, or None) - the string representation of the char
    """
    return char2num(token_repr) if ischar(token_repr) else None


def match_number_string(token_repr):
    """Return a string that represents the given constant number, or None if not possible

    token_repr (str) - the string to make into a token
    returns (str, or None) - the string representation of the number
    """
    if token_repr.isdigit(): return token_repr
    elif isbinary(token_repr): return token_repr[2:]+'B'


def ischar(token):
    """Check whether the submitted token is a char

    token - the token to check if it in char representation or not
    returns (boolean) - True (1) if given token is char, False (0) if not
    """
    return 1 if match(r'(\'.\')', token) else 0


def isbinary(token):
    """ Check whether the submitted token is a binary number

    token (int) - the int to check if it binary or not
    returns (boolean) - True (1) if given int is in binary representation, False (0) if not
    """
    return 1 if match(r'^0[bB][01]+$', token) else 0


def char2num(sym):
    """Convert the given char into int number

    sym (char) - the char to make into a number
    returns (int) - the int representation of the  char
    """
    return str(ord(sym[1:-1]))


class Lexer:
    """The environment for running tokenize() and associated functions.
    Effectively, creates a closure for tokenize().

    symbol_kinds (List[TokenKind]) - a list of all the specific token kinds that are not keywords.
    These should split into a new token even when they are not surrounded by whitespace, like the plus in `a+b`.
    Sorted from longest to shortest.

    keyword_kinds (List[TokenKind]) - a list of all the specific tokens that are not splitting.
    These are just the keywords.
    Sorted from longest to shortest.
    """

    def __init__(self, symbol_kinds, keyword_kinds):
        self.symbol_kinds = sorted(symbol_kinds, key=lambda kind: -len(kind.text_repr))
        self.keyword_kinds = sorted(keyword_kinds, key=lambda kind: -len(kind.text_repr))

    def tokenize(self, code_lines):
        """Convert the given lines of code into a list of tokens.

        The tokenizing algorithm proceeds through the content linearly in 1 pass, producing the list of tokens as we go.
        Has direct external reference to token_kinds.number.

        content (List(tuple)) - the lines of code to tokenize, provided in the following form:

           [("int main()", "main.c", 1),
            ("{", "main.c", 2),
            ("return 5;", "main.c", 3),
            ("}", "main.c", 4)]

        Where the 1st element is the contents of the line, the 2nd is the file name, and the 3rd is the line number.

        returns (List[Token]) - a list of the tokens parsed from the input string
        """

        all_tokens = []
        for line_with_info in code_lines:
            # This strange logic allows the tokenize_line function to be ignorant to the file-context of line passed in.
            try:
                tokens = self.tokenize_line(line_with_info[0])
            except CompilerError as e:
                e.file_name = line_with_info[1]
                e.line_num = line_with_info[2]
                raise e

            for token in tokens:
                token.file_name = line_with_info[1]
                token.line_num = line_with_info[2]
                all_tokens.append(token)
        return all_tokens

    def tokenize_line(self, line):
        """Convert the given line of code into a tokens list that have no file-context
        dependent attributes (like line number) set.

        line (str) - a line of code
        returns (Token) - a token without file-context dependent attributes
        """

        # line[block_start:block_end] is the section of the line currently being considered for conversion into a token;
        # this string will be called the 'block'. Everything before the block has already been tokenized, and everything
        # after has not yet been examined
        block_start = 0
        block_end = 0

        # Stores the tokens as they are generated
        tokens = []

        # While we still have characters in the line left to parse
        while block_end < len(line):
            # Checks if line[block_end:] starts with a symbol token kind
            symbol_kind = self.match_symbol_kind_at(line, block_end)
            if symbol_kind:
                symbol_token = Token(symbol_kind)

                self.add_block(line[block_start:block_end], tokens)
                tokens.append(symbol_token)

                block_start = block_end + len(symbol_kind.text_repr)
                block_end = block_start

            elif line[block_end].isspace():
                self.add_block(line[block_start:block_end], tokens)
                block_start = block_end + 1
                block_end = block_start

            else:
                block_end += 1

        # Flush out anything that is left in the block to the output
        self.add_block(line[block_start:block_end], tokens)
        return tokens

    def match_symbol_kind_at(self, content, start):
        """Return the longest symbol token kind that matches the content string starting at the indicated index,
        or None if no symbol token matches.

        content (str) - the input string to tokenize
        start (int) - the index, inclusive, at which to start searching for a token match
        returns (TokenType, None) - the symbol token found, or None if no token is found
        """
        for symbol_kind in self.symbol_kinds:
            if content.startswith(symbol_kind.text_repr, start):
                return symbol_kind
        return None

    def add_block(self, block, tokens):
        """Convert the provided block into a token and add to the provided tokens variable.
        If block is non-empty but cannot be made into a token, raise a compiler error.

        block (str) - the block to convert into a token
        tokens (List[Token]) - a list of the tokens parsed so far
        """
        if block:
            keyword_kind = self.match_keyword_kind(block)
            if keyword_kind:
                tokens.append(Token(keyword_kind))
                return

            number_string = match_number_string(block)
            char_string = match_char_string(block)
            if number_string:
                tokens.append(Token(token_kinds.number, number_string))
                return
            elif char_string:
                tokens.append(Token(token_kinds.number, char_string))
                return

            raise CompilerError("unrecognized token at '{}'".format(block))

    def match_keyword_kind(self, token_repr):
        """Return the longest keyword token kind with representation exactly equal to the given token_repr,
        or None if not found.

        token_repr (str) - the token representation to match
        returns (TokenKind, or None) - the keyword token kind that matched
        """
        for keyword_kind in self.keyword_kinds:
            if keyword_kind.text_repr == token_repr:
                return keyword_kind
        return None
