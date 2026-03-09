"""Tests for AuditLoggerService"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.audit_log import AuditLog
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.audit_logger import AuditLoggerService
from src.dev.domain.value_objects.log import LogEntry


@pytest.mark.asyncio
async def test_log_action_success_with_user():
    """Test logging an action successfully with an existing user and workstation"""
    # Mocks
    audit_repo = AsyncMock()
    workstation_repo = AsyncMock()
    user_repo = AsyncMock()

    workstation_mock = MagicMock()
    workstation_mock.hardware_id = "HW-123"
    workstation_repo.get_by_network.return_value = workstation_mock

    user_repo.exists_by_id.return_value = True

    service = AuditLoggerService(
        audit_repository=audit_repo,
        workstation_repository=workstation_repo,
        user_repository=user_repo,
    )

    id_mock = MagicMock()
    resource_id = MagicMock()
    network_info = MagicMock()
    user_id = MagicMock()

    await service.log_action(
        id_=id_mock,
        action="CREATE_REPORT",
        resource_id=resource_id,
        network_info=network_info,
        user_id=user_id,
    )

    # Assertions
    workstation_repo.get_by_network.assert_called_once_with(network_info)
    user_repo.exists_by_id.assert_called_once_with(user_id)

    # Verify save was called with an AuditLog containing the exact data
    audit_repo.save.assert_called_once()
    saved_log = audit_repo.save.call_args[0][0]

    assert isinstance(saved_log, AuditLog)
    assert saved_log.action == "CREATE_REPORT"
    assert saved_log.user_id == user_id


@pytest.mark.asyncio
async def test_log_action_unregistered_workstation():
    """Test logging fails if workstation network is unregistered"""
    audit_repo = AsyncMock()
    workstation_repo = AsyncMock()
    user_repo = AsyncMock()

    workstation_repo.get_by_network.return_value = None

    service = AuditLoggerService(
        audit_repository=audit_repo,
        workstation_repository=workstation_repo,
        user_repository=user_repo,
    )

    with pytest.raises(DomainError, match="Workstation is not registered"):
        await service.log_action(
            id_=MagicMock(),
            action="CREATE_REPORT",
            resource_id=MagicMock(),
            network_info=MagicMock(),
        )

    audit_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_log_action_non_existent_user():
    """Test logging fails if provided user_id does not exist"""
    audit_repo = AsyncMock()
    workstation_repo = AsyncMock()
    user_repo = AsyncMock()

    workstation_mock = MagicMock()
    workstation_repo.get_by_network.return_value = workstation_mock

    user_repo.exists_by_id.return_value = False

    service = AuditLoggerService(
        audit_repository=audit_repo,
        workstation_repository=workstation_repo,
        user_repository=user_repo,
    )

    with pytest.raises(DomainError, match="User does not exist"):
        await service.log_action(
            id_=MagicMock(),
            action="CREATE_REPORT",
            resource_id=MagicMock(),
            network_info=MagicMock(),
            user_id=MagicMock(),
        )

    audit_repo.save.assert_not_called()
