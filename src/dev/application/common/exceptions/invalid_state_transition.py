"""Invalid exam state transition exception for the application layer."""

from typing import Any

from src.dev.application.common.exceptions.base import ApplicationError


class InvalidExamStateTransitionError(ApplicationError):
    """Raised when an exam workflow transition is not permitted from its current state.

    This exception is raised at the use-case level when a command tries to
    move an exam to a lifecycle state that is not reachable from its current
    one (e.g. transitioning a DELIVERED exam back to IN_PROGRESS).

    It complements the domain-layer ``InvalidExamStateError`` by providing
    richer context about the attempted workflow step, making it suitable for
    presenting actionable feedback to the caller.

    Args:
        exam_id: The identifier of the exam whose state transition failed.
        from_state: The current ``ExamStatus`` value (as a string).
        to_state: The target ``ExamStatus`` value (as a string).
    """

    def __init__(self, exam_id: Any, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Exam {exam_id!r} cannot transition from {from_state!r} to {to_state!r}."
        )
        self.exam_id = exam_id
        self.from_state = from_state
        self.to_state = to_state
