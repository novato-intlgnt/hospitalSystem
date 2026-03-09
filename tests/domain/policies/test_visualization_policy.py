"""Tests for VisualizationPolicy"""

from unittest.mock import MagicMock

from src.dev.domain.policies.visualization_policy import VisualizationPolicy


def test_visualization_policy_public_viewer_no_user():
    """Test policy allows access on a public viewer even without a logged in user"""
    policy = VisualizationPolicy()
    workstation_mock = MagicMock()
    workstation_mock.is_public_viewer = True

    assert policy.is_satisfied_by(None, workstation_mock) is True


def test_visualization_policy_public_viewer_with_user():
    """Test policy allows access on a public viewer with a logged in user"""
    policy = VisualizationPolicy()
    user_mock = MagicMock()
    workstation_mock = MagicMock()
    workstation_mock.is_public_viewer = True

    assert policy.is_satisfied_by(user_mock, workstation_mock) is True


def test_visualization_policy_not_public_with_user():
    """Test policy allows access on a non-public viewer if user is logged in"""
    policy = VisualizationPolicy()
    user_mock = MagicMock()
    workstation_mock = MagicMock()
    workstation_mock.is_public_viewer = False

    assert policy.is_satisfied_by(user_mock, workstation_mock) is True


def test_visualization_policy_not_public_no_user():
    """Test policy denis access on a non-public viewer if user is None"""
    policy = VisualizationPolicy()
    workstation_mock = MagicMock()
    workstation_mock.is_public_viewer = False

    assert policy.is_satisfied_by(None, workstation_mock) is False
