""" Holds functions and classes related to managing and wrapping database connections """

import itertools
import pkg_resources
import operator

from typing import Tuple, Dict, Iterable, Generator, Type

from .constants import DEFAULT_CONNECTION_NAME_PATTERN


class ConnectionWrapper:
    """ Generic database connection wrapper, meant for subclassing """

    # Shows when using the "help" command. Used to describe what
    # kinds of non-shell commands can be issued (for example,
    # SQL queries, Redis commands, etc).
    HELP_TEXT = ""

    # When multiple ConnectionWrapper subclasses indicate
    # they can handle a connection, the one with the HIGHEST
    # SEARCH_RANK value will be chosen.

    # Recommended values:
    # -1 = Abstract class wrappers
    #  0 = Wrappers meant to cover a broad range of connection types (i.e. DB API)
    #  1 = Wrappers meant to cover connections from a specific package
    #  2 = User-defined wrappers
    SEARCH_RANK = -1

    def __init__(self, raw_connection: object):
        """ Initialize a ConnectionWrapper

        :param raw_connection: Database connection being wrapped
        """

        # Connection to the underlying database
        self.raw_connection = raw_connection

        # Any custom shell commands the user should
        # be allowed to use while connected to this
        # database. Follows the same format as
        # commands.SHELL_COMMANDS.
        self.custom_commands = {}

    def execute_statement(self, statement: str):
        """ Return the results of executing a database statement

        :param statement: Statement to execute in the database
        """

        raise NotImplementedError("Not implemented in base class")

    @classmethod
    def find_handler(cls, raw_connection: object) -> [None, Type["ConnectionWrapper"]]:
        """ Find an appropriate ConnectionWrapper class for a given connection

        :param raw_connection: Database connection to find wrapper class for
        """

        # Get all subclasses that can handle this connection
        # and then sort them by their SEARCH_RANK
        sorted_candidates = sorted(
            cls.find_handlers(raw_connection),
            key=operator.attrgetter("SEARCH_RANK")
        )

        # Return the class with the highest SEARCH_RANK, or None
        # if no classes are available
        try:
            return sorted_candidates[-1]
        except IndexError:
            return None

    @classmethod
    def find_handlers(cls, raw_connection: object) -> Generator[Type["ConnectionWrapper"], None, None]:
        """ Find all classes that can handle the given connection

        :param raw_connection: An unwrapped database connection to find wrapped for
        """

        if cls.handles(raw_connection):

            yield cls

        for subclass in cls.__subclasses__():

            yield from subclass.find_handlers(raw_connection)

    @classmethod
    def handles(cls, raw_connection: object) -> bool:
        """ Returns True if this class can wrap the given connection

        :param raw_connection: An unwrapped database connection to test
        """

        return False


def prepare_connections(unnamed_connections: Tuple, named_connections: Dict) -> Dict[str, ConnectionWrapper]:
    """ Wrap and name all provided named and unnamed connections

    :param unnamed_connections: Raw or wrapped db connections to assign default names
    :param named_connections: Raw or wrapped db connections with specific names attached
    """

    # Provide a name for all unnamed_connections and merge
    # the two iterables into a single iterable of (name, connection)
    # pairs.

    # Note: Technically possible for there to be name collisions,
    # but you'd really have to do it deliberately.
    named_raw_connections = itertools.chain(
        name_connections(unnamed_connections),
        named_connections.items()
    )

    # Wrap any connections that require it and return
    # a dictionary of connections keyed by name.
    return wrap_connections(
        named_raw_connections=named_raw_connections
    )


def name_connections(raw_connections: Iterable) -> Generator[Tuple[str, object], None, None]:
    """ Provide a name to an iterable of raw connection objects

    Yields (name, connection) tuples.

    :param raw_connections: Iterable of raw connection objects
    """

    for position, raw_connection in enumerate(raw_connections):

        name = DEFAULT_CONNECTION_NAME_PATTERN.format(number=position)

        yield name, raw_connection


def wrap_connections(named_raw_connections: Iterable[Tuple[str, object]]) -> Dict[str, ConnectionWrapper]:
    """ Wrap all connections in ConnectionWrappers and produce a name-keyed dictionary

    :param named_raw_connections: Iterable of (name, raw connection) tuples
    """

    return {
        name: wrap_connection(
            raw_connection=raw_connection
        )
        for name, raw_connection
        in named_raw_connections
    }


def wrap_connection(raw_connection: object) -> ConnectionWrapper:
    """ Wrap a connection in the appropriate ConnectionWrapper

    :param raw_connection: A database connection
    """

    if isinstance(raw_connection, ConnectionWrapper):
        return raw_connection

    # Functions used to search for potential wrappers
    search_functions = (
        _search_loaded_wrappers,
        _search_entry_points
    )

    # Apply all search functions to the raw connection
    # and return an initialized wrapper if a match is found
    for search_function in search_functions:

        wrapper_class = search_function(raw_connection)

        if wrapper_class is not None:

            return wrapper_class(
                raw_connection=raw_connection
            )

    raise TypeError(f"Could not find connection wrapper for {type(raw_connection).__name__}")


def _search_loaded_wrappers(raw_connection: object) -> [Type[ConnectionWrapper], None]:
    """ Search ConnectionWrapper for subclasses that handle a connection type

    :param raw_connection: A database connection
    """

    return ConnectionWrapper.find_handler(raw_connection)


def _search_entry_points(raw_connection: object) -> [Type[ConnectionWrapper], None]:
    """ Search package entry points for plugins

    :param raw_connection: A database connection
    """

    for entry_point in pkg_resources.iter_entry_points('connection_wrappers'):
        wrapper_class = entry_point.load()

        if wrapper_class.handles(raw_connection):
            return wrapper_class
