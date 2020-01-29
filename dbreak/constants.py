""" Holds important constants used across modules """

# Naming pattern to use for connections that are
# not explicitly named by the user
DEFAULT_CONNECTION_NAME_PATTERN = "db[{number}]"

# Character that indicates a command is a shell
# command that should NOT be sent to the database
# directly
SHELL_COMMAND_INDICATOR = "!"
