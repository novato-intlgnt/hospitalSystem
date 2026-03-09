"""Tests for ReportSignerService"""

from unittest.mock import MagicMock, patch

import pytest

from src.dev.domain.exceptions.report import UnauthorizedSignerError
from src.dev.domain.services.report_signer import ReportSignerService


def test_report_signer_success():
    """Test successful report signing"""
    # Mocking dependencies
    mock_signature_service = MagicMock()
    mock_signature_service.generate_hash.return_value = "fake_hash_123"

    # Mock entities
    mock_report = MagicMock()
    mock_report.content = "Diagnosis: Healthy"

    mock_doctor = MagicMock()
    mock_doctor.id_ = "doc_1"
    mock_doctor.role = "DOCTOR"
    mock_doctor.legal_signature = "CMP.123"

    mock_workstation = MagicMock()

    service = ReportSignerService(signature_service=mock_signature_service)

    # Patch the access policy inside the service to return True
    with patch.object(
        service._access_policy, "is_satisfied_by", return_value=True
    ) as mock_policy:
        service.sign(mock_report, mock_doctor, mock_workstation)

        # Verify policy was checked
        mock_policy.assert_called_once_with(mock_doctor, mock_workstation)

        # Verify hash generation was called correctly
        mock_signature_service.generate_hash.assert_called_once_with(
            content="Diagnosis: Healthy", medical_license="CMP.123"
        )

        # Verify report was signed
        mock_report.sign.assert_called_once_with("fake_hash_123")


def test_report_signer_unauthorized():
    """Test report signing fails when access policy is not satisfied"""
    mock_signature_service = MagicMock()

    mock_report = MagicMock()
    mock_doctor = MagicMock()
    mock_doctor.id_ = "doc_1"
    mock_doctor.role = "NURSE"  # To test logging inside exception
    mock_workstation = MagicMock()

    service = ReportSignerService(signature_service=mock_signature_service)

    # Patch the access policy inside the service to return False
    with patch.object(service._access_policy, "is_satisfied_by", return_value=False):
        with pytest.raises(UnauthorizedSignerError) as exc_info:
            service.sign(mock_report, mock_doctor, mock_workstation)

        assert "User 'doc_1' with role NURSE is not authorized to sign reports." in str(
            exc_info.value
        )

        # Verify sign was NOT called on report
        mock_report.sign.assert_not_called()
