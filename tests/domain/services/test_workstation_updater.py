"""Tests for WorkstationUpdaterService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.workstation_updater import WorkstationUpdaterService


def _make_ws_mock(*, is_authorized: bool = True) -> MagicMock:
    ws = MagicMock(spec=Workstation)
    ws.id_ = MagicMock()
    ws.hardware_id = MagicMock()
    ws.network = MagicMock()
    ws.specs = MagicMock()
    ws.location = MagicMock()
    ws.type = MagicMock()
    ws.is_authorized = is_authorized
    return ws


@pytest.mark.asyncio
async def test_update_workstation_specs_success():
    """Workstation specs can be updated without changing the network address"""
    ws_repo = AsyncMock()
    ws_mock = _make_ws_mock()
    ws_repo.get_by_id.return_value = ws_mock

    service = WorkstationUpdaterService(workstation_repository=ws_repo)
    new_specs = MagicMock()

    result = await service.update(workstation_id=MagicMock(), new_specs=new_specs)

    assert isinstance(result, Workstation)
    ws_repo.esists_by_network_address.assert_not_called()
    ws_repo.save.assert_called_once()
    saved = ws_repo.save.call_args[0][0]
    assert saved.specs == new_specs


@pytest.mark.asyncio
async def test_update_workstation_network_success():
    """RN-09: Network address can be updated when the new address is unique"""
    ws_repo = AsyncMock()
    ws_mock = _make_ws_mock()
    ws_repo.get_by_id.return_value = ws_mock
    ws_repo.esists_by_network_address.return_value = False

    service = WorkstationUpdaterService(workstation_repository=ws_repo)
    new_network = MagicMock()
    # Ensure new_network != ws_mock.network so uniqueness check is triggered
    new_network.__eq__ = lambda self, other: False

    result = await service.update(workstation_id=MagicMock(), new_network=new_network)

    assert isinstance(result, Workstation)
    ws_repo.esists_by_network_address.assert_called_once_with(new_network)
    ws_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_update_workstation_duplicate_network_raises():
    """RN-09: DomainError is raised when new network address is already in use"""
    ws_repo = AsyncMock()
    ws_mock = _make_ws_mock()
    ws_repo.get_by_id.return_value = ws_mock
    ws_repo.esists_by_network_address.return_value = True

    service = WorkstationUpdaterService(workstation_repository=ws_repo)

    new_network = MagicMock()
    new_network.__eq__ = lambda self, other: False
    new_network.ip_address = "10.0.0.5"
    new_network.mac_address = "FF:EE:DD:CC:BB:AA"

    with pytest.raises(DomainError, match="10.0.0.5"):
        await service.update(workstation_id=MagicMock(), new_network=new_network)

    ws_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_update_workstation_not_found_raises():
    """DomainError is raised when workstation to update is not found"""
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = None

    service = WorkstationUpdaterService(workstation_repository=ws_repo)

    with pytest.raises(DomainError, match="Workstation not found"):
        await service.update(workstation_id=MagicMock())

    ws_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_update_workstation_same_network_skips_uniqueness_check():
    """No uniqueness check is done when the network address is unchanged"""
    ws_repo = AsyncMock()
    ws_mock = _make_ws_mock()
    ws_repo.get_by_id.return_value = ws_mock

    service = WorkstationUpdaterService(workstation_repository=ws_repo)

    # Pass the same network object — equality is True, so no check
    result = await service.update(
        workstation_id=MagicMock(),
        new_network=ws_mock.network,
    )

    ws_repo.esists_by_network_address.assert_not_called()
    ws_repo.save.assert_called_once()
