"""Domain service for system auditing."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from src.dev.domain.entities.audit_log import AuditLog
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.exceptions.user import UserNotFoundByIdError
from src.dev.domain.ports.repositories.persistence import (
    AuditRepository,
    UserRepository,
    WorkstationRepository,
)
from src.dev.domain.value_objects.log import LogEntry
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import NetworkAddress


class AuditLoggerService:
    """Service to centralize the creation of AuditLogs enforcing RN-12."""

    def __init__(
        self,
        audit_repository: AuditRepository,
        workstation_repository: WorkstationRepository,
        user_repository: UserRepository,
    ) -> None:
        self._audit_repository = audit_repository
        self._workstation_repository = workstation_repository
        self._user_repository = user_repository

    async def log_action(
        self,
        id_: EntityID,
        action: str,
        resource_id: EntityID,
        network_info: NetworkAddress,
        user_id: Optional[EntityID] = None,
    ) -> None:
        """
        Logs an action performed in the system (RN-12).

        Rules enforced:
        - The workstation must be registered in the system (derived from network_info).
        - If a user_id is provided, the user must exist.
        """
        # Validate Workstation and get its HardwareID
        workstation = await self._workstation_repository.get_by_network(network_info)
        if workstation is None:
            raise DomainError(
                "Cannot log action: Workstation is not registered "
                "or recognized by its network address."
            )

        hardware_id = workstation.hardware_id

        # Validate User if provided
        if user_id is not None:
            user_exists = await self._user_repository.exists_by_id(user_id)
            if not user_exists:
                raise DomainError("Cannot log action: User does not exist.")

        # Create LogEntry value object
        log_entry = LogEntry(
            hardware_id=hardware_id,
            action=action,
            resource_id=resource_id,
            network_info=network_info,
            user_id=user_id,
        )

        # Create the AuditLog entity
        audit_log = AuditLog(
            id_=id_,
            log_data=log_entry,
            timestamp=datetime.now(),
        )

        # Save to repository
        await self._audit_repository.save(audit_log)
