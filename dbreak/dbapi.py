""" ConnectionWrapper and functions for DB API database console access """

from typing import List

from .connections import ConnectionWrapper
from .outputs import TableOutput


class DBAPIWrapper(ConnectionWrapper):
    """ Wraps DB API connection objects to support console access """

    # This is given a low SEARCH_RANK so that more
    # specific database connectors can take precedence
    SEARCH_RANK = 0

    def execute_statement(self, statement: str) -> List:
        """ Return the results of executing a database statement

        :param statement: Statement to execute in the database
        """

        # Execute the statement and get a cursor for the results
        cursor = self.raw_connection.cursor()

        try:
            outputs = self._execute(
                cursor=cursor,
                statement=statement
            )
        finally:
            cursor.close()

        return outputs

    def _execute(self, cursor, statement: str) -> List:
        """ Execute a statement against a cursor and return a list of outputs

        :param cursor: DB API cursor object
        :param statement: Statement to execute
        """

        # Execute the query
        cursor.execute(statement)

        # Attempt to read the columns that appear in the
        # resultset. This won't return anything for
        # most non-select commands.
        columns = _read_resultset_columns(cursor)

        # If no columns are mentioned in the cursor description
        # then there's no more data to return
        if not columns:
            return []

        # Pull all results out of the cursor
        rows = list(cursor)

        # Put the data into tabular format
        table = TableOutput(
            rows=rows,
            columns=columns
        )

        # Return the list of outputs
        return [table]

    @classmethod
    def handles(cls, raw_connection: object) -> bool:
        """ Returns True if raw_connection is DB API compliant

        :param raw_connection: An unwrapped database connection
        """

        # Check for attributes that should be defined on
        # a DB API compliant connection
        return all(
            (
                hasattr(raw_connection, "cursor"),
                hasattr(raw_connection, "commit"),
                hasattr(raw_connection, "close")
            )
        )


def _read_resultset_columns(cursor) -> List[str]:
    """ Read names of all columns returned by a cursor

    :param cursor: Cursor to read column names from
    """

    if cursor.description is None:
        return []
    else:
        return [x[0] for x in cursor.description]
