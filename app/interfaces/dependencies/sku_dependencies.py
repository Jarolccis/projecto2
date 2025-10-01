from typing import Annotated
from fastapi import Depends
from app.domain.repositories.sku_repository import SkuRepository
from app.application.use_cases.sku_use_cases import SkuUseCases
from app.infrastructure.repositories.sku_repository import SkuRepository as SkuRepositoryImpl


def get_sku_repository() -> SkuRepository:
    return SkuRepositoryImpl()


def get_sku_use_cases(
    sku_repository: Annotated[SkuRepository, Depends(get_sku_repository)]
) -> SkuUseCases:
    return SkuUseCases(sku_repository)


SkuRepositoryDep = Annotated[SkuRepository, Depends(get_sku_repository)]
SkuUseCasesDep = Annotated[SkuUseCases, Depends(get_sku_use_cases)]
