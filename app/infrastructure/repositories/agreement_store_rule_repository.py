from sqlalchemy import select, and_, outerjoin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List

from app.domain.entities.agreement_store_rule import AgreementStoreRule
from app.infrastructure.postgres.models.tottus.agreement_store_rule_model import AgreementStoreRuleModel
from app.infrastructure.postgres.models.tottus.stores_model import StoresModel
from app.core.logging import LoggerMixin


class PostgresAgreementStoreRuleRepository(LoggerMixin):

    def __init__(self, session: Session):
        self._session = session

    async def create_agreement_store_rule(self, store_rule: AgreementStoreRule) -> AgreementStoreRule:
        try:
            self.log_info(
                "Creating agreement store rule",
                agreement_id=store_rule.agreement_id,
                store_id=store_rule.store_id,
                status=store_rule.status
            )

            store_rule_model = AgreementStoreRuleModel(
                agreement_id=store_rule.agreement_id,
                store_id=store_rule.store_id,
                status=store_rule.status,
                active=store_rule.active,
                created_by_user_email=store_rule.created_by_user_email,
                updated_status_by_user_email=store_rule.updated_status_by_user_email,
            )

            self._session.add(store_rule_model)
            await self._session.flush()
            await self._session.refresh(store_rule_model)

            store_rule.id = store_rule_model.id
            store_rule.created_at = store_rule_model.created_at
            store_rule.updated_at = store_rule_model.updated_at

            self.log_info(
                "Agreement store rule created successfully",
                store_rule_id=store_rule.id,
                agreement_id=store_rule.agreement_id
            )

            return store_rule

        except Exception as e:
            self.log_error(
                "Failed to create agreement store rule",
                error=e,
                agreement_id=store_rule.agreement_id,
                store_id=store_rule.store_id
            )
            raise

    async def get_agreement_store_rules(self, agreement_id: int) -> List[AgreementStoreRule]:
        try:
            self.log_info("Retrieving agreement store rules with store names", agreement_id=agreement_id)

            # Select specific columns for better performance and clarity
            stmt = select(
                AgreementStoreRuleModel.id,
                AgreementStoreRuleModel.agreement_id,
                AgreementStoreRuleModel.store_id,
                AgreementStoreRuleModel.status,
                AgreementStoreRuleModel.active,
                AgreementStoreRuleModel.created_at,
                AgreementStoreRuleModel.created_by_user_email,
                AgreementStoreRuleModel.updated_status_by_user_email,
                AgreementStoreRuleModel.updated_at,
                StoresModel.name.label('store_name')
            ).select_from(
                AgreementStoreRuleModel.__table__.outerjoin(
                    StoresModel.__table__,
                    AgreementStoreRuleModel.store_id == StoresModel.store_id
                )
            ).where(
                and_(
                    AgreementStoreRuleModel.agreement_id == agreement_id,
                    AgreementStoreRuleModel.active == True
                )
            )

            result = await self._session.execute(stmt)
            rows = result.fetchall()

            store_rules = []
            for row in rows:
                store_rule = AgreementStoreRule(
                    id=row.id,
                    agreement_id=row.agreement_id,
                    store_id=row.store_id,
                    status=row.status,
                    active=row.active,
                    created_at=row.created_at,
                    created_by_user_email=row.created_by_user_email,
                    updated_status_by_user_email=row.updated_status_by_user_email,
                    updated_at=row.updated_at,
                    store_name=row.store_name
                )
                store_rules.append(store_rule)

            self.log_info(
                "Retrieved agreement store rules with store names successfully",
                agreement_id=agreement_id,
                count=len(store_rules)
            )

            return store_rules

        except Exception as e:
            self.log_error(
                "Failed to retrieve agreement store rules with store names",
                error=e,
                agreement_id=agreement_id
            )
            raise

    async def exists_agreement_store_rule(self, agreement_id: int, store_id: int) -> bool:
        try:
            self.log_info(
                "Checking if agreement store rule exists",
                agreement_id=agreement_id,
                store_id=store_id
            )

            stmt = select(AgreementStoreRuleModel.id).where(
                and_(
                    AgreementStoreRuleModel.agreement_id == agreement_id,
                    AgreementStoreRuleModel.store_id == store_id,
                    AgreementStoreRuleModel.active == True
                )
            )

            result = await self._session.execute(stmt)
            scalar_result = result.scalar_one_or_none()
            exists = scalar_result is not None

            self.log_info(
                "Agreement store rule existence check completed",
                agreement_id=agreement_id,
                store_id=store_id,
                exists=exists
            )

            return exists

        except Exception as e:
            self.log_error(
                "Failed to check agreement store rule existence",
                error=e,
                agreement_id=agreement_id,
                store_id=store_id
            )
            raise
