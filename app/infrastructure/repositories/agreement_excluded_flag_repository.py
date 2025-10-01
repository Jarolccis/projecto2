
from sqlalchemy import select, and_ 
from sqlalchemy.orm import Session
from typing import List

from app.domain.entities.agreement_excluded_flag import AgreementExcludedFlag
from app.infrastructure.postgres.models.tottus.agreement_excluded_flag_model import AgreementExcludedFlagModel
from app.infrastructure.postgres.models.tottus.lookup_category_model import LookupCategoryModel
from app.infrastructure.postgres.models.tottus.lookup_value_model import LookupValueModel
from app.core.constants import EXCLUDED_FLAGS_CATEGORY
from app.core.logging import LoggerMixin




class PostgresAgreementExcludedFlagRepository(LoggerMixin):

    def __init__(self, session: Session):
        self._session = session

    async def create_agreement_excluded_flag(self, excluded_flag: AgreementExcludedFlag) -> AgreementExcludedFlag:
        try:
            self.log_info(
                "Creating agreement excluded flag",
                agreement_id=excluded_flag.agreement_id,
                excluded_flag_id=excluded_flag.excluded_flag_id
            )

            excluded_flag_model = AgreementExcludedFlagModel(
                agreement_id=excluded_flag.agreement_id,
                excluded_flag_id=excluded_flag.excluded_flag_id,
                active=excluded_flag.active,
                created_by_user_email=excluded_flag.created_by_user_email,
                updated_status_by_user_email=excluded_flag.updated_status_by_user_email,
            )

            self._session.add(excluded_flag_model)
            await self._session.flush()
            await self._session.refresh(excluded_flag_model)

            # Update the entity with the generated ID
            excluded_flag.id = excluded_flag_model.id
            excluded_flag.created_at = excluded_flag_model.created_at
            excluded_flag.updated_at = excluded_flag_model.updated_at

            self.log_info(
                "Agreement excluded flag created successfully",
                excluded_flag_id=excluded_flag.id,
                agreement_id=excluded_flag.agreement_id
            )

            return excluded_flag

        except Exception as e:
            self.log_error(
                "Failed to create agreement excluded flag",
                error=e,
                agreement_id=excluded_flag.agreement_id,
                excluded_flag_id=excluded_flag.excluded_flag_id
            )
            raise

    async def get_agreement_excluded_flags(self, agreement_id: int) -> List[AgreementExcludedFlag]:
        try:
            self.log_info("Retrieving agreement excluded flags with flag names", agreement_id=agreement_id)

            # Create aliases for lookup joins
            lc_excluded_flags = LookupCategoryModel.__table__.alias('lc_excluded_flags')
            lv_excluded_flags = LookupValueModel.__table__.alias('lv_excluded_flags')

            # Select specific columns for better performance and clarity
            stmt = select(
                AgreementExcludedFlagModel.id,
                AgreementExcludedFlagModel.agreement_id,
                AgreementExcludedFlagModel.excluded_flag_id,
                AgreementExcludedFlagModel.active,
                AgreementExcludedFlagModel.created_at,
                AgreementExcludedFlagModel.created_by_user_email,
                AgreementExcludedFlagModel.updated_at,
                AgreementExcludedFlagModel.updated_status_by_user_email,
                lv_excluded_flags.c.display_value.label('excluded_flag_name')
            ).select_from(
                AgreementExcludedFlagModel.__table__
                # Excluded flags lookup
                .outerjoin(lc_excluded_flags, lc_excluded_flags.c.code == EXCLUDED_FLAGS_CATEGORY)
                .outerjoin(lv_excluded_flags, and_(
                    lv_excluded_flags.c.category_id == lc_excluded_flags.c.id,
                    lv_excluded_flags.c.option_value == AgreementExcludedFlagModel.excluded_flag_id
                ))
            ).where(
                and_(
                    AgreementExcludedFlagModel.agreement_id == agreement_id,
                    AgreementExcludedFlagModel.active == True
                )
            )

            result = await self._session.execute(stmt)
            rows = result.fetchall()

            excluded_flags = []
            for row in rows:
                excluded_flag = AgreementExcludedFlag(
                    id=row.id,
                    agreement_id=row.agreement_id,
                    excluded_flag_id=row.excluded_flag_id,
                    active=row.active,
                    created_at=row.created_at,
                    created_by_user_email=row.created_by_user_email,
                    updated_at=row.updated_at,
                    updated_status_by_user_email=row.updated_status_by_user_email,
                    excluded_flag_name=row.excluded_flag_name
                )
                excluded_flags.append(excluded_flag)

            self.log_info(
                "Retrieved agreement excluded flags with flag names successfully",
                agreement_id=agreement_id,
                count=len(excluded_flags)
            )

            return excluded_flags

        except Exception as e:
            self.log_error(
                "Failed to retrieve agreement excluded flags with flag names",
                error=e,
                agreement_id=agreement_id
            )
            raise

    async def exists_agreement_excluded_flag(self, agreement_id: int, excluded_flag_id: str) -> bool:
        try:
            self.log_info(
                "Checking if agreement excluded flag exists",
                agreement_id=agreement_id,
                excluded_flag_id=excluded_flag_id
            )

            stmt = select(AgreementExcludedFlagModel.id).where(
                and_(
                    AgreementExcludedFlagModel.agreement_id == agreement_id,
                    AgreementExcludedFlagModel.excluded_flag_id == excluded_flag_id,
                    AgreementExcludedFlagModel.active == True
                )
            )

            result = await self._session.execute(stmt)
            scalar_result = result.scalar_one_or_none()
            exists = scalar_result is not None

            self.log_info(
                "Agreement excluded flag existence check completed",
                agreement_id=agreement_id,
                excluded_flag_id=excluded_flag_id,
                exists=exists
            )

            return exists

        except Exception as e:
            self.log_error(
                "Failed to check agreement excluded flag existence",
                error=e,
                agreement_id=agreement_id,
                excluded_flag_id=excluded_flag_id
            )
            raise
