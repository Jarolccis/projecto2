from sqlalchemy import select, and_ 
from sqlalchemy.orm import Session
from typing import List

from app.domain.entities.agreement_product import AgreementProduct
from app.infrastructure.postgres.models.tottus.agreement_product_model import AgreementProductModel
from app.core.logging import LoggerMixin


class PostgresAgreementProductRepository(LoggerMixin):

    def __init__(self, session: Session):
        self._session = session

    async def create_agreement_product(self, product: AgreementProduct) -> AgreementProduct:
        try:
            self.log_info(
                "Creating agreement product",
                agreement_id=product.agreement_id,
                sku_code=product.sku_code
            )

            product_model = AgreementProductModel(
                agreement_id=product.agreement_id,
                sku_code=product.sku_code,
                sku_description=product.sku_description,
                division_code=product.division_code,
                division_name=product.division_name,
                department_code=product.department_code,
                department_name=product.department_name,
                subdepartment_code=product.subdepartment_code,
                subdepartment_name=product.subdepartment_name,
                class_code=product.class_code,
                class_name=product.class_name,
                subclass_code=product.subclass_code,
                subclass_name=product.subclass_name,
                brand_id=product.brand_id,
                brand_name=product.brand_name,
                supplier_id=product.supplier_id,
                supplier_name=product.supplier_name,
                supplier_ruc=product.supplier_ruc,
                active=product.active,
                created_by_user_email=product.created_by_user_email,
                updated_status_by_user_email=product.updated_status_by_user_email,
            )

            self._session.add(product_model)
            await self._session.flush()
            await self._session.refresh(product_model)

            product.id = product_model.id
            product.created_at = product_model.created_at
            product.updated_at = product_model.updated_at

            self.log_info(
                "Agreement product created successfully",
                product_id=product.id,
                agreement_id=product.agreement_id
            )

            return product

        except Exception as e:
            self.log_error(
                "Failed to create agreement product",
                error=e,
                agreement_id=product.agreement_id,
                sku_code=product.sku_code
            )
            raise

    async def get_agreement_products(self, agreement_id: int) -> List[AgreementProduct]:
        try:
            self.log_info("Retrieving agreement products", agreement_id=agreement_id)

            stmt = select(AgreementProductModel).where(
                and_(
                    AgreementProductModel.agreement_id == agreement_id,
                    AgreementProductModel.active == True
                )
            )

            result = await self._session.execute(stmt)
            product_models = result.scalars().all()

            products = []
            for model in product_models:
                product = AgreementProduct(
                    id=model.id,
                    agreement_id=model.agreement_id,
                    sku_code=model.sku_code,
                    sku_description=model.sku_description,
                    division_code=model.division_code,
                    division_name=model.division_name,
                    department_code=model.department_code,
                    department_name=model.department_name,
                    subdepartment_code=model.subdepartment_code,
                    subdepartment_name=model.subdepartment_name,
                    class_code=model.class_code,
                    class_name=model.class_name,
                    subclass_code=model.subclass_code,
                    subclass_name=model.subclass_name,
                    brand_id=model.brand_id,
                    brand_name=model.brand_name,
                    supplier_id=model.supplier_id,
                    supplier_name=model.supplier_name,
                    supplier_ruc=model.supplier_ruc,
                    active=model.active,
                    created_at=model.created_at,
                    created_by_user_email=model.created_by_user_email,
                    updated_status_by_user_email=model.updated_status_by_user_email,
                    updated_at=model.updated_at
                )
                products.append(product)

            self.log_info(
                "Retrieved agreement products successfully",
                agreement_id=agreement_id,
                count=len(products)
            )

            return products

        except Exception as e:
            self.log_error(
                "Failed to retrieve agreement products",
                error=e,
                agreement_id=agreement_id
            )
            raise

    async def exists_agreement_product(self, agreement_id: int, sku_code: str) -> bool:
        try:
            self.log_info(
                "Checking if agreement product exists",
                agreement_id=agreement_id,
                sku_code=sku_code
            )

            stmt = select(AgreementProductModel.id).where(
                and_(
                    AgreementProductModel.agreement_id == agreement_id,
                    AgreementProductModel.sku_code == sku_code,
                    AgreementProductModel.active == True
                )
            )

            result = await self._session.execute(stmt)
            scalar_result = result.scalar_one_or_none()
            exists = scalar_result is not None

            self.log_info(
                "Agreement product existence check completed",
                agreement_id=agreement_id,
                sku_code=sku_code,
                exists=exists
            )

            return exists

        except Exception as e:
            self.log_error(
                "Failed to check agreement product existence",
                error=e,
                agreement_id=agreement_id,
                sku_code=sku_code
            )
            raise