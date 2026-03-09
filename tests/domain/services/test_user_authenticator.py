"""Tests for UserAuthenticatorService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.user import User
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.user_authenticator import UserAuthenticatorService


@pytest.mark.asyncio
async def test_authenticate_success():
    """Authentication succeeds with correct username and password"""
    user_repo = AsyncMock()
    hasher = AsyncMock()

    user_mock = MagicMock(spec=User)
    user_mock.password_hash = MagicMock()
    user_repo.get_by_username.return_value = user_mock
    hasher.verify.return_value = True

    service = UserAuthenticatorService(
        user_repository=user_repo,
        password_hasher=hasher,
    )

    username = MagicMock()
    raw_password = MagicMock()
    result = await service.authenticate(username=username, raw_password=raw_password)

    assert result is user_mock
    user_repo.get_by_username.assert_called_once_with(username)
    hasher.verify.assert_called_once_with(raw_password, user_mock.password_hash)


@pytest.mark.asyncio
async def test_authenticate_user_not_found_raises():
    """Authentication fails with a generic message when username does not exist"""
    user_repo = AsyncMock()
    user_repo.get_by_username.return_value = None
    hasher = AsyncMock()

    service = UserAuthenticatorService(
        user_repository=user_repo,
        password_hasher=hasher,
    )

    with pytest.raises(DomainError, match="Invalid username or password"):
        await service.authenticate(username=MagicMock(), raw_password=MagicMock())

    hasher.verify.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_wrong_password_raises():
    """Authentication fails with a generic message when password is wrong"""
    user_repo = AsyncMock()
    hasher = AsyncMock()

    user_mock = MagicMock(spec=User)
    user_mock.password_hash = MagicMock()
    user_repo.get_by_username.return_value = user_mock
    hasher.verify.return_value = False

    service = UserAuthenticatorService(
        user_repository=user_repo,
        password_hasher=hasher,
    )

    with pytest.raises(DomainError, match="Invalid username or password"):
        await service.authenticate(username=MagicMock(), raw_password=MagicMock())
