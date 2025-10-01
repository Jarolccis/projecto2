"""Division domain entity."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Division:
    """Entidad de dominio para División."""
    
    division_id: int
    division_code: str
    division_name: str
    
    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.division_code:
            raise ValueError("Division code cannot be empty")
        if not self.division_name:
            raise ValueError("Division name cannot be empty")
    
    def __str__(self) -> str:
        return f"Division(id={self.division_id}, code='{self.division_code}', name='{self.division_name}')"
    
    def __repr__(self) -> str:
        return self.__str__()
