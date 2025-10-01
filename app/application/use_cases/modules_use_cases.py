"""Module use cases for business logic."""

from typing import List
from dataclasses import asdict

from app.interfaces.schemas.module_schema import (
    ActiveModuleUsersResponse,
    ModuleIdRequest,
    ModuleSchema,
    ModulesResponse,
    ModuleUserSchema,
    ModuleUsersResponse,
)
from app.domain.repositories.modules_repository import ModulesRepository
from app.core.logging import LoggerMixin


class ModulesUseCases(LoggerMixin):
    """Use cases for module operations."""

    def __init__(self, module_repository: ModulesRepository):
        """Initialize module use cases with repository."""
        self.module_repository = module_repository

    async def get_active_module_users(self) -> ActiveModuleUsersResponse:
        """
        Get distinct user emails from active modules.
        
        Returns:
            ActiveModuleUsersResponse: Response containing user emails and total count
        """
        self.log_info("Iniciando caso de uso: obtener usuarios de módulos activos")
        
        try:
            # Obtener emails de usuarios desde el repositorio
            user_emails = await self.module_repository.get_active_module_users()
            
            # Crear respuesta estructurada
            response = ActiveModuleUsersResponse(
                user_emails=user_emails,
                total_users=len(user_emails)
            )
            
            self.log_info(
                "Caso de uso completado: usuarios de módulos activos obtenidos",
                total_users=response.total_users
            )
            
            return response
            
        except Exception as e:
            self.log_error(
                "Error en caso de uso: obtener usuarios de módulos activos",
                error=str(e)
            )
            raise

    async def get_active_modules(self) -> ModulesResponse:
        """
        Get all active modules.
        
        Returns:
            ModulesResponse: Response containing active modules
        """
        self.log_info("Iniciando caso de uso: obtener módulos activos")
        
        try:
            # Obtener módulos activos desde el repositorio
            modules = await self.module_repository.get_active_modules()
            
            # Convertir a schemas
            module_schemas = [
                ModuleSchema.model_validate(asdict(module))
                for module in modules
            ]
            
            # Crear respuesta estructurada
            response = ModulesResponse(
                modules=module_schemas,
                total_modules=len(module_schemas)
            )
            
            self.log_info(
                "Caso de uso completado: módulos activos obtenidos",
                total_active_modules=response.total_modules
            )
            
            return response
            
        except Exception as e:
            self.log_error(
                "Error en caso de uso: obtener módulos activos",
                error=str(e)
            )
            raise

    async def get_module_users_by_module_id(self, request: ModuleIdRequest) -> ModuleUsersResponse:
        """
        Get all users for a specific module.
        
        Args:
            request: ModuleIdRequest containing the module_id
            
        Returns:
            ModuleUsersResponse: Response containing module users
        """
        self.log_info(
            "Iniciando caso de uso: obtener usuarios por módulo",
            module_id=request.module_id
        )
        
        try:
            # Obtener usuarios del módulo desde el repositorio
            module_users = await self.module_repository.get_module_users_by_module_id(
                request.module_id
            )
            
            # Convertir a schemas
            user_schemas = [
                ModuleUserSchema.model_validate(asdict(user))
                for user in module_users
            ]
            
            # Crear respuesta estructurada
            response = ModuleUsersResponse(
                users=user_schemas,
                total_users=len(user_schemas),
                module_id=request.module_id
            )
            
            self.log_info(
                "Caso de uso completado: usuarios por módulo obtenidos",
                module_id=request.module_id,
                total_users=response.total_users
            )
            
            return response
            
        except Exception as e:
            self.log_error(
                "Error en caso de uso: obtener usuarios por módulo",
                module_id=request.module_id,
                error=str(e)
            )
            raise
