""" All exceptions used by this library """


class StopSession(Exception):
    """ Raised to request an exit the main console loop """
    pass


class UnknownCommandError(Exception):
    """ Raised when attempting to use an unknown shell command """
    pass


class WrongNumberOfArgumentsError(Exception):
    """ Raised when passing too many or two few shell command arguments """
    pass


class ConnectionNotFoundError(Exception):
    """ Raised when a connection cannot be found by its name """
    pass


class ConnectionAlreadyExistsError(Exception):
    """ Raised when trying to assign two connections to the same name """
    pass
