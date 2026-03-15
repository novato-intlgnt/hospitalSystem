"""Base class for all application-layer exceptions."""


class ApplicationError(Exception):
    """Root exception for all application-layer errors.

    Raised when a use-case violates an application rule that is not
    tied to domain invariants (e.g. authorization, preconditions
    enforced at the orchestration level, or infrastructure contracts).

    Attributes:
        message: Human-readable description of the failure.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
