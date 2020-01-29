""" Functions handling the execution of commands, either locally or against a database """

from typing import TYPE_CHECKING, Dict, List

from .constants import SHELL_COMMAND_INDICATOR
from .exc import StopSession, ConnectionAlreadyExistsError
from .parser import parse
from .outputs import TableOutput

if TYPE_CHECKING:
    from .sessions import DebugSession


def execute_command(command_string: str, session: "DebugSession") -> [List, None]:
    """ Parse and execute a command entered by the user

    :param command_string: Commands entered by the user
    :param session: Current DebugSession
    """

    # Shell commands are defined both globally and for
    # individual ConnectionWrapper classes. Merge the
    # two dictionaries together for a complete list
    # of commands.
    merged_command_list = {
        **SHELL_COMMANDS,
        **session.current_connection.custom_commands
    }

    # Parse the command string into one command function
    # and an iterable of arguments to provide to it
    command_func, arguments = parse(
        command_string=command_string,
        shell_command_lookup=merged_command_list
    )

    # Run the command and return results
    return command_func(session, *arguments)


def _connections(session: "DebugSession") -> List[TableOutput]:
    """ Return names of all connections available for use

    :param session: Current DebugSession
    """

    columns = [
        "Connection Name",
        "Wrapper Type",
        "Raw Connection Module",
        "Raw Connection Class",
    ]

    # Construct rows with the connection name, wrapper type, and raw connection type
    rows = [
        (
            name,
            type(wrapper).__name__,
            type(wrapper.raw_connection).__module__,
            type(wrapper.raw_connection).__name__
        )
        for name, wrapper
        in session.connections.items()
    ]

    return [
        TableOutput(
            rows=rows,
            columns=columns
        )
    ]


def _execute_in_database(session: "DebugSession", statement: str) -> [List, None]:
    """ Execute a database command

    :param session: Current DebugSession
    :param statement: Text of statement to execute
    """

    return session.current_connection.execute_statement(statement)


def _exit(_):
    """ Exit the console application """

    raise StopSession()


def _file(session: "DebugSession", file_path: str) -> [List, None]:
    """ Read and execute a database command from a file

    :param session: Current DebugSession
    :param file_path: Path of file containing database statement
    """

    with open(file_path) as file:

        statement = file.read()

    return _execute_in_database(
        session=session,
        statement=statement
    )


def _help(session: "DebugSession") -> List:
    """ Display command help for both general and connection-specific commands

    :param session: Current DebugSession
    """

    # Construct a help table for standard shell commands
    outputs = [
        _create_help_table(
            first_column_name="Standard Commands",
            command_lookup=SHELL_COMMANDS
        )
    ]

    # Get the current connection and any associated custom commands
    current_connection = session.current_connection

    custom_commands = current_connection.custom_commands

    # Construct a help table for custom commands, if any
    if custom_commands:

        outputs.append(
            _create_help_table(
                first_column_name="Database-Specific Commands",
                command_lookup=custom_commands
            )
        )

    # Output connection-specific HELP_TEXT if available
    if current_connection.HELP_TEXT:

        outputs.append(f"{current_connection.HELP_TEXT}")

    return outputs


def _create_help_table(first_column_name: str, command_lookup: Dict[str, dict]) -> TableOutput:
    """ Construct a table of commands

    :param first_column_name: Name to use for first table column
    :param command_lookup: Lookup of commands to use when creating table
    """

    # Construct table columns
    columns = [
        first_column_name,
        "Arguments",
        "Description"
    ]

    # Construct table rows
    # Example console output:
    #
    # !execute  statement   List connection names available for switch statement
    rows = [
        (
            f"{SHELL_COMMAND_INDICATOR}{command}",
            " ".join(details['arguments']),
            details['description']
        )
        for command, details
        in command_lookup.items()
    ]

    return TableOutput(
        rows=rows,
        columns=columns
    )


def _rename(session: "DebugSession", connection_name: str):
    """ Rename the current connection

    :param session: Current DebugSession
    :param connection_name: New name to use for the connection
    """

    # Don't allow renaming connections to a name already in use,
    # unless we're for some reason renaming the current connection
    # to the name already in use
    if connection_name == session.current_connection_name:
        return

    elif connection_name in session.connections:
        message = f"Connection named '{connection_name}' already exists"
        raise ConnectionAlreadyExistsError(message)

    # Name of the current connection
    current_name = session.current_connection_name

    # Rename the connection in the session's connection lookup
    session.connections[connection_name] = session.connections.pop(current_name)

    # Reset the current connection name to the new name
    session.current_connection_name = connection_name


def _switch(session: "DebugSession", connection_name: str):
    """ Switch to a different connection

    :param session: Current DebugSession
    :param connection_name: Name of the connection
    """

    # Validity will be checked by the session object
    session.current_connection_name = connection_name


# Commands available to all connections
# Individual custom_commands dicts defined in ConnectionWrapper
# objects should follow this same format.
SHELL_COMMANDS = {
    "connections": {
        "func": _connections,
        "description": "List connections available for switch statement",
        "arguments": [],
        "verbose_final_argument": False
    },

    "execute": {
        "func": _execute_in_database,
        "description": "Execute a statement against the database",
        "arguments": ["statement"],
        "verbose_final_argument": True
    },

    "exit": {
        "func": _exit,
        "description": "Exit debugger and resume application",
        "arguments": [],
        "verbose_final_argument": False
    },

    "file": {
        "func": _file,
        "description": "Read and execute a database statement from a file",
        "arguments": ["path"],
        "verbose_final_argument": True
    },

    "help": {
        "func": _help,
        "description": "Show debugger help information",
        "arguments": [],
        "verbose_final_argument": False
    },

    "rename": {
        "func": _rename,
        "description": "Rename the current connection",
        "arguments": ["name"],
        "verbose_final_argument": True
    },

    "switch": {
        "func": _switch,
        "description": "Switch to another connection",
        "arguments": ["connection"],
        "verbose_final_argument": True
    }
}
