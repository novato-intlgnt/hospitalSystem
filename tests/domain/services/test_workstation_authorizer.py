"""Tests for WorkstationAuthorizerService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.workstation_authorizer import WorkstationAuthorizerService


def _make_ws_mock(*, is_authorized: bool) -> MagicMock:
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
async def test_authorize_success():
    """A deauthorized workstation can be successfully authorized"""
    ws_repo = AsyncMock()
    ws_mock = _make_ws_mock(is_authorized=False)
    ws_repo.get_by_id.return_value = ws_mock

    service = WorkstationAuthorizerService(workstation_repository=ws_repo)
    result = await service.authorize(workstation_id=MagicMock())

    assert isinstance(result, Workstation)
    assert result.is_authorized is True
    ws_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_authorize_already_authorized_raises():
    """DomainError is raised when trying to authorize an already authorized workstation"""
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = _make_ws_mock(is_authorized=True)

    service = WorkstationAuthorizerService(workstation_repository=ws_repo)

    with pytest.raises(DomainError, match="already authorized"):
        await service.authorize(workstation_id=MagicMock())

    ws_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_authorize_not_found_raises():
    """DomainError is raised when workstation to authorize is not found"""
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = None

    service = WorkstationAuthorizerService(workstation_repository=ws_repo)

    with pytest.raises(DomainError, match="Workstation not found"):
        await service.authorize(workstation_id=MagicMock())


@pytest.mark.asyncio
async def test_deauthorize_success():
    """An authorized workstation can be successfully deauthorized"""
    ws_repo = AsyncMock()
    ws_mock = _make_ws_mock(is_authorized=True)
    ws_repo.get_by_id.return_value = ws_mock

    service = WorkstationAuthorizerService(workstation_repository=ws_repo)
    result = await service.deauthorize(workstation_id=MagicMock())

    assert isinstance(result, Workstation)
    assert result.is_authorized is False
    ws_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_deauthorize_already_deauthorized_raises():
    """DomainError is raised when trying to deauthorize an already deauthorized workstation"""
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = _make_ws_mock(is_authorized=False)

    service = WorkstationAuthorizerService(workstation_repository=ws_repo)

    with pytest.raises(DomainError, match="already deauthorized"):
        await service.deauthorize(workstation_id=MagicMock())

    ws_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_deauthorize_not_found_raises():
    """DomainError is raised when workstation to deauthorize is not found"""
    ws_repo = AsyncMock()
    ws_repo.get_by_id.return_value = None

    service = WorkstationAuthorizerService(workstation_repository=ws_repo)

    with pytest.raises(DomainError, match="Workstation not found"):
        await service.deauthorize(workstation_id=MagicMock())
