"""Tests for WorkstationAccessPolicy"""

from unittest.mock import MagicMock

from src.dev.domain.policies.workstation_access_policy import WorkstationAccessPolicy


def test_workstation_access_policy_satisfied():
    """Test policy is satisfied when user is a doctor and workstation handles legal reports"""
    policy = WorkstationAccessPolicy()

    user_mock = MagicMock()
    user_mock.is_doctor = True

    workstation_mock = MagicMock()
    workstation_mock.can_handle_legal_reports = True

    assert policy.is_satisfied_by(user_mock, workstation_mock) is True


def test_workstation_access_policy_not_doctor():
    """Test policy fails when user is not a doctor"""
    policy = WorkstationAccessPolicy()

    user_mock = MagicMock()
    user_mock.is_doctor = False

    workstation_mock = MagicMock()
    workstation_mock.can_handle_legal_reports = True

    assert policy.is_satisfied_by(user_mock, workstation_mock) is False


def test_workstation_access_policy_invalid_workstation():
    """Test policy fails when workstation cannot handle legal reports"""
    policy = WorkstationAccessPolicy()

    user_mock = MagicMock()
    user_mock.is_doctor = True

    workstation_mock = MagicMock()
    workstation_mock.can_handle_legal_reports = False

    assert policy.is_satisfied_by(user_mock, workstation_mock) is False
