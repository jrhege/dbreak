""" Functions for parsing database and shell commands """

import shlex

from typing import Tuple, Callable, List, Dict, Generator

from .constants import SHELL_COMMAND_INDICATOR
from .exc import WrongNumberOfArgumentsError, UnknownCommandError


def parse(command_string: str, shell_command_lookup: Dict[str, dict]) -> Tuple[Callable, List]:
    """ Parse a string of commands and arguments into a (command function, arguments) tuple

    :param command_string: String of command + arguments
    :param shell_command_lookup: Dict of shell commands to compare against command_string
    """

    # It's assumed any string not starting with SHELL_COMMAND_INDICATOR
    # is a command that should be sent directly to the db
    if command_string.startswith(SHELL_COMMAND_INDICATOR):

        return _parse_shell_command(
            command_string=command_string,
            shell_command_lookup=shell_command_lookup
        )

    else:

        return _parse_db_command(
            command_string=command_string,
            shell_command_lookup=shell_command_lookup
        )


def unquote(s: str) -> str:
    """ Remove starting and ending quotes, only if quoted on both sides

    :param s: String to strip leading/trailing quotes from
    """

    # Don't strip if the string is too short
    if len(s) < 2:
        return s

    # Get first and last character
    start_char, end_char = s[0], s[-1]

    # Only strip quotes if it starts and ends with the same quote type
    if start_char == end_char and start_char in {'"', "'"}:
        return s.strip(start_char)
    else:
        return s


def tokenize(s: str, maximum_tokens: [int, None] = None) -> Generator[str, None, None]:
    """ Split a string containing whitespace-separated strings into tokens

    Uses shlex for tokenization. If the number of tokens returned by shlex
    would exceed maximum_tokens, the rest of the string is returned
    as the last token.

    :param s: String to parse
    :param maximum_tokens: Maximum number of parsed arguments to return
    """

    if isinstance(maximum_tokens, int) and maximum_tokens < 1:
        raise ValueError("Maximum tokens must be None or greater than 0")

    # This is tracked so we can return the rest of the string
    # when we reach maximum_tokens, rather than wasting time
    # tokenizing and recombining to form the final token
    string_position = 0

    token_number = 0

    # Use shlex for parsing, splitting on whitespace only
    lex = shlex.shlex(s)
    lex.whitespace_split = True

    for token in lex:

        token_number += 1

        # Return the rest of the string when we've
        # reached the final token
        if token_number == maximum_tokens:
            rest_of_string = s[string_position:]

            yield unquote(rest_of_string)
            break

        string_position += len(token) + 1

        yield unquote(token)


def _parse_shell_command(command_string: str, shell_command_lookup: Dict[str, dict]) -> Tuple[Callable, List]:
    """ Parse a shell (non-db) command into a (command function, arguments) tuple

    :param command_string: String of command + arguments
    :param shell_command_lookup: Dict of shell commands to compare against command_string
    """

    # Break the command_string into a command string and arguments string
    command, argument_string = _split_command_string(command_string)

    # Get information about the command that was parsed out
    command_details = _find_command_details(
        command=command,
        shell_command_lookup=shell_command_lookup
    )

    # Determine how many arguments we should expect
    number_of_arguments = len(command_details["arguments"])

    # Convert argument_string into a list of arguments
    arguments = _parse_arguments(
        argument_string=argument_string,
        number_of_arguments=number_of_arguments,
        verbose_final_argument=command_details["verbose_final_argument"]
    )

    # Raise an error if too many or too few arguments are provided
    # (Optional arguments currently aren't a thing)
    if len(arguments) != number_of_arguments:
        message = f"Command '{command}' expects {number_of_arguments} arguments, got {len(arguments)}"
        raise WrongNumberOfArgumentsError(message)

    return command_details["func"], arguments


def _split_command_string(command_string: str) -> Tuple[str, str]:
    """ Split a string into a (command, argument string) tuple

    :param command_string: String of command + arguments
    """

    # Remove the command character prefix
    command_string_sans_prefix = command_string[len(SHELL_COMMAND_INDICATOR):]

    try:
        first_space = command_string_sans_prefix.index(" ")
    except ValueError:
        return command_string_sans_prefix, ""

    # Get the command from the string
    command = command_string_sans_prefix[:first_space]

    # Get the arguments portion of the string
    arguments = command_string_sans_prefix[first_space + 1:]

    return command, arguments


def _find_command_details(command: str, shell_command_lookup: Dict[str, dict]):
    """ Retrieve details about a given command

    :param command: Command to search for
    :param shell_command_lookup: Dict of shell commands to search in
    """

    try:
        return shell_command_lookup[command]
    except KeyError:
        raise UnknownCommandError(f"Command '{command}' not recognized")


def _parse_arguments(argument_string: str, number_of_arguments: int, verbose_final_argument: bool) -> List[str]:
    """ Convert an argument_string into number_of_arguments arguments

    :param argument_string: String containing all arguments to be parsed
    :param number_of_arguments: How many arguments should be returned
    :param verbose_final_argument: If True, ignore whitespace for generating final argument
    """

    # Limit the number of arguments returned if we're doing a
    # verbose final argument (the final argument will contain
    # the rest of the string), else return as many as we can find
    maximum_arguments = number_of_arguments if verbose_final_argument else None

    # Get a generator that yield arguments
    parser = tokenize(
        s=argument_string,
        maximum_tokens=maximum_arguments
    )

    return list(parser)


def _parse_db_command(command_string: str, shell_command_lookup: Dict[str, dict]) -> Tuple[Callable, List]:
    """ Parse a database command into (command function, arguments) tuple

    :param command_string: String of command + arguments
    :param shell_command_lookup: Dict of shell commands for looking up execute function
    """

    func = shell_command_lookup["execute"]["func"]

    return func, [command_string]
