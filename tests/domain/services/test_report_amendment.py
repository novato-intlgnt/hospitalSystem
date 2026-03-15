"""Tests for ReportAmendmentService"""

from unittest.mock import MagicMock

from src.dev.domain.services.report.report_amendment import ReportAmendmentService


def test_amend_report_success():
    """Test amend_report orchestrates the entity's create_amendment correctly"""
    service = ReportAmendmentService()

    # Mock the original report
    original_report_mock = MagicMock()

    # Mock the returned new report
    new_report_mock = MagicMock()
    original_report_mock.create_amendment.return_value = new_report_mock

    # Execute the service
    new_id = "new_id"
    new_content = MagicMock()
    result = service.amend_report(original_report_mock, new_id, new_content)

    # Verify the aggregate's internal logic was called
    original_report_mock.create_amendment.assert_called_once_with(
        new_id=new_id, new_content=new_content
    )

    assert result == new_report_mock
