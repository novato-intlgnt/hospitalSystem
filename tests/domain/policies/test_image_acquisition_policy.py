"""Tests for ImageAcquisitionPolicy"""

from unittest.mock import MagicMock

from src.dev.domain.policies.image_acquisition_policy import ImageAcquisitionPolicy


def test_image_acquisition_policy_satisfied():
    """Test policy is satisfied when workstation can upload files"""
    policy = ImageAcquisitionPolicy()
    user_mock = MagicMock()
    workstation_mock = MagicMock()
    workstation_mock.can_upload_file = True

    assert policy.is_satisfied_by(user_mock, workstation_mock) is True


def test_image_acquisition_policy_not_satisfied():
    """Test policy fails when workstation cannot upload files"""
    policy = ImageAcquisitionPolicy()
    user_mock = MagicMock()
    workstation_mock = MagicMock()
    workstation_mock.can_upload_file = False

    assert policy.is_satisfied_by(user_mock, workstation_mock) is False
