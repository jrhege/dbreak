""" Tests for sessions.py module """

import sqlite3

import pytest

import dbreak
import dbreak.exc
import dbreak.sessions


class TestDebugSession:
    """ Tests related to the DebugSession object """

    def test_basic_init(self):
        """ Test a basic initialization with two connections """

        connection = dbreak.DBAPIWrapper(sqlite3.connect(":memory:"))

        connections = {
            "conn1": connection
        }

        session = dbreak.sessions.DebugSession(
            connections=connections,
            current_connection_name="conn1"
        )

        assert session.current_connection_name == "conn1"

    def test_init_invalid_connection_name(self):
        """ Test an initialization with an invalid current_connection_name """

        connection = dbreak.DBAPIWrapper(sqlite3.connect(":memory:"))

        connections = {
            "conn1": connection
        }

        with pytest.raises(dbreak.exc.ConnectionNotFoundError):

            dbreak.sessions.DebugSession(
                connections=connections,
                current_connection_name="conn2"
            )

    def test_set_current_connection_name(self, basic_debug_session):
        """ Test switching connection names works as expected """

        basic_debug_session.current_connection_name = "conn2"

        assert basic_debug_session.current_connection_name == "conn2", "Wrong connection in use"

    def test_set_invalid_connection_name(self, basic_debug_session):
        """ Test attempting to switch to an invalid connection """

        with pytest.raises(dbreak.exc.ConnectionNotFoundError):
            basic_debug_session.current_connection_name = "conn100"

    def test_get_connection(self, basic_debug_session):
        """ Test retrieving the current connection through the current_connection property """

        expected = id(basic_debug_session.connections["conn1"])
        found = id(basic_debug_session.current_connection)

        assert expected == found

    def test_with_starting_name(self, basic_wrapped_connections):
        """ Test session is starting correctly when given a starting name """

        session = dbreak.sessions.DebugSession(
            current_connection_name="conn2",
            connections=basic_wrapped_connections
        )

        expected = id(basic_wrapped_connections["conn2"])
        found = id(session.current_connection)

        assert expected == found, "Wrong connection in use"

    def test_without_starting_name(self, basic_wrapped_connections):
        """ Test session is starting correctly when not given starting name """

        session = dbreak.sessions.DebugSession(
            connections=basic_wrapped_connections
        )

        current_connection = id(session.current_connection)

        possible_connections = {
            id(connection)
            for connection
            in basic_wrapped_connections.values()
        }

        assert current_connection in possible_connections, "Wrong connection in use"

    def test_no_connections_given(self):
        """ Test creating a session without connection (fails) """

        with pytest.raises(dbreak.exc.ConnectionNotFoundError):

            dbreak.sessions.DebugSession(
                connections={}
            )
