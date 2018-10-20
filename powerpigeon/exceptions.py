class PowerPigeonError(BaseException):
    """The base exception for Remodel."""


class NoMetaFound(PowerPigeonError):
    """This exception is thrown when the "Meta" class cannot be found."""


class InvalidAttributeType(PowerPigeonError):
    """This is raised when a attribute does not inherit BaseAttribute."""


class NoIDAttribute(PowerPigeonError):
    """
    This is raised when you try and run something that needs a ID attribute and
    you do not have one.
    """


class NoConnectionFound(PowerPigeonError):
    """This is raised when there is no connection in the "Meta" class."""


class TableDoesNotExist(PowerPigeonError):
    """This is raised when a table does not exist."""


class TableOrDBDoesNotExist(PowerPigeonError):
    """This is raised when a table or database does not exist."""


class DoesNotExist(PowerPigeonError):
    """This is raised when a item does not exist."""


class NotAllRequired(PowerPigeonError):
    """This is raised when not all of the required items have been sorted."""


class TableCreationError(PowerPigeonError):
    """This is raised when a table cannot be created."""


class SaveFailed(PowerPigeonError):
    """This is raised when a item cannot be saved."""


class ConversionError(PowerPigeonError):
    """This is raised when a item cannot be encoded/decoded."""


class IndexParametersInvalid(PowerPigeonError):
    """This is raised when the index parameters are invalid."""
