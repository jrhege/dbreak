""" Containers for data returned by a command

These Output objects specify how the data is formatted, not how it
should be displayed. A TableOutput, for example, could be displayed
as an HTML table, an ASCII table, etc.
"""

from typing import Iterable


class TableOutput:
    """ Represents data output in tabular form """

    def __init__(self, rows: Iterable, columns: Iterable[str]):
        """ Construct a new TableOutput

        :param rows: Iterable of rows
        :param columns: Iterable of column names
        """

        self.rows = rows
        self.columns = columns
