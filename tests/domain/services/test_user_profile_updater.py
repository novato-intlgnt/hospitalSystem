"""Tests for UserProfileUpdaterService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.user import User
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.user_profile_updater import UserProfileUpdaterService


@pytest.mark.asyncio
async def test_update_profile_name_success():
    """Profile name can be updated when user exists"""
    user_repo = AsyncMock()

    user_mock = MagicMock(spec=User)
    user_mock.id_ = MagicMock()
    user_mock.username = MagicMock()
    user_mock.email = MagicMock()
    user_mock.password_hash = MagicMock()
    user_mock.name = MagicMock()
    user_mock.role = MagicMock()
    user_mock.doctor_data = None
    user_repo.get_by_id.return_value = user_mock

    service = UserProfileUpdaterService(user_repository=user_repo)

    new_name = MagicMock()
    result = await service.update_profile(user_id=MagicMock(), new_name=new_name)

    assert isinstance(result, User)
    user_repo.save.assert_called_once()
    saved = user_repo.save.call_args[0][0]
    assert saved.name == new_name


@pytest.mark.asyncio
async def test_update_profile_email_success():
    """Profile email can be updated when user exists"""
    user_repo = AsyncMock()

    user_mock = MagicMock(spec=User)
    user_mock.id_ = MagicMock()
    user_mock.username = MagicMock()
    user_mock.email = MagicMock()
    user_mock.password_hash = MagicMock()
    user_mock.name = MagicMock()
    user_mock.role = MagicMock()
    user_mock.doctor_data = None
    user_repo.get_by_id.return_value = user_mock

    service = UserProfileUpdaterService(user_repository=user_repo)

    new_email = MagicMock()
    result = await service.update_profile(user_id=MagicMock(), new_email=new_email)

    assert isinstance(result, User)
    saved = user_repo.save.call_args[0][0]
    assert saved.email == new_email


@pytest.mark.asyncio
async def test_update_profile_user_not_found_raises():
    """DomainError is raised when user to update is not found"""
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = None

    service = UserProfileUpdaterService(user_repository=user_repo)

    with pytest.raises(DomainError, match="User not found"):
        await service.update_profile(user_id=MagicMock())

    user_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_update_profile_no_changes_keeps_existing():
    """Calling update with no kwargs preserves all existing values"""
    user_repo = AsyncMock()

    original_name = MagicMock()
    original_email = MagicMock()
    original_doctor = MagicMock()

    user_mock = MagicMock(spec=User)
    user_mock.id_ = MagicMock()
    user_mock.username = MagicMock()
    user_mock.email = original_email
    user_mock.password_hash = MagicMock()
    user_mock.name = original_name
    user_mock.role = MagicMock()
    user_mock.doctor_data = original_doctor
    user_repo.get_by_id.return_value = user_mock

    service = UserProfileUpdaterService(user_repository=user_repo)
    result = await service.update_profile(user_id=MagicMock())

    saved = user_repo.save.call_args[0][0]
    assert saved.name == original_name
    assert saved.email == original_email
    assert saved.doctor_data == original_doctor
