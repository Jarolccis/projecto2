"""Division application schemas."""

from pydantic import BaseModel, Field


#region Response Schemas

class DivisionResponse(BaseModel):
    """Schema de respuesta para División."""
    
    division_id: int
    division_code: str
    division_name: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "division_id": 1,
                "division_code": "J01",
                "division_name": "PGC COMESTIBLE"
            }
        }

#endregion
