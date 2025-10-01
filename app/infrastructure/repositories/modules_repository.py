"""PostgreSQL module repository implementation."""

from typing import List

from sqlalchemy import distinct, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.module import Module, ModuleUser
from app.domain.repositories.modules_repository import ModulesRepository
from app.core.logging import LoggerMixin
from app.infrastructure.postgres.models.tottus.module_users_model import ModuleUsersModel
from app.infrastructure.postgres.models.tottus.modules_model import ModulesModel


def _module_to_entity(model: ModulesModel) -> Module:
    """Convert Modules ORM to Module entity."""
    return Module(
        id=model.id,
        business_unit_id=model.business_unit_id,
        name=model.name,
        description=model.description,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _module_user_to_entity(model: ModuleUsersModel) -> ModuleUser:
    """Convert ModuleUsers ORM to ModuleUser entity."""
    return ModuleUser(
        id=model.id,
        user_email=model.user_email,
        module_id=model.module_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class ModulesRepository(ModulesRepository, LoggerMixin):
    """PostgreSQL implementation of ModuleRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        self._session = session

    async def get_active_module_users(self) -> List[str]:
        """
        Get distinct user emails from active modules.
        
        Executes the query:
        SELECT distinct mu.user_email
        FROM tottus_pe.module_users mu 
        inner join tottus_pe.modules m on m.id = mu.module_id 
        where m.is_active = true
        order by mu.user_email
        """
        self.log_info("Starting active module users query")
        
        try:
            query = (
                select(distinct(ModuleUsersModel.user_email))
                .select_from(
                    ModuleUsersModel.__table__.join(
                        ModulesModel.__table__, 
                        ModulesModel.id == ModuleUsersModel.module_id
                    )
                )
                .where(ModulesModel.is_active == True)
                .order_by(ModuleUsersModel.user_email)
            )
            
            self.log_debug("Executing active module users query")

            # Execute the query
            result = await self._session.execute(query)
            user_emails = [row[0] for row in result.fetchall()]
            
            self.log_info(
                "Active module users query completed",
                total_users=len(user_emails)
            )
            
            return user_emails
                
        except SQLAlchemyError as e:
            self.log_error(
                "Database error querying active module users",
                error=str(e),
                operation="get_active_module_users"
            )
            raise Exception(f"Error getting active module users: {str(e)}")
        except Exception as e:
            self.log_error(
                "Unexpected error querying active module users",
                error=str(e),
                operation="get_active_module_users"
            )
            raise Exception(f"Unexpected error getting active module users: {str(e)}")

    async def get_active_modules(self) -> List[Module]:
        """Get all active modules."""
        self.log_info("Starting active modules query")
        
        try:
            query = (
                select(ModulesModel)
                .where(ModulesModel.is_active == True)
                .order_by(ModulesModel.name)
            )
            
            result = await self._session.execute(query)
            modules_orm = result.scalars().all()
            
            modules = [_module_to_entity(module) for module in modules_orm]
            
            self.log_info(
                "Active modules query completed",
                total_active_modules=len(modules)
            )
            
            return modules
                
        except SQLAlchemyError as e:
            self.log_error(
                "Database error querying active modules",
                error=str(e),
                operation="get_active_modules"
            )
            raise Exception(f"Error getting active modules: {str(e)}")
        except Exception as e:
            self.log_error(
                "Unexpected error querying active modules",
                error=str(e),
                operation="get_active_modules"
            )
            raise Exception(f"Unexpected error getting active modules: {str(e)}")

    async def get_module_users_by_module_id(self, module_id: int) -> List[ModuleUser]:
        """Get all users for a specific module."""
        self.log_info("Starting module users query", module_id=module_id)
        
        try:
            query = (
                select(ModuleUsersModel)
                .where(ModuleUsersModel.module_id == module_id)
                .order_by(ModuleUsersModel.user_email)
            )
            
            result = await self._session.execute(query)
            module_users_orm = result.scalars().all()
            
            module_users = [_module_user_to_entity(user) for user in module_users_orm]
            
            self.log_info(
                "Module users query completed",
                module_id=module_id,
                total_users=len(module_users)
            )
            
            return module_users
                
        except SQLAlchemyError as e:
            self.log_error(
                "Database error querying module users",
                error=str(e),
                module_id=module_id,
                operation="get_module_users_by_module_id"
            )
            raise Exception(f"Error getting users for module {module_id}: {str(e)}")
        except Exception as e:
            self.log_error(
                "Unexpected error querying module users",
                error=str(e),
                module_id=module_id,
                operation="get_module_users_by_module_id"
            )
            raise Exception(f"Unexpected error getting users for module {module_id}: {str(e)}")
