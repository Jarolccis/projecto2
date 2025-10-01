from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Sku:
    
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
    def create(
        cls,
        sku: str,
        descripcion_sku: str,
        costo_reposicion: Decimal,
        estado_id: int,
        marca_id: int,
        marca: str,
        subclase_id: int,
        codigo_subclase: str,
        subclase: str,
        clase_id: int,
        codigo_clase: str,
        clase: str,
        subdepartamento_id: int,
        codigo_subdepartamento: str,
        subdepartamento: str,
        departamento_id: int,
        codigo_departamento: str,
        departamento: str,
        division_id: int,
        codigo_division: str,
        division: str,
        proveedor_id: int,
        ruc_proveedor: str,
        proveedor: str,
    ) -> "Sku":
        return cls(
            sku=sku,
            descripcion_sku=descripcion_sku,
            costo_reposicion=costo_reposicion,
            estado_id=estado_id,
            marca_id=marca_id,
            marca=marca,
            subclase_id=subclase_id,
            codigo_subclase=codigo_subclase,
            subclase=subclase,
            clase_id=clase_id,
            codigo_clase=codigo_clase,
            clase=clase,
            subdepartamento_id=subdepartamento_id,
            codigo_subdepartamento=codigo_subdepartamento,
            subdepartamento=subdepartamento,
            departamento_id=departamento_id,
            codigo_departamento=codigo_departamento,
            departamento=departamento,
            division_id=division_id,
            codigo_division=codigo_division,
            division=division,
            proveedor_id=proveedor_id,
            ruc_proveedor=ruc_proveedor,
            proveedor=proveedor,
        )
