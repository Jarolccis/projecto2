"""SKU Pydantic schemas for validation."""

from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field, field_validator

from app.core.validators import validate_with_timing_protection


#region Request Schemas

class SkuCodesRequest(BaseModel):
    """Request schema for getting SKUs by codes."""
    
    sku_codes: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of SKU codes to search for",
        example=["41217739", "41217740"]
    )

    @field_validator("sku_codes")
    @classmethod
    def validate_sku_codes(cls, v):
        """Validate SKU codes format with enhanced security validation."""
        if not v:
            raise ValueError("SKU codes list cannot be empty")
        
        # Validate each SKU code format with security checks
        for sku_code in v:
            if not sku_code or not isinstance(sku_code, str):
                raise ValueError("All SKU codes must be non-empty strings")
            
            if not sku_code.strip():
                raise ValueError("SKU codes cannot be empty or whitespace only")
            
            # Enhanced validation with security checks
            try:
                validated_code = validate_with_timing_protection(
                    value=sku_code.strip(),
                    field_name="SKU code",
                    min_length=3,
                    max_length=8,
                    allowed_chars=r'^[a-zA-Z0-9]+$',
                    generic_names=['test', 'admin', 'root', 'user', 'demo', 'example', 'sample']
                )
                
                # Additional business validation
                if len(validated_code) < 3 or len(validated_code) > 8:
                    raise ValueError("SKU codes must be between 3 and 8 characters")
                
                if not validated_code.isalnum():
                    raise ValueError("SKU codes must contain only alphanumeric characters")
                
            except Exception as e:
                raise ValueError(f"Invalid SKU code '{sku_code}': {str(e)}")
        
        return [code.strip() for code in v]

#endregion


#region Response Schemas

class SkuResponse(BaseModel):
    """Response schema for individual SKU data."""
    
    sku: str
    descripcion_sku: str
    costo_reposicion: Decimal
    estado_id: int
    marca_id: int
    marca: str
    subclase_id: int
    codigo_subclase: str
    subclase: str
    clase_id: int
    codigo_clase: str
    clase: str
    subdepartamento_id: int
    codigo_subdepartamento: str
    subdepartamento: str
    departamento_id: int
    codigo_departamento: str
    departamento: str
    division_id: int
    codigo_division: str
    division: str
    proveedor_id: int
    ruc_proveedor: str
    proveedor: str

    @classmethod
    def from_domain_model(cls, sku) -> "SkuResponse":
        """Create SkuResponse from domain model."""
        return cls(
            sku=sku.sku,
            descripcion_sku=sku.descripcion_sku,
            costo_reposicion=sku.costo_reposicion,
            estado_id=sku.estado_id,
            marca_id=sku.marca_id,
            marca=sku.marca,
            subclase_id=sku.subclase_id,
            codigo_subclase=sku.codigo_subclase,
            subclase=sku.subclase,
            clase_id=sku.clase_id,
            codigo_clase=sku.codigo_clase,
            clase=sku.clase,
            subdepartamento_id=sku.subdepartamento_id,
            codigo_subdepartamento=sku.codigo_subdepartamento,
            subdepartamento=sku.subdepartamento,
            departamento_id=sku.departamento_id,
            codigo_departamento=sku.codigo_departamento,
            departamento=sku.departamento,
            division_id=sku.division_id,
            codigo_division=sku.codigo_division,
            division=sku.division,
            proveedor_id=sku.proveedor_id,
            ruc_proveedor=sku.ruc_proveedor,
            proveedor=sku.proveedor,
        )


class SkusResponse(BaseModel):
    """Response schema for multiple SKUs with metadata."""
    
    skus: List[SkuResponse]
    count: int
    requested_codes: List[str]

    @classmethod
    def from_domain_models(cls, skus: List, requested_codes: List[str]) -> "SkusResponse":
        """Create SkusResponse from domain models."""
        sku_responses = [SkuResponse.from_domain_model(sku) for sku in skus]
        return cls(
            skus=sku_responses,
            count=len(sku_responses),
            requested_codes=requested_codes
        )

#endregion
