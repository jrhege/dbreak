""" Tests for commands.py module """

import pytest

import dbreak
import dbreak.exc
import dbreak.commands
import dbreak.connections
import dbreak.sessions


class TestExecuteCommand:
    """ Test the execute_command function """

    @pytest.fixture()
    def custom_debug_session(self, custom_connection, custom_connection_wrapper):
        """ Debug session with a custom connection type """

        raw_connection = custom_connection()

        connections = {
            "custom": custom_connection_wrapper(raw_connection)
        }

        return dbreak.sessions.DebugSession(
            current_connection_name="custom",
            connections=connections
        )

    def test_custom_command(self, custom_debug_session):
        """ Test executing a custom shell command """

        found = dbreak.commands.execute_command(
            "!doit",
            custom_debug_session
        )

        expected = "Did it"

        assert expected == found, "!doit returned unexpected output"

    def test_connections_command(self, basic_debug_session):
        """ Test executing the !connections command """

        outputs = dbreak.commands.execute_command(
            "!connections",
            basic_debug_session
        )

        expected = [
            ("conn1", "DBAPIWrapper", "sqlite3", "Connection"),
            ("conn2", "DBAPIWrapper", "sqlite3", "Connection")
        ]

        found = outputs[0].rows

        assert expected == found, "!connections returned unexpected output"

    def test_execute_in_database_command(self, basic_debug_session):
        """ Test executing a SQL command via !execute """

        outputs = dbreak.commands.execute_command(
            "!execute select 'a' as foo;",
            basic_debug_session
        )

        table = outputs[0]

        assert table.columns == ["foo"], "!execute returned unexpected columns"
        assert table.rows == [("a",)], "!execute returned unexpected columns"

    def test_exit_command(self, basic_debug_session):
        """ Test the !exit command """

        with pytest.raises(dbreak.exc.StopSession):
            dbreak.commands.execute_command(
                "!exit",
                basic_debug_session
            )

    def test_file_command(self, basic_debug_session, sql_file):
        """ Test the !file command """

        outputs = dbreak.commands.execute_command(
            f"!file {sql_file}",
            basic_debug_session
        )

        table = outputs[0]

        assert table.columns == ["foo"], "!execute returned unexpected columns"
        assert table.rows == [(1,)], "!execute returned unexpected columns"

    def test_help_command(self, custom_debug_session,):
        """ Test the !help command """

        outputs = dbreak.commands.execute_command(
            "!help",
            custom_debug_session
        )

        # Count rows
        expected_rows = 8
        found_rows = len(outputs[0].rows) + len(outputs[1].rows)

        assert expected_rows == found_rows, "!help returned an unexpected number of rows"

    def test_rename_command(self, basic_debug_session):
        """ Test the !rename command """

        dbreak.commands.execute_command(
            "!rename 'better name'",
            basic_debug_session
        )

        assert basic_debug_session.current_connection_name == "better name", "!rename failed"

    def test_switch_command(self, basic_debug_session):
        """ Test the !switch command """

        dbreak.commands.execute_command(
            "!switch conn2",
            basic_debug_session
        )

        assert basic_debug_session.current_connection_name == "conn2", "!switch failed"

    def test_unparsed_database_command(self, basic_debug_session):
        """ Test executing a SQL command without !execute """

        outputs = dbreak.commands.execute_command(
            "select 'a' as foo, 1 as bar;",
            basic_debug_session
        )

        table = outputs[0]

        assert table.columns == ["foo", "bar"], "Returned unexpected columns"
        assert table.rows == [("a", 1)], "Returned unexpected columns"


class TestFile:
    """ Tests for _file function """

    def test_invalid_path(self, basic_debug_session):
        """ Test if an invalid file path is given """

        with pytest.raises(FileNotFoundError):

            dbreak.commands._file(
                basic_debug_session,
                "this_is_not_a_real_file.txt"
            )


class TestRename:
    """ Tests for _rename function """

    def test_name_in_use_by_other(self, basic_debug_session):
        """ Test if the name given is already in use by a different connection """

        with pytest.raises(dbreak.exc.ConnectionAlreadyExistsError):

            dbreak.commands._rename(
                basic_debug_session,
                "conn2"
            )

    def test_name_in_use_by_self(self, basic_debug_session):
        """ Test if the name given is already in use by the current connection """

        dbreak.commands._rename(
            basic_debug_session,
            "conn1"
        )


class TestSwitch:
    """ Tests for _switch function """

    def test_no_connection(self, basic_debug_session):
        """ Test switching to a connection that does not exists """

        with pytest.raises(dbreak.exc.ConnectionNotFoundError):

            dbreak.commands._switch(
                basic_debug_session,
                "conn100"
            )
