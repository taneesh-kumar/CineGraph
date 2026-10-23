"""Custom exception hierarchy for CineGraph backend."""


class CineGraphException(Exception):
    """Base exception for CineGraph application errors."""

    def __init__(self, message: str = "An internal server error occurred."):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundException(CineGraphException):
    """Raised when a requested entity (movie, user, genre) does not exist."""

    def __init__(self, entity_name: str, entity_id: any):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with identifier '{entity_id}' was not found.")


class DatabaseConnectionException(CineGraphException):
    """Raised when connection to Neo4j or MonetDB fails."""

    def __init__(self, database: str, details: str = ""):
        self.database = database
        self.details = details
        msg = f"Failed to connect to {database}."
        if details:
            msg += f" {details}"
        super().__init__(msg)


class DatabaseQueryException(CineGraphException):
    """Raised when a database query execution fails."""

    def __init__(self, database: str, message: str = ""):
        self.database = database
        super().__init__(f"Query execution failed on {database}: {message}" if message else f"Query execution failed on {database}.")


class InvalidInputException(CineGraphException):
    """Raised when client input or parameter validation fails."""

    def __init__(self, message: str):
        super().__init__(message)
