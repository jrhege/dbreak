""" Holds functions and objects related to debug sessions """

from typing import TYPE_CHECKING, Dict

from .exc import ConnectionNotFoundError

if TYPE_CHECKING:
    from .connections import ConnectionWrapper


class DebugSession:
    """ Represents a debugging session """

    def __init__(self, connections: Dict[str, "ConnectionWrapper"], current_connection_name: [str, None] = None):
        """ Initialize a new DebugSession

        :param connections: Dict of named ConnectionWrapper objects
        :param current_connection_name: Name of the connection to use
        """

        # Make sure we've been given at least one connection
        if not connections:
            raise ConnectionNotFoundError("At least one database connection must be provided")

        # Pick an arbitrary starting connection if none is given
        if not current_connection_name:
            current_connection_name = next(iter(connections))

        # Holds a dictionary of ConnectionWrapper objects,
        # keyed by connection name
        self.connections = connections

        # Set via the current_connection_name property
        self._current_connection_name = None

        self.current_connection_name = current_connection_name

    @property
    def current_connection_name(self) -> str:
        """ Returns the name of the connection currently in use """

        return self._current_connection_name

    @property
    def current_connection(self) -> "ConnectionWrapper":
        """ Get a reference to the current connection """

        return self.connections[self.current_connection_name]

    @current_connection_name.setter
    def current_connection_name(self, name: str):
        """ Set the name of the current connection

        :param name: Name of the connection to use
        """

        # Ensure the connection actually exists
        if name not in self.connections:
            raise ConnectionNotFoundError(name)

        self._current_connection_name = name
