from src.dev.application.common.exceptions.base import ApplicationError


class MissingDoctorCredentialsError(ApplicationError):
    """
    Raised when a user with the DOCTOR role attempts to digitally sign
    a medical report but their profile lacks mandatory credentials such
    as the Medical College ID (CMP) or National Registry of Specialists (RNE).
    """

    def __init__(
        self, message: str = "Doctor profile is missing valid CMP/RNE credentials."
    ) -> None:
        super().__init__(message=message)
