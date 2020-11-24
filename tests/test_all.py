from errors import error_collector
import glob
import main
import unittest


def compile_with_jackshenc(test_file_name):
    """Compile given file with JackShenC. Errors are saved in the error collector."""

    class MockArguments:
        filename = test_file_name
        show_il = False
        show_reg_alloc_perf = False
        variables_on_stack = False

    main.get_arguments = lambda: MockArguments()

    # Mock out error collector functions
    error_collector.show = lambda: True

    main.main()


def new(glob_str, dct):
    """The implementation of __new__ used for generating tests."""
    def generate_test(test_file_name):
        def test_function(self):
            # Read test parameters from test file
            with open(test_file_name) as f:
                ret_val = 0

                exp_errors = []
                exp_error_lines = []

                exp_warnings = []
                exp_warning_lines = []

                for index, line in enumerate(f.readlines()):
                    ret_mark = "// Return:"
                    error_mark = "// error:"
                    warning_mark = "// warning:"

                    if line.strip().startswith(ret_mark):
                        ret_val = int(line.split(ret_mark)[-1])
                    elif line.strip().startswith(error_mark):
                        exp_errors.append(
                            line.split(error_mark)[-1].strip())
                        exp_error_lines.append(index + 2)
                    elif line.strip().startswith(warning_mark):
                        exp_warnings.append(
                            line.split(warning_mark)[-1].strip())
                        exp_warning_lines.append(index + 2)

            compile_with_jackshenc(test_file_name)

            act_errors = []
            act_error_lines = []

            act_warnings = []
            act_warning_lines = []

            for issue in error_collector.issues:
                if issue.warning:
                    act_warnings.append(issue.descr)
                    act_warning_lines.append(issue.span.start.line)
                else:
                    act_errors.append(issue.descr)
                    act_error_lines.append(issue.span.start.line)

            self.assertListEqual(act_errors, exp_errors)
            self.assertListEqual(act_error_lines, exp_error_lines)

            self.assertListEqual(act_warnings, exp_warnings)
            self.assertListEqual(act_warning_lines, exp_warning_lines)


        return test_function

    test_file_name = glob.glob(glob_str)
    for test_file_name in test_file_name:
        short_name = test_file_name.split("/")[-1][:-2]
        test_func_name = "test_" + short_name
        dct[test_func_name] = generate_test(test_file_name)


class TestUtils(unittest.TestCase):
    """Helper base class for all unit tests."""

    def setUp(self):
        """Clear error collector before each test."""
        error_collector.clear()


class MetaFrontendTests(type):
    """Metaclass for creating frontend tests."""

    def __new__(meta, name, bases, dct):
        """Create FrontendTests class."""
        new("tests/frontend_tests/*.c", dct)
        return super().__new__(meta, name, bases, dct)


class FrontendTests(TestUtils, metaclass=MetaFrontendTests):
    """Frontend tests that test the lexer, preprocessor, and myparser."""

    pass


class MetaFeatureTests(type):
    """Metaclass for creating feature tests."""

    def __new__(meta, name, bases, dct):
        """Create FeatureTests class."""
        new("tests/feature_tests/*.c", dct)
        done_class = super().__new__(meta, name, bases, dct)
        return done_class


class FeatureTests(TestUtils, metaclass=MetaFeatureTests):
    """Frontend tests that test the lexer, preprocessor, and myparser."""

    pass
