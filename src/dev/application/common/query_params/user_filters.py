from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class UserQueryParams:
    """
    Data Transfer Object holding immutable parameters for filtering User listings,
    specifically designed for the Administrator console views.
    """
    
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
