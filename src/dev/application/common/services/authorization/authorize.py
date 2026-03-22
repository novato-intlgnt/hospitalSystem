from src.dev.application.common.exceptions.unauthorized_access import (
    UnauthorizedAccessError,
)
from src.dev.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)
from src.dev.application.common.services.constants import AUTHZ_NOT_AUTHORIZED


def authorize[PC: PermissionContext](
    permission: Permission[PC],
    *,
    context: PC,
) -> None:
    """
    Evaluates a specific permission against the provided business context,
    enforcing a strict Authorization gateway (RN-14, RN-16, RN-17).

    Args:
        permission (Permission[PC]): An instance of a concrete Permission strategy.
        context (PC): The current request context holding actors and targets.

    Raises:
        UnauthorizedAccessError: If the provided rule `is_satisfied_by()` returns False,
            terminating the use case flow immediately.
    """
    if not permission.is_satisfied_by(context):
        # We can throw a broad error here or allow the context/permission to override it
        # But per standard, the Interactor can catch and remap or we use the global constant.
        raise UnauthorizedAccessError(AUTHZ_NOT_AUTHORIZED)
