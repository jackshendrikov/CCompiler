"""Implements tests for the Parser class"""
import unittest

import ast
from errors import CompilerError
from myparser import Parser
import token_kinds
from tokens import Token


class parser_tests(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parse_main(self):
        """ int main() { return 27; } """
        tokens = [Token(token_kinds.int_kw), Token(token_kinds.main),
                  Token(token_kinds.open_paren), Token(token_kinds.close_paren),
                  Token(token_kinds.open_brack), Token(token_kinds.return_kw),
                  Token(token_kinds.number, "27"), Token(token_kinds.semicolon),
                  Token(token_kinds.close_brack)]

        ast_root = self.parser.parse(tokens)
        self.assertEqual(ast_root, ast.MainNode([ast.ReturnNode(ast.NumberNode(Token(token_kinds.number, "27")))]))

    def test_parse_bin_main(self):
        """ int main() { return 0b101; } """
        tokens = [Token(token_kinds.int_kw), Token(token_kinds.main),
                  Token(token_kinds.open_paren), Token(token_kinds.close_paren),
                  Token(token_kinds.open_brack), Token(token_kinds.return_kw),
                  Token(token_kinds.number, "0b101"), Token(token_kinds.semicolon),
                  Token(token_kinds.close_brack)]

        ast_root = self.parser.parse(tokens)
        self.assertEqual(ast_root, ast.MainNode([ast.ReturnNode(ast.NumberNode(Token(token_kinds.number, "0b101")))]))

    def test_parse_char_main(self):
        """ int main() { return 'd'; } """
        tokens = [Token(token_kinds.int_kw), Token(token_kinds.main),
                  Token(token_kinds.open_paren), Token(token_kinds.close_paren),
                  Token(token_kinds.open_brack), Token(token_kinds.return_kw),
                  Token(token_kinds.number, "100"), Token(token_kinds.semicolon),
                  Token(token_kinds.close_brack)]

        ast_root = self.parser.parse(tokens)
        self.assertEqual(ast_root, ast.MainNode([ast.ReturnNode(ast.NumberNode(Token(token_kinds.number, "100")))]))

    def test_parse_multiple_return(self):
        """ int main() { return 27; return 14; } """
        tokens = [Token(token_kinds.int_kw), Token(token_kinds.main),
                  Token(token_kinds.open_paren), Token(token_kinds.close_paren),
                  Token(token_kinds.open_brack),
                  Token(token_kinds.return_kw), Token(token_kinds.number, "27"),
                  Token(token_kinds.semicolon),
                  Token(token_kinds.return_kw), Token(token_kinds.number, "14"),
                  Token(token_kinds.semicolon),
                  Token(token_kinds.close_brack)]

        ast_root = self.parser.parse(tokens)
        self.assertEqual(ast_root,
                         ast.MainNode([ast.ReturnNode(ast.NumberNode(Token(token_kinds.number, "27"))),
                                       ast.ReturnNode(ast.NumberNode(Token(token_kinds.number, "14")))]))

    def test_extra_tokens_at_end(self):
        tokens = [Token(token_kinds.int_kw), Token(token_kinds.main),
                  Token(token_kinds.open_paren), Token(token_kinds.close_paren),
                  Token(token_kinds.open_brack), Token(token_kinds.return_kw),
                  Token(token_kinds.number, "27"), Token(token_kinds.semicolon),
                  Token(token_kinds.close_brack), Token(token_kinds.int_kw)]
        with self.assertRaisesRegex(CompilerError, "unexpected token at 'int'"):
            ast_root = self.parser.parse(tokens)

    def test_missing_end_of_main(self):
        tokens = [Token(token_kinds.int_kw), Token(token_kinds.main),
                  Token(token_kinds.open_paren), Token(token_kinds.close_paren),
                  Token(token_kinds.open_brack), Token(token_kinds.return_kw),
                  Token(token_kinds.number, "27")]
        with self.assertRaisesRegex(CompilerError, "expected semicolon after '27'"):
            ast_root = self.parser.parse(tokens)

    def test_missing_final_brace_main(self):
        """ Missing semicolon: int main() { return 27 } """
        tokens = [Token(token_kinds.int_kw), Token(token_kinds.main),
                  Token(token_kinds.open_paren), Token(token_kinds.close_paren),
                  Token(token_kinds.open_brack), Token(token_kinds.return_kw),
                  Token(token_kinds.number, "27"), Token(token_kinds.semicolon)]
        with self.assertRaisesRegex(CompilerError, "expected closing brace after ';'"):
            ast_root = self.parser.parse(tokens)


if __name__ == "__main__":
    unittest.main()
