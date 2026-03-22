from src.dev.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)


class AnyOf[PC: PermissionContext](Permission[PC]):
    """
    Composite Authorization Strategy (Logical OR).
    Evalutes successfully if at least ONE of the provided nested permissions
    is satisfied by the given context.

    Particularly useful for complex rules (e.g., IsAdmin OR IsAuthorizedDoctor).
    """

    def __init__(self, *permissions: Permission[PC]) -> None:
        """
        Initializes the logical OR composite permission.

        Args:
            *permissions: A variable-length tuple encompassing all Permission rules
                to be conditionally chained.
        """
        self._permissions = permissions

    def is_satisfied_by(self, context: PC) -> bool:
        """
        Executes a short-circuited evaluation of the encapsulated rules.

        Args:
            context (PC): The context applied uniformly to all child permissions.

        Returns:
            bool: True upon the first successful satisfaction, False if all fail.
        """
        return any(p.is_satisfied_by(context) for p in self._permissions)


class AllOf[PC: PermissionContext](Permission[PC]):
    """
    Composite Authorization Strategy (Logical AND).
    Evalutes successfully only if ALL of the provided nested permissions
    are completely satisfied.
    """

    def __init__(self, *permissions: Permission[PC]) -> None:
        self._permissions = permissions

    def is_satisfied_by(self, context: PC) -> bool:
        return all(p.is_satisfied_by(context) for p in self._permissions)
