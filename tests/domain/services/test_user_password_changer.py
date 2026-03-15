"""Tests for UserPasswordChangerService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.user import User
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.user.user_password_changer import (
    UserPasswordChangerService,
)


@pytest.mark.asyncio
async def test_change_password_success():
    """Password changes successfully when user exists and current password matches"""
    user_repo = AsyncMock()
    hasher = AsyncMock()

    user_mock = MagicMock(spec=User)
    user_mock.password_hash = MagicMock()
    user_mock.username = MagicMock()
    user_mock.email = MagicMock()
    user_mock.name = MagicMock()
    user_mock.role = MagicMock()
    user_mock.doctor_data = None
    user_mock.id_ = MagicMock()

    user_repo.get_by_id.return_value = user_mock
    hasher.verify.return_value = True
    hasher.hash.return_value = MagicMock()

    service = UserPasswordChangerService(
        user_repository=user_repo,
        password_hasher=hasher,
    )

    current_pw = MagicMock()
    new_pw = MagicMock()
    user_id = MagicMock()

    result = await service.change_password(
        user_id=user_id,
        current_password=current_pw,
        new_password=new_pw,
    )

    assert isinstance(result, User)
    user_repo.get_by_id.assert_called_once_with(user_id)
    hasher.verify.assert_called_once_with(current_pw, user_mock.password_hash)
    hasher.hash.assert_called_once_with(new_pw)
    user_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_change_password_user_not_found_raises():
    """DomainError is raised when user is not found"""
    user_repo = AsyncMock()
    user_repo.get_by_id.return_value = None

    service = UserPasswordChangerService(
        user_repository=user_repo,
        password_hasher=AsyncMock(),
    )

    with pytest.raises(DomainError, match="User not found"):
        await service.change_password(
            user_id=MagicMock(),
            current_password=MagicMock(),
            new_password=MagicMock(),
        )


@pytest.mark.asyncio
async def test_change_password_wrong_current_password_raises():
    """DomainError is raised when the current password does not match"""
    user_repo = AsyncMock()
    hasher = AsyncMock()

    user_mock = MagicMock(spec=User)
    user_mock.password_hash = MagicMock()
    user_repo.get_by_id.return_value = user_mock
    hasher.verify.return_value = False

    service = UserPasswordChangerService(
        user_repository=user_repo,
        password_hasher=hasher,
    )

    with pytest.raises(DomainError, match="Current password is incorrect"):
        await service.change_password(
            user_id=MagicMock(),
            current_password=MagicMock(),
            new_password=MagicMock(),
        )

    hasher.hash.assert_not_called()
    user_repo.save.assert_not_called()
