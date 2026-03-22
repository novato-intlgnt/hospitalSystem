"""User Gateway — Application Layer Port

Contract for mutable operations on the User aggregate, supporting the full
administrative lifecycle: creation, query, and deletion of user accounts.
"""

from typing import Optional, Protocol

from src.dev.domain.entities.user import User


class UserCommandGateway(Protocol):
    """Port for mutable (write) operations on the User entity.

    Consumed by the application layer to persist new users, hydrate existing
    aggregates for update, and hard-delete accounts when required (RN-14, RN-17).
    """

    def add(self, user: User) -> None:
        """Register a new User aggregate in the persistence store.

        The User entity must have its ``id_`` and all mandatory fields
        set before calling this method.  The unit of work (``Flusher``) will
        detect any uniqueness constraint violations (e.g. duplicate username)
        during :py:meth:`Flusher.flush`.

        :raises DataMapperError: On fatal persistence errors.
        """
        ...

    def delete(self, user: User) -> None:
        """Mark the User aggregate for hard deletion within the active transaction.

        The physical removal is committed when ``TransactionManager.commit`` is
        called.  Prefer ``DeactivateUserInteractor`` for logical deactivation
        (preserves audit trail). Only use hard deletion for exceptional cases.

        :raises DataMapperError: On fatal persistence errors.
        """
        ...

    async def read_by_id(
        self, user_id: str, *, for_update: bool = False
    ) -> Optional[User]:
        """Retrieve a User entity by its unique identifier.

        Args:
            user_id: The string representation of the user's ``EntityID``.
            for_update: If ``True``, acquires a row-level lock (``SELECT FOR UPDATE``)
                to prevent concurrent modifications during the active transaction.

        Returns:
            The hydrated ``User`` entity if found, otherwise ``None``.

        :raises DataMapperError: On fatal read failures.
        """
        ...
