""" Holds functions related to the interactive debugging console """

import sys

from typing import Iterable

import tabulate

from .connections import prepare_connections
from .constants import SHELL_COMMAND_INDICATOR
from .commands import execute_command
from .exc import StopSession
from .sessions import DebugSession
from .outputs import TableOutput


def start_console(*unnamed_connections: object, starting_connection: str = None,
                  **named_connections: object):
    """ Pause execution and start a database debugging console

    Supports both named and unnamed connections, as well as both raw
    and pre-wrapped connections. Connections provided via *unnamed_connections
    will be named using const.DEFAULT_CONNECTION_NAME_PATTERN in the order
    they are provided. A starting_connection string may be provided to select
    which connection is opened up with the console.

    :param unnamed_connections: Raw or wrapped db connections to assign default names
    :param starting_connection: Name of the connection to use at startup
    :param named_connections: Raw or wrapped db connections with specific names attached
    """

    if not isinstance(starting_connection, str) and starting_connection is not None:
        raise TypeError("starting_connection must be a string or None")

    # Wrap and name all connections
    connections = prepare_connections(
        unnamed_connections=unnamed_connections,
        named_connections=named_connections
    )

    # Initialize the session object
    session = DebugSession(
        connections=connections,
        current_connection_name=starting_connection
    )

    # Show starting help information
    _print_console_intro(session)

    # Enter the main input loop
    _do_main_loop(session)


def _print_console_intro(session: DebugSession):
    """ Show the console startup greeting

    :param session: Current DebugSession
    """

    lines = (
        "",
        f"Starting debug session on connection '{session.current_connection_name}'.",
        "You may issue database commands by simply typing them and pressing enter.",
        "",
        f"Use {SHELL_COMMAND_INDICATOR}help for a list of special commands.",
        f"Use {SHELL_COMMAND_INDICATOR}exit to quit the debugger and resume the application."
        "\n"
    )

    print("\n".join(lines))


def _do_main_loop(session: DebugSession):
    """ Wait for user input, respond, repeat until StopSession is raised

    :param session: Current DebugSession
    """

    # Run forever until StopSession is raised or process is killed
    while True:

        prompt = f"{session.current_connection_name}> "

        # Gather user input
        command_string = input(prompt).strip()

        # Ignore lines with just whitespace
        if not command_string:
            continue

        # Run the command
        # Abort if StopSession raised (for example, on exit)
        try:
            outputs = execute_command(
                command_string=command_string,
                session=session
            )
        except StopSession:
            break
        except Exception as ex:
            outputs = [ex]

        # Display any outputted data
        _display_outputs(outputs)


def _display_outputs(outputs: [None, Iterable]):
    """ Print each of an iterable of outputs to the console

    :param outputs: Iterable of outputs to display
    """

    if not outputs:
        return

    for output in outputs:
        _display_output(output)

    print("")


def _display_output(output: object):
    """ Display a specific output object

    :param output: Output object to display
    """

    # A blank line will precede each displayed output
    print("")

    if isinstance(output, TableOutput):
        _display_table(output)
    elif isinstance(output, Exception):
        _display_exception(output)
    else:
        print(output)


def _display_table(output: TableOutput):
    """ Display a TableOutput object

    :param output: TableOutput object to display
    """

    formatted_table = tabulate.tabulate(
        output.rows,
        headers=output.columns,
        tablefmt="rst"
    )

    row_count = len(output.rows)

    print(formatted_table)
    print(f"({row_count} row(s) returned)")


def _display_exception(output: Exception):
    """ Display an exception

    :param output: Exception to display details for
    """

    exception_name = type(output).__name__

    print(f"Error: {exception_name}\n{output}", file=sys.stderr)
