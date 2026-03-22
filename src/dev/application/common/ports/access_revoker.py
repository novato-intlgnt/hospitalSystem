from typing import Protocol


class AccessRevoker(Protocol):
    """
    Interface for revoking user access across the system.

    This port is utilized when a security policy explicitly demands
    that a user's active sessions or tokens be immediately invalidated,
    such as when an account is logically deactivated.
    """

    async def remove_all_user_access(self, user_id: str) -> None:
        """
        Immediately invalidates all active sessions for the specified user.

        Args:
            user_id (str): The unique identifier of the user to act upon.
        """
        ...
