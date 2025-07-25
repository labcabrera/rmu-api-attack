"""
Domain exceptions for the RMU Attack system.
"""


class AttackDomainException(Exception):
    """Base exception for attack domain errors"""

    pass


class AttackNotFoundException(AttackDomainException):
    """Exception raised when an attack is not found"""

    def __init__(self, attack_id: str):
        self.attack_id = attack_id
        super().__init__(f"Attack with ID '{attack_id}' not found")


class AttackInvalidStateException(AttackDomainException):
    """Exception raised when an attack has an invalid state for the requested operation"""

    def __init__(
        self, attack_id: str, current_state: str, expected_state: str, operation: str
    ):
        self.attack_id = attack_id
        self.current_state = current_state
        self.expected_state = expected_state
        self.operation = operation
        super().__init__(
            f"Attack '{attack_id}' has invalid state '{current_state}' for operation '{operation}'. "
            f"Expected state: '{expected_state}'"
        )


class AttackInvalidStateTransitionException(AttackDomainException):
    """Exception raised when an attack state transition is not allowed"""

    def __init__(self, attack_id: str, from_state: str, to_state: str):
        self.attack_id = attack_id
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Attack '{attack_id}' cannot transition from state '{from_state}' to '{to_state}'"
        )


class AttackAlreadyExecutedException(AttackDomainException):
    """Exception raised when trying to execute an attack that is already executed"""

    def __init__(self, attack_id: str):
        self.attack_id = attack_id
        super().__init__(f"Attack '{attack_id}' is already executed")


class AttackNotExecutedException(AttackDomainException):
    """Exception raised when trying to perform an operation that requires an executed attack"""

    def __init__(self, attack_id: str, operation: str):
        self.attack_id = attack_id
        self.operation = operation
        super().__init__(
            f"Attack '{attack_id}' must be executed before performing operation '{operation}'"
        )


class AttackValidationException(AttackDomainException):
    """Exception raised when attack data validation fails"""

    def __init__(self, message: str, field: str = None):
        self.field = field
        if field:
            super().__init__(f"Validation error in field '{field}': {message}")
        else:
            super().__init__(f"Validation error: {message}")


class AttackRepositoryException(AttackDomainException):
    """Exception raised for repository-related errors"""

    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        if operation:
            super().__init__(f"Repository error during '{operation}': {message}")
        else:
            super().__init__(f"Repository error: {message}")
