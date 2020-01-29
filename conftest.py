""" Shared fixtures for tests """

import sqlite3

import pytest

import dbreak
import dbreak.sessions


@pytest.fixture()
def basic_raw_connections():
    """ Couple of basic unwrapped SQLite connections """

    return {
        "conn1": sqlite3.connect(":memory:"),
        "conn2": sqlite3.connect(":memory:")
    }


@pytest.fixture()
def basic_wrapped_connections():
    """ Couple of in-memory wrapped SQLite connections """

    return {
        "conn1": dbreak.DBAPIWrapper(sqlite3.connect(":memory:")),
        "conn2": dbreak.DBAPIWrapper(sqlite3.connect(":memory:"))
    }


@pytest.fixture()
def custom_connection():
    """ Generate a custom database connection class """

    class SomeDatabaseConnection:

        pass

    return SomeDatabaseConnection


@pytest.fixture()
def custom_connection_wrapper(custom_connection):
    """ Generate a wrapper for the custom database connection class"""

    class SomeDatabaseWrapper(dbreak.ConnectionWrapper):

        def __init__(self, raw_connection: object):

            super().__init__(raw_connection)

            self.custom_commands = {
                "doit": {
                    "func": self._doit,
                    "description": "Do the thing",
                    "arguments": [],
                    "verbose_final_argument": False
                }
            }

        @staticmethod
        def _doit(_):
            return "Did it"

        @classmethod
        def handles(cls, raw_connection):

            return type(raw_connection) == custom_connection

    return SomeDatabaseWrapper


@pytest.fixture()
def basic_debug_session(basic_wrapped_connections):
    """ A basic DebugSession object with two SQLite connections """

    return dbreak.sessions.DebugSession(
        current_connection_name="conn1",
        connections=basic_wrapped_connections
    )


@pytest.fixture()
def sql_file(tmp_path):
    """ Construct a file containing a SQL statement """

    directory = tmp_path / "sql"

    directory.mkdir()

    file = directory / "sql.txt"

    file.write_text("SELECT\n 1 as foo;")

    return file.absolute()
