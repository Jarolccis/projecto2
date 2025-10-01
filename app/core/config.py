"""Application configuration."""

import os
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
env_path = Path(__file__).parent.parent.parent / ".env" 
load_dotenv(env_path, override=True) 

class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__"
    )

    # Configuración de la aplicación
    app_name: str = Field(json_schema_extra={"env": "APP_NAME"})
    app_version: str = Field(json_schema_extra={"env": "APP_VERSION"})
    debug: bool = Field(json_schema_extra={"env": "DEBUG"})

    # Configuración de PostgreSQL (para migraciones y Docker)
    postgres_user: str = Field(json_schema_extra={"env": "POSTGRES_USER"})
    postgres_password: str = Field(json_schema_extra={"env": "POSTGRES_PASSWORD"})
    postgres_db: str = Field(json_schema_extra={"env": "POSTGRES_DB"})
    postgres_host: str = Field(json_schema_extra={"env": "POSTGRES_HOST"})
    postgres_port: int = Field(json_schema_extra={"env": "POSTGRES_PORT"})
    
    # Configuración SSL para PostgreSQL
    postgres_ssl_mode: str = Field(json_schema_extra={"env": "POSTGRES_SSL_MODE"})
    postgres_ssl_cert: str = Field(json_schema_extra={"env": "POSTGRES_SSL_CERT"})
    postgres_ssl_key: str = Field(json_schema_extra={"env": "POSTGRES_SSL_KEY"})
    postgres_ssl_root_cert: str = Field(json_schema_extra={"env": "POSTGRES_SSL_ROOT_CERT"})
    
    # Configuración del pool de conexiones
    postgres_pool_size: int = Field(json_schema_extra={"env": "POSTGRES_POOL_SIZE"})
    postgres_max_overflow: int = Field(json_schema_extra={"env": "POSTGRES_MAX_OVERFLOW"})
    postgres_pool_timeout: int = Field(json_schema_extra={"env": "POSTGRES_POOL_TIMEOUT"})
    postgres_pool_recycle: int = Field(json_schema_extra={"env": "POSTGRES_POOL_RECYCLE"})
    
    # Configuración de timeouts de conexión
    postgres_connect_timeout: int = Field(json_schema_extra={"env": "POSTGRES_CONNECT_TIMEOUT"})
    postgres_command_timeout: int = Field(json_schema_extra={"env": "POSTGRES_COMMAND_TIMEOUT"})
    postgres_statement_timeout: int = Field(json_schema_extra={"env": "POSTGRES_STATEMENT_TIMEOUT"})
    
    # Configuración adicional de la base de datos
    sql_echo: bool = Field(json_schema_extra={"env": "SQL_ECHO"})

    @property
    def database_url(self) -> str:
        """Construye la URL de conexión a la base de datos usando las variables individuales."""
        base_url = f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        
        # Agregar parámetros SSL si están configurados
        ssl_params = []
        if self.postgres_ssl_mode and self.postgres_ssl_mode != "disable":
            ssl_params.append(f"sslmode={self.postgres_ssl_mode}")
        
        if self.postgres_ssl_cert:
            ssl_params.append(f"sslcert={self.postgres_ssl_cert}")
        
        if self.postgres_ssl_key:
            ssl_params.append(f"sslkey={self.postgres_ssl_key}")
        
        if self.postgres_ssl_root_cert:
            ssl_params.append(f"sslrootcert={self.postgres_ssl_root_cert}")
        
        if ssl_params:
            base_url += "?" + "&".join(ssl_params)
        
        return base_url

    @property
    def database_engine_kwargs(self) -> dict:
        """Retorna los parámetros del motor de base de datos."""
        return {
            "echo": self.sql_echo,
            "future": True,
            "pool_size": self.postgres_pool_size,
            "max_overflow": self.postgres_max_overflow,
            "pool_timeout": self.postgres_pool_timeout,
            "pool_recycle": self.postgres_pool_recycle,
            #"pool_pre_ping": True,  # Verificar conexión antes de usar
        }

    # Configuración de entorno
    environment: str = Field(json_schema_extra={"env": "ENVIRONMENT"})
    log_level: str = Field(json_schema_extra={"env": "LOG_LEVEL"})
    
    # Configuración de seguridad
    cors_origins: str | None = Field(json_schema_extra={"env": "CORS_ORIGINS"})
    cors_allow_credentials: bool = Field(json_schema_extra={"env": "CORS_ALLOW_CREDENTIALS"})
    
    @property
    def cors_origins_list(self) -> list:
        """Convert cors_origins string to list or return ['*'] if not configured."""
        # Si cors_origins es None (no configurado en .env), usar ['*']
        if self.cors_origins is None:
            return ["*"]
        
        # Si cors_origins es string, procesarlo
        if isinstance(self.cors_origins, str):
            if self.cors_origins.strip():
                # Split by comma and clean up each origin
                origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
                return origins if origins else ["*"]
            return ["*"]  # If empty string, allow all origins
        
        # Default fallback
        return ["*"]
    
    
    # Configuración de Google Cloud BigQuery
    gcp_key_file: str = Field(
        default="./bigquery.key.json",
        json_schema_extra={"env": "GCP_KEY_FILE"}
    )
    gcp_project_id: str = Field(
        default="btot-cl-prd-webgestiontottus",
        json_schema_extra={"env": "GCP_PROJECT_ID"}
    )

    # Configuración de Blob Storage
    blob_storage_connection: str = Field(json_schema_extra={"env": "BLOB_STORAGE_CONNECTION"})

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be one of: development, staging, production")
        return v
    



# Global settings instance
settings = Settings()
