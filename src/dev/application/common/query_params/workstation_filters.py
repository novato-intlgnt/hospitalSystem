from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, kw_only=True)
class WorkstationQueryParams:
    """
    Data Transfer Object holding immutable parameters for filtering Workstations.
    Used by the Administrator panel to locate machines by status, IP, or type.
    """
    
    workstation_type: Optional[str] = None  # e.g., 'ADQUISICION' or 'VISUALIZACION'
    status: Optional[str] = None            # e.g., 'PENDING', 'AUTHORIZED', 'DISABLED'
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
