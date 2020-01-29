""" Tests for connections.py module """

import pytest

import dbreak
import dbreak.exc
import dbreak.connections


class TestConnectionWrapper:
    """ Tests for ConnectionWrapper class """

    @pytest.fixture()
    def wrapper_subclasses(self, custom_connection):
        """ Provides multiple ConnectionWrapper subclasses """

        class L1_1(dbreak.connections.ConnectionWrapper):
            """ Top-level wrapper """

            SEARCH_RANK = 1

            @classmethod
            def handles(cls, raw_connection: object) -> bool:

                return type(raw_connection) is custom_connection

        class L1_2(dbreak.connections.ConnectionWrapper):
            """ Another top-level wrapper """

            SEARCH_RANK = 1

            @classmethod
            def handles(cls, raw_connection: object) -> bool:
                return type(raw_connection) is custom_connection

        class L2_1(L1_1):
            """ A nested wrapper """

            SEARCH_RANK = 1

        class L2_2(L1_1):
            """ Another nested wrapper """

            SEARCH_RANK = 1

        class L2_3(L1_1):
            """ A nested wrapper that doesn't handle custom_connection """

            SEARCH_RANK = 1

            @classmethod
            def handles(cls, raw_connection: object) -> bool:
                return False

        return {
            "L1": [L1_1, L1_2],
            "L2": [L2_1, L2_2, L2_3],
        }

    def test_find_handler_level_1(self, wrapper_subclasses, custom_connection):
        """ Tests whether find_handler finds the correct ConnectionWrapper child """

        connection = custom_connection()

        desired_class = wrapper_subclasses["L1"][1]
        desired_class.SEARCH_RANK = 2

        found_class = dbreak.connections.ConnectionWrapper.find_handler(connection)

        assert found_class is desired_class

    def test_find_handler_level_2(self, wrapper_subclasses, custom_connection):
        """ Tests whether find_handler finds the correct ConnectionWrapper grandchild """

        connection = custom_connection()

        desired_class = wrapper_subclasses["L2"][1]
        desired_class.SEARCH_RANK = 2

        found_class = dbreak.connections.ConnectionWrapper.find_handler(connection)

        assert found_class is desired_class

    def test_find_handler_only_valid_wrappers(self, wrapper_subclasses, custom_connection):
        """ Tests whether find_handler is filtering out non-handling wrappers correctly """

        connection = custom_connection()

        # This wrapper handles custom_connection
        desired_class = wrapper_subclasses["L2"][1]
        desired_class.SEARCH_RANK = 2

        # This wrapper does NOT handle custom_connection
        bad_class = wrapper_subclasses["L2"][2]
        bad_class.SEARCH_RANK = 9999

        found_class = dbreak.connections.ConnectionWrapper.find_handler(connection)

        assert found_class is desired_class


class TestPrepareConnections:
    """ Tests for prepare_connections function """

    def test_unnamed_connections(self, basic_raw_connections):
        """ Test unnamed connections are given the correct names """

        connections_tuple = tuple(basic_raw_connections.values())

        wrapped_connections = dbreak.connections.prepare_connections(
            unnamed_connections=connections_tuple,
            named_connections={}
        )

        expected = {
            "db[0]": id(connections_tuple[0]),
            "db[1]": id(connections_tuple[1])
        }

        found = {
            name: id(connection.raw_connection)
            for name, connection
            in wrapped_connections.items()
        }

        assert expected == found, "Incorrect or wrong number of connections"

    def test_named_connections(self, basic_raw_connections):
        """ Test named connections are given the correct names """

        wrapped_connections = dbreak.connections.prepare_connections(
            unnamed_connections=tuple(),
            named_connections=basic_raw_connections
        )

        expected = {
            "conn1": id(basic_raw_connections["conn1"]),
            "conn2": id(basic_raw_connections["conn2"]),
        }

        found = {
            name: id(connection.raw_connection)
            for name, connection
            in wrapped_connections.items()
        }

        assert expected == found, "Incorrect or wrong number of connections"

    def test_mixed_connections(self, basic_raw_connections):
        """ Test named and unnamed connections together """

        unnamed_connections = (basic_raw_connections["conn1"],)

        named_connections = {
            "conn2": basic_raw_connections["conn2"]
        }

        wrapped_connections = dbreak.connections.prepare_connections(
            unnamed_connections=unnamed_connections,
            named_connections=named_connections
        )

        expected = {
            "db[0]": id(basic_raw_connections["conn1"]),
            "conn2": id(basic_raw_connections["conn2"]),
        }

        found = {
            name: id(connection.raw_connection)
            for name, connection
            in wrapped_connections.items()
        }

        assert expected == found, "Incorrect or wrong number of connections"


class TestNameConnections:
    """ Test name_connections function """

    def test_naming_connections(self, basic_raw_connections):
        """ Test connections are named appropriately """

        connections = basic_raw_connections.values()

        name_connection_tuples = dbreak.connections.name_connections(connections)

        expected = ["db[0]", "db[1]"]
        found = [name for name, _ in name_connection_tuples]

        assert expected == found, "Incorrect names found"


class TestWrapConnection:
    """ Test wrap_connection function """

    def test_sqlite_connection(self, basic_raw_connections):
        """ Test wrapping a raw SQLite connection """

        connection = basic_raw_connections["conn1"]

        wrapped = dbreak.connections.wrap_connection(connection)

        assert isinstance(wrapped, dbreak.DBAPIWrapper), "Wrong ConnectionWrapper returned"

    def test_pre_wrapped_connection(self, basic_wrapped_connections):
        """ Test providing a wrapped connection returns it """

        connection = basic_wrapped_connections["conn1"]

        wrapped = dbreak.connections.wrap_connection(connection)

        assert id(connection) == id(wrapped), "Object IDs do not match"

    def test_invalid_connection(self):
        """ Test trying to wrap an invalid object """

        with pytest.raises(TypeError):
            dbreak.connections.wrap_connection(list())

    def test_custom_wrapper(self, custom_connection, custom_connection_wrapper):
        """ Test wrapping a custom connection type with a custom wrapper """

        connection = custom_connection()

        wrapped = dbreak.connections.wrap_connection(connection)

        assert isinstance(wrapped, custom_connection_wrapper), "Wrong wrapper returned"
