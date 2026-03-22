from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionContext:
    """
    DTO serving as the foundational payload
    for permission satisfaction checks. Inheriting classes should hold
    the immutable state (subjects, targets, resources) necessary for validation.
    """

    pass


class Permission[PC: PermissionContext](ABC):
    """
    Strategy abstract base class representing a generic Authorization Rule.
    It encapsulates the logic indicating whether the current Context (PC)
    complies with an expected privilege or security state.
    """

    @abstractmethod
    def is_satisfied_by(self, context: PC) -> bool:
        """
        Evaluates the specific business security rule against the provided context.

        Args:
            context (PC): A frozen dataclass inheriting from PermissionContext,
                holding actors and targets relative to the invocation.

        Returns:
            bool: True if the specific rule is met, False otherwise.
        """
        ...
