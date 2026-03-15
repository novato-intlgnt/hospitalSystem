"""Flusher port — Application Layer"""

from abc import abstractmethod
from typing import Protocol


class Flusher(Protocol):
    """
    Contract for flushing intermediate changes within an active transaction.

    The flush synchronizes the in-memory state with the database without committing
    the transaction, allowing constraint violations
    (e.g., duplicate patient health records)
    to be detected or side effects to be triggered before the final commit.

    """

    @abstractmethod
    async def flush(self) -> None:
        """
        :raises DataMapperError:
        :raises DuplicatePatientError: Si la HC ya existe (RN-01).

        Persist the pending changes in the ORM buffer to the database within
        the current transaction, without performing a commit.
        """
