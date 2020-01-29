""" Tests for dbapi.py module """

import pytest


class TestDBAPIWrapper:
    """ Test usage of DBAPIWrapper functions """

    @pytest.fixture()
    def connection(self, basic_wrapped_connections):
        """ A single wrapped SQLite connection """

        return basic_wrapped_connections["conn1"]

    @pytest.fixture()
    def connection_with_table(self, connection):
        """ A SQLite connection with a table with 1 row """

        connection.raw_connection.execute(
            "CREATE TABLE foobar (i int, a varchar(255))"
        )

        connection.raw_connection.execute(
            "insert into foobar select 100, 'sample-record'"
        )

        return connection

    def test_create_table(self, connection):
        """ Test output of a create table statement """

        outputs = connection.execute_statement(
            "create table foobar (i int, a varchar(255));"
        )

        assert outputs == [], "Unexpected outputs returned"

    def test_select(self, connection):
        """ Test output of a select statement """

        outputs = connection.execute_statement(
            "select 1 as foo, '100' as bar;"
        )

        table = outputs[0]

        assert table.rows == [(1, "100")], "Unexpected rows returned"
        assert table.columns == ["foo", "bar"], "Unexpected columns returned"
        assert len(outputs) == 1, "Wrong number of outputs"

    def test_select_datetime(self, connection):
        """ Test output of a select statement with a datetime """

        outputs = connection.execute_statement(
            "select datetime('2000-01-01 00:00:00') as the_datetime;"
        )

        table = outputs[0]

        assert table.rows == [('2000-01-01 00:00:00',)], "Unexpected rows returned"
        assert table.columns == ["the_datetime"], "Unexpected columns returned"
        assert len(outputs) == 1, "Wrong number of outputs"

    def test_insert(self, connection_with_table):
        """ Test output of an insert statement """

        outputs = connection_with_table.execute_statement(
            "insert into foobar select 1, 'hello'"
        )

        assert outputs == []

    def test_update(self, connection_with_table):
        """ Test output of an update statement """

        outputs = connection_with_table.execute_statement(
            "update foobar set i = 7"
        )

        assert outputs == [], "Unexpected message returned"

    def test_delete(self, connection_with_table):
        """ Test output of an delete statement """

        outputs = connection_with_table.execute_statement(
            "delete from foobar"
        )

        assert outputs == []
