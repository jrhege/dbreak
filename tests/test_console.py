""" Tests for console.py module """

import dbreak.console
import dbreak.outputs
import dbreak.exc


class TestDisplayOutputs:
    """ Tests for _display_outputs function """

    def test_output_none(self, capsys):
        """ Test giving no outputs for display """

        dbreak.console._display_outputs(None)

        out, err = capsys.readouterr()

        assert out == "", "Unexpected output"

    def test_output_empty_list(self, capsys):
        """ Test giving an empty list for display """

        dbreak.console._display_outputs([])

        out, err = capsys.readouterr()

        assert out == "", "Unexpected output"

    def test_output_multiple_items(self, capsys):
        """ Test giving multiple items for display """

        table = dbreak.outputs.TableOutput(
            rows=[("a", 1), ("b", 2)],
            columns=["letter", "number"]
        )

        dbreak.console._display_outputs(
            [
                table,
                "This is a message",
                {"message": "This is a dict"}
            ]
        )

        out, err = capsys.readouterr()

        expected = [
            "",
            "========  ========",
            "letter      number",
            "========  ========",
            "a                1",
            "b                2",
            "========  ========",
            "(2 row(s) returned)",
            "",
            "This is a message",
            "",
            "{'message': 'This is a dict'}",
            "\n"
        ]

        assert out == "\n".join(expected), "Unexpected output"


class TestDisplayOutput:
    """ Test the _display_output function """

    def test_display_table(self, capsys):
        """ Test displaying a table """

        table = dbreak.outputs.TableOutput(
            rows=[("a", 1), ("b", 2)],
            columns=["letter", "number"]
        )

        dbreak.console._display_output(table)

        out, err = capsys.readouterr()

        expected = [
            "",
            "========  ========",
            "letter      number",
            "========  ========",
            "a                1",
            "b                2",
            "========  ========",
            "(2 row(s) returned)",
            ""
        ]

        assert out == "\n".join(expected), "Unexpected output"

    def test_display_exception(self, capsys):
        """ Test displaying an exception """

        ex = dbreak.exc.UnknownCommandError("foo")

        dbreak.console._display_output(ex)

        out, err = capsys.readouterr()

        expected = [
            "Error: UnknownCommandError",
            "foo",
            ""
        ]

        assert err == "\n".join(expected), "Unexpected output"
