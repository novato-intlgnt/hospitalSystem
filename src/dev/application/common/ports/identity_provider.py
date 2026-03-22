from typing import Protocol


class IdentityProvider(Protocol):
    """
    Interface for providing identity information in the current context.

    This port is used by application services to identify the active user
    from the current request scope (e.g., extracting from a JWT token).
    """

    async def get_current_user_id(self) -> str:
        """
        Retrieves the unique identifier of the currently authenticated user.

        Raises:
            UnauthorizedAccessError: If there is no active session or token.

        Returns:
            str: The unique user identifier.
        """
        ...
