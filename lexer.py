"""Objects for the lexing phase of the compiler. The lexing phase takes a raw text string as input from the preprocessor
and generates a flat list of tokens present in that text string. Because there's currently no preproccesor implemented,
the input text string is simply the file contents.
"""
import token_kinds
from errors import CompilerError, error_collector
from tokens import Token
from re import match


class Lexer:
    """Environment for running tokenize() and associated functions. Effectively, creates a closure for tokenize().

        symbol_kinds (List[TokenKind]) - A list of all the specific token kinds that are not keywords. These should
        split into a new token even when they are not surrounded by whitespace, like the plus in `a+b`. Stored in the
        object sorted from longest to shortest.

        keyword_kinds (List[TokenKind]) - A list of all the specific tokens that are not splitting. These are just the
        keywords. Stored in the object sorted from longest to shortest.
    """

    def __init__(self):
        """Sort the token kind lists and initialize lexer."""
        self.symbol_kinds = sorted(
            token_kinds.symbol_kinds, key=lambda kind: -len(kind.text_repr))
        self.keyword_kinds = sorted(
            token_kinds.keyword_kinds, key=lambda kind: -len(kind.text_repr))

    def tokenize(self, code_lines):
        """Convert the given lines of code into a list of tokens.
        The tokenizing algorithm proceeds through the content linearly in 1 pass, producing the list of tokens as we go.
            content (List(tuple)) - Lines of code to tokenize, provided in the following form:
               [("int main()", "main.c", 1),
                ("{", "main.c", 2),
                ("return 5;", "main.c", 3),
                ("}", "main.c", 4)]
            where first element is the contents of the line, the second is the file name, and the third is the line num.

            returns (List[Token]) - List of the tokens parsed from the input string.
        """
        all_tokens = []
        for line_with_info in code_lines:
            # This strange logic allows tokenize_line function to be ignorant to the file-context of the line passed in.
            try:
                tokens = self.tokenize_line(line_with_info[0])
            except CompilerError as e:
                e.file_name = line_with_info[1]
                e.line_num = line_with_info[2]
                error_collector.add(e)

            for token in tokens:
                token.file_name = line_with_info[1]
                token.line_num = line_with_info[2]
                all_tokens.append(token)
        return all_tokens

    def tokenize_line(self, line):
        """Convert the given line of code into a list of tokens. The tokens returned have no file-context dependent
        attributes (like line number). These must be set by the caller.
            line (str) - Line of code.
            returns (List(Token)) - List of tokens.
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
        """Return the longest matching symbol token kind.
            content (str) - Input string in which to search for a match.
            start (int) - Index, inclusive, at which to start searching for a match.
            returns (TokenType or None) - Symbol token found, or None if no token is found.
        """
        for symbol_kind in self.symbol_kinds:
            if content.startswith(symbol_kind.text_repr, start):
                return symbol_kind
        return None

    def add_block(self, block, tokens):
        """Convert block into a token if possible and add to tokens. If block is non-empty but cannot be made into a
        token, this function records a compiler error. We don't need to check for symbol kind tokens here because they
        are converted before they are shifted into the block.
            block (str) - block to convert into a token.
            tokens (List[Token]) - List of the tokens thusfar parsed.
        """
        if block:
            keyword_kind = self.match_keyword_kind(block)
            if keyword_kind:
                tokens.append(Token(keyword_kind))
                return

            number_string = self.match_number_string(block)
            char_string = self.match_char_string(block)
            if number_string:
                tokens.append(Token(token_kinds.number, number_string))
                return
            elif char_string:
                tokens.append(Token(token_kinds.number, char_string))
                return

            identifier_name = self.match_identifier_name(block)
            if identifier_name:
                tokens.append(Token(token_kinds.identifier, identifier_name))
                return

            desc = "unrecognized token at '{}'"
            error_collector.add(CompilerError(desc.format(block)))

    def ischar(self, token):
        """Check whether the submitted token is a char
            token - the token to check if it in char representation or not.
            returns (boolean) - True (1) if given token is char, False (0) if not.
        """
        return 1 if match(r'(\'.\')|(\".\")', token) else 0

    def isbinary(self, token):
        """Check whether the submitted token is a binary number
            token (int) - the int to check if it binary or not.
            returns (boolean) - True (1) if given int is in binary representation, False (0) if not.
        """
        return 1 if match(r'^0[bB][01]+$', token) else 0

    def isnegative(self, token):
        """Check whether the submitted token is a negative number
            token (int) - the int to check if it negative or not.
            returns (boolean) - True (1) if given int is in negative representation, False (0) if not.
        """
        return 1 if match(r'^-0[bB][01]+$', token) or match(r'^-[0-9]+$', token) else 0

    def char2num(self, sym):
        """Convert the given char into int number
            sym (char) - the char to make into a number.
            returns (int) - the int representation of the char.
        """
        return str(ord(sym[1:-1]))

    # These match_* functions can safely assume the input token_repr is non-empty.

    def match_keyword_kind(self, token_repr):
        """Find the longest keyword token kind with representation token_repr.
            token_repr (str) - Token representation to match exactly.
            returns (TokenKind, or None) - Keyword token kind that matched.
        """
        for keyword_kind in self.keyword_kinds:
            if keyword_kind.text_repr == token_repr:
                return keyword_kind
        return None

    def match_char_string(self, token_repr):
        """Return a string that represents the given constant character, or None if not possible
            token_repr (str) - the string to make into a token.
            returns (str, or None) - the string representation of the char.
        """
        return self.char2num(token_repr) if self.ischar(token_repr) else None

    def match_number_string(self, token_repr):
        """Return a string that represents the given constant number.
            token_repr (str) - String to make into a token.
            returns (str, or None) - String representation of the number.
        """
        if token_repr.isdigit(): return token_repr
        elif self.isnegative(token_repr): return token_repr
        elif self.isbinary(token_repr): return token_repr[2:] + 'B'

    def match_identifier_name(self, token_repr):
        """Return a string that represents the name of an identifier.
            token_repr (str) - String to make into a token.
            returns (str, or None) - String name of the identifier.
        """
        if match(r"[_a-zA-Z][_a-zA-Z0-9]*$", token_repr): return token_repr
        else: return None
