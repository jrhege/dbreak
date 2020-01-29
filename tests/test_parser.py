""" Tests for parser.py module """

import pytest

import dbreak
import dbreak.exc
import dbreak.parser


@pytest.fixture(scope="module")
def command_lookup():
    """ Example lookup for shell commands """

    return {
        "execute": {
            "func": lambda: "execute",
            "description": "Execute a statement against the database",
            "arguments": ["statement"],
            "verbose_final_argument": True
        },

        "single-arg-not-verbose": {
            "func": lambda: "single-arg-not-verbose",
            "description": "Command taking single verbose argument",
            "arguments": ["a1"],
            "verbose_final_argument": False
        },

        "single-arg-verbose": {
            "func": lambda: "single-arg-verbose",
            "description": "Command taking single, non-verbose argument",
            "arguments": ["a1"],
            "verbose_final_argument": True
        },

        "multi-args-not-verbose": {
            "func": lambda: "multi-args-not-verbose",
            "description": "Command taking multiple arguments without verbose final argument",
            "arguments": ["a1", "a2"],
            "verbose_final_argument": False
        },

        "multi-args-verbose": {
            "func": lambda: "multi-args-verbose",
            "description": "Command taking multiple arguments with verbose final argument",
            "arguments": ["a1", "a2"],
            "verbose_final_argument": True
        },

        "no-args": {
            "func": lambda: "no-args",
            "description": "Command taking no arguments",
            "arguments": [],
            "verbose_final_argument": False
        }

    }


class TestParse:
    """ Tests for the parse function """

    def test_parse_no_args(self, command_lookup):
        """ Parse a command with no arguments """

        func, arguments = dbreak.parser.parse(
            "!no-args",
            command_lookup
        )

        assert func() == "no-args", "Wrong function chosen"
        assert arguments == [], "Wrong number of arguments parsed"

    def test_parse_no_args_with_args_given(self, command_lookup):
        """ Parse a command expecting no arguments given arguments """

        with pytest.raises(dbreak.exc.WrongNumberOfArgumentsError):

            dbreak.parser.parse(
                "!no-args arg1",
                command_lookup
            )

    def test_parse_single_non_verbose_argument(self, command_lookup):
        """ Parse a command expecting 1 non-verbose argument """

        func, arguments = dbreak.parser.parse(
            "!single-arg-not-verbose arg1",
            command_lookup
        )

        assert func() == "single-arg-not-verbose", "Wrong function chosen"
        assert arguments == ["arg1"], "Wrong number of arguments parsed"

    def test_parse_single_non_verbose_with_multiple_arguments(self, command_lookup):
        """ Parse a command expecting 1 non-verbose argument with multiple arguments given """

        with pytest.raises(dbreak.exc.WrongNumberOfArgumentsError):

            dbreak.parser.parse(
                "!single-arg-not-verbose this is a test",
                command_lookup
            )

    def test_parse_single_quoted_argument(self, command_lookup):
        """ Parse a single quoted argument """

        func, arguments = dbreak.parser.parse(
            "!single-arg-not-verbose 'this is a test'",
            command_lookup
        )

        assert func() == "single-arg-not-verbose", "Wrong function chosen"
        assert arguments == ["this is a test"], "Wrong number of arguments parsed"

    def test_parse_single_nested_quote_argument(self, command_lookup):
        """ Parse a single quoted argument with nested quotes """

        func, arguments = dbreak.parser.parse(
            "!single-arg-not-verbose 'this \"is a\" test'",
            command_lookup
        )

        assert func() == "single-arg-not-verbose", "Wrong function chosen"
        assert arguments == ['this "is a" test'], "Wrong number of arguments parsed"

    def test_parse_single_verbose_argument(self, command_lookup):
        """ Parse a single verbose argument """

        func, arguments = dbreak.parser.parse(
            "!single-arg-verbose this isn't 'a test' of the emergency",
            command_lookup
        )

        assert func() == "single-arg-verbose", "Wrong function chosen"
        assert arguments == ["this isn't 'a test' of the emergency"], "Wrong number of arguments parsed"

    def test_parse_multi_arguments_non_verbose(self, command_lookup):
        """ Parse multiple non-verbose arguments """

        func, arguments = dbreak.parser.parse(
            "!multi-args-not-verbose foo 'second argument'",
            command_lookup
        )

        assert func() == "multi-args-not-verbose", "Wrong function chosen"
        assert arguments == ["foo", "second argument"], "Wrong number of arguments parsed"

    def test_parse_multi_arguments_verbose(self, command_lookup):
        """ Parse multiple arguments, with the last one verbose """

        func, arguments = dbreak.parser.parse(
            "!multi-args-verbose foo select '100'",
            command_lookup
        )

        assert func() == "multi-args-verbose", "Wrong function chosen"
        assert arguments == ["foo", "select '100'"], "Wrong number of arguments parsed"

    def test_parse_insufficient_arguments(self, command_lookup):
        """ Parse a statement with a missing argument """

        with pytest.raises(dbreak.exc.WrongNumberOfArgumentsError):

            dbreak.parser.parse(
                "!multi-args-verbose 'select 100'",
                command_lookup
            )

    def test_parse_trailing_whitespace(self, command_lookup):
        """ Parse a statement with a whitespace argument """

        with pytest.raises(dbreak.exc.WrongNumberOfArgumentsError):

            dbreak.parser.parse(
                "!multi-args-not-verbose 'select 100'  ",
                command_lookup
            )

    def test_parse_database_statement(self, command_lookup):
        """ Parse a statement that goes directly to the database """

        func, arguments = dbreak.parser.parse(
            "select '100', '200', '300'",
            command_lookup
        )

        assert func() == "execute", "Wrong function chosen"
        assert arguments == ["select '100', '200', '300'"], "Wrong number of arguments parsed"
