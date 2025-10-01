# 🚀 Rebate Management Backend - Tottus Perú

## 📋 Project Description

Complete backend system for managing rebates and discounts for Tottus Perú, built with **FastAPI** following **Clean Architecture** principles. The project implements a scalable, secure, and maintainable architecture for handling commercial operations.

## 🏗️ System Architecture

### **Clean Architecture Implementation**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACES LAYER                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   API Routes    │  │   Middleware    │  │ Controllers │ │
│  │   (FastAPI)     │  │ (Rate Limiting) │  │             │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Use Cases     │  │    Schemas      │  │    DTOs     │ │
│  │ (Business Logic)│  │ (Validation)    │  │             │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │    Entities     │  │   Repositories  │  │  Interfaces │ │
│  │ (Core Business) │  │   (Contracts)   │  │             │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                INFRASTRUCTURE LAYER                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   PostgreSQL    │  │   BigQuery      │  │   Redis     │ │
│  │   (Database)    │  │  (Analytics)    │  │ (Caching)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Directory Structure**

```
app/
├── application/           # Application layer
│   ├── schemas/          # Pydantic schemas and validations
│   ├── use_cases/        # Business use cases
│   └── services/         # Business services
├── domain/               # Domain layer
│   ├── entities/         # Business entities
│   ├── repositories/     # Repository interfaces
│   └── utils/            # Domain utilities
├── infrastructure/       # Infrastructure layer
│   ├── postgres/         # PostgreSQL implementation
│   ├── bigquery/         # BigQuery integration
│   ├── security/         # Security implementations
│   ├── repositories/     # Repository implementations
│   ├── config.py         # Application configuration
│   └── logging.py        # Logging system
└── interfaces/           # Interface layer
    └── api/              # REST API
        ├── controllers/   # Endpoint controllers
        ├── dependencies/  # Dependency injection
        ├── middleware/    # Custom middleware
        └── routers/       # API routing
```

### **Arquitectura Detallada por Capas**

#### **🔴 Interfaces Layer (Capa Externa)**
**Propósito:** Maneja la comunicación con el mundo exterior
- **API Routes:** Definición de endpoints REST con FastAPI
- **Controllers:** Lógica de presentación y validación de requests
- **Middleware:** Rate limiting, logging, CORS, autenticación
- **Dependencies:** Inyección de dependencias y configuración

**Archivos Principales:**
```
app/interfaces/api/
├── controllers/          # Controladores de endpoints
│   ├── stores.py        # Gestión de tiendas
│   └── suppliers.py     # Gestión de proveedores
├── middleware/           # Middleware personalizado
│   ├── auth_middleware.py # Autenticación y autorización
│   ├── rate_limiter.py  # Limitación de velocidad
│   └── request_logging.py # Logging estructurado
├── dependencies/         # Inyección de dependencias
└── routers/             # Configuración de rutas
```

#### **🟡 Application Layer (Capa de Aplicación)**
**Propósito:** Orquesta los casos de uso y la lógica de negocio
- **Use Cases:** Implementación de reglas de negocio
- **Schemas:** Validación y serialización de datos
- **DTOs:** Objetos de transferencia de datos

**Archivos Principales:**
```
app/application/
├── use_cases/           # Casos de uso de negocio
│   ├── store_use_cases.py      # Lógica de tiendas
│   └── supplier_use_cases.py   # Lógica de proveedores
├── schemas/             # Esquemas de validación
│   ├── store.py         # Esquemas de tienda
│   ├── supplier.py      # Esquemas de proveedor
│   └── response.py      # Esquemas de respuesta
└── services/            # Servicios de negocio
    └── auth_service.py  # Servicio de autenticación
```

#### **🟢 Domain Layer (Capa de Dominio)**
**Propósito:** Contiene las entidades de negocio y contratos
- **Entities:** Objetos de dominio puros
- **Repositories:** Interfaces para acceso a datos
- **DTOs:** Objetos de transferencia de dominio

**Archivos Principales:**
```
app/domain/
├── entities/            # Entidades de negocio
│   ├── store.py         # Entidad Tienda
│   └── supplier.py      # Entidad Proveedor
├── repositories/         # Interfaces de repositorio
│   ├── store_repository.py      # Contrato para tiendas
│   └── supplier_repository.py   # Contrato para proveedores
└── utils/               # Utilidades de dominio
    └── business_utils.py # Utilidades de negocio
```

#### **🔵 Infrastructure Layer (Capa de Infraestructura)**
**Propósito:** Implementa el acceso a servicios externos
- **PostgreSQL:** Base de datos principal
- **BigQuery:** Análisis y reportes
- **Redis:** Caché y rate limiting
- **Config:** Configuración de la aplicación

**Archivos Principales:**
```
app/infrastructure/
├── postgres/            # Implementación PostgreSQL
│   ├── models/          # Modelos de base de datos
│   ├── session.py       # Gestión de sesiones
│   └── repositories/    # Implementaciones concretas
├── bigquery/            # Integración BigQuery
│   ├── bigquery_helper.py       # Utilidades
│   └── repositories/            # Repositorios BigQuery
├── security/            # Implementaciones de seguridad
│   ├── keycloak_strategy.py     # Estrategia Keycloak
│   ├── security_context.py      # Contexto de seguridad
│   └── constants.py             # Constantes de seguridad
├── repositories/        # Implementaciones de repositorios
├── config.py            # Configuración centralizada
└── logging.py           # Sistema de logging
```

### **Flujo de Datos en la Arquitectura**

```
Request → Controller → Use Case → Repository → Database
   ↑                                                      ↓
Response ← Schema ← Entity ← DTO ← Repository ← Database
```

1. **Request llega** al Controller
2. **Controller valida** usando Schemas
3. **Use Case ejecuta** la lógica de negocio
4. **Repository accede** a los datos
5. **Entity/DTO se convierte** a Schema
6. **Response se serializa** y retorna

### **Principios de Clean Architecture Aplicados**

- **Dependency Inversion:** Las capas internas no dependen de las externas
- **Single Responsibility:** Cada clase tiene una responsabilidad específica
- **Open/Closed:** Abierto para extensión, cerrado para modificación
- **Interface Segregation:** Interfaces pequeñas y específicas
- **Dependency Injection:** Dependencias se inyectan, no se crean

## 🚀 Core Features

### **✅ Core Functionalities**
- **Clean Architecture** completely implemented
- **FastAPI** with automatic OpenAPI documentation
- **Pydantic** for data validation and serialization
- **SQLAlchemy 2.0** as modern ORM
- **PostgreSQL** as primary database
- **BigQuery** for analytics and reports
- **Redis** for rate limiting and caching

### **🔒 Security and Performance**
- **Advanced Rate Limiting** with multiple strategies
- **Multi-layer security validation**
- **Configurable authentication middleware**
- **Secure CORS** configuration
- **Structured logging** with different levels
- **Standardized error handling**

### **📊 Monitoring and Observability**
- **Structured logging system** with structlog
- **Real-time rate limiting metrics**
- **Automatic attack pattern detection**
- **Health checks** for critical services
- **Complete request traceability**
- **Comprehensive monitoring and observability**

## 📊 **Monitoring & Observability**

### **Health Checks**
- **Application Health**: `/health` endpoint for overall system status
- **Database Health**: Connection pool status and response times
- **External Services**: BigQuery, Redis, and Keycloak connectivity
- **Custom Metrics**: Business logic health indicators

### **Logging & Tracing**
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Request Tracing**: Complete request lifecycle tracking
- **Error Tracking**: Detailed error context and stack traces
- **Performance Metrics**: Response times and resource usage

### **Metrics & Monitoring**
- **Rate Limiting**: Real-time API usage and throttling metrics
- **Database Performance**: Query execution times and connection pool stats
- **Security Events**: Authentication attempts and authorization failures
- **Business Metrics**: Store and supplier operation counts

### **Alerting & Notifications**
- **Performance Alerts**: Response time thresholds exceeded
- **Error Rate Alerts**: High error rates or critical failures
- **Security Alerts**: Suspicious authentication patterns
- **Resource Alerts**: Database connection pool exhaustion

## 🛠️ Technology Stack

### **Backend Framework**
- **FastAPI 0.104.0+** - Modern and fast web framework
- **Uvicorn** - High-performance ASGI server
- **Pydantic 2.5.0+** - Data validation and serialization

## 📦 Dependency Management

### **Dual Dependency Files**

This project maintains both dependency management approaches for maximum compatibility:

#### **pyproject.toml (Recommended)**
- **Modern standard** following PEP 518
- **Organized dependencies** by type (core, dev, test)
- **Project metadata** and configuration
- **Tool configuration** (Ruff, pytest, etc.)
- **Better dependency resolution** and conflict handling

#### **requirements.txt (Alternative)**
- **Traditional format** for maximum compatibility
- **Simple text format** easy to read and edit
- **Compatible with all tools** and CI/CD pipelines
- **Backup option** if pyproject.toml has issues

### **When to Use Each**

| Use Case | Recommended File | Reason |
|----------|------------------|---------|
| **Development** | `pyproject.toml` | Better organization, tool config |
| **Production** | `requirements.txt` | Simple, reliable, universal |
| **CI/CD** | Both | Flexibility for different tools |
| **Docker** | `requirements.txt` | Simple, fast builds |
| **Local Dev** | `pyproject.toml` | Editable install, tool config |

### **Keeping Both Files Synchronized**

To maintain consistency between both files:

#### **Automatic Synchronization**
```bash
# Generate requirements.txt from pyproject.toml
pip install -e ".[dev]"
pip freeze > requirements.txt

# Or use pip-tools for better control
pip install pip-tools
pip-compile pyproject.toml --output-file=requirements.txt
```

#### **Manual Synchronization Steps**
```bash
# Step 1: Update pyproject.toml with new dependencies
# Edit pyproject.toml and add new packages

# Step 2: Install new dependencies
pip install -e ".[dev]"

# Step 3: Update requirements.txt
pip freeze > requirements.txt

# Step 4: Verify both files are in sync
echo "=== pyproject.toml dependencies ==="
grep -E "^    \".*" pyproject.toml | sed 's/    "//;s/",//'

echo "=== requirements.txt dependencies ==="
grep -v "^#" requirements.txt | grep -v "^$"
```

#### **Synchronization Script**
Create a `sync_deps.sh` script for easy maintenance:

```bash
#!/bin/bash
echo "🔄 Synchronizing dependencies..."

# Install from pyproject.toml
echo "📦 Installing from pyproject.toml..."
pip install -e ".[dev]"

# Generate requirements.txt
echo "📝 Generating requirements.txt..."
pip freeze > requirements.txt

# Clean up common packages
echo "🧹 Cleaning up requirements.txt..."
sed -i '/^#/d' requirements.txt
sed -i '/^$/d' requirements.txt

echo "✅ Dependencies synchronized!"
echo "📊 Total packages: $(wc -l < requirements.txt)"
```

### **Database**
- **PostgreSQL** - Primary relational database
- **SQLAlchemy 2.0.21** - Modern and type-safe ORM
- **psycopg2-binary** - Native PostgreSQL driver
- **Alembic** - Migration system

### **Cache and Rate Limiting**
- **Redis** - In-memory storage and rate limiting
- **slowapi** - Rate limiting for FastAPI
- **fastapi-limiter** - Limitation middleware

### **Security**
- **passlib[bcrypt]** - Password hashing
- **python-jose[cryptography]** - JWT tokens
- **cryptography** - High-level cryptography
- **bleach** - HTML sanitization

### **Logging and Monitoring**
- **structlog** - Structured logging
- **python-json-logger** - JSON format for logs
- **pydantic-settings** - Configuration management

### **Development and Testing**
- **Ruff** - Code linter and formatter
- **pytest** - Testing framework
- **httpx** - HTTP client for testing

## ⚙️ System Configuration

### **Required Environment Variables**

```bash
# Application Configuration
APP_NAME="Rebate Management API"
APP_VERSION="0.1.0"
DEBUG=true
API_PREFIX="/api/v1"
ENVIRONMENT="development"

# PostgreSQL Database
POSTGRES_USER="rbm_tot"
POSTGRES_PASSWORD="kM4a.qIZ&m!B*CjVs.CN"
POSTGRES_DB="rebates_management"
POSTGRES_HOST="txd-notas-pg-flex-dev-server.postgres.database.azure.com"
POSTGRES_PORT=5432

# PostgreSQL SSL Configuration
POSTGRES_SSL_MODE="require"
POSTGRES_SSL_CERT=""
POSTGRES_SSL_KEY=""
POSTGRES_SSL_ROOT_CERT=""

# Connection Pool
POSTGRES_POOL_SIZE=10
POSTGRES_MAX_OVERFLOW=20
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=3600

# Additional Configuration
SQL_ECHO=false
LOG_LEVEL="info"

# CORS Security
CORS_ORIGINS="http://localhost:3000,https://app.tottus.com.pe"
CORS_ALLOW_CREDENTIALS=false
```

### **Database Configuration**

```python
# Database connection configuration example
database_url = "postgresql+psycopg2://user:pass@host:port/db?sslmode=require"

# Connection pool parameters
pool_config = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}
```

## 🚀 Installation and Deployment

### **Option 1: Docker (Recommended)**

#### **Production**
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f web
```

#### **Development with Hot Reload**
```bash
# Use development file
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d --build
```

### **Option 2: Local Installation**

#### **Prerequisites**
- Python 3.11+
- PostgreSQL 13+
- Redis 6+

#### **Installation**

##### **Option 1: Using pyproject.toml (Recommended)**
```bash
# Clone repository
git clone <repository-url>
cd rebate-management-back-totpe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install project in editable mode with all dependencies
pip install -e ".[dev]"

# Configure environment variables
cp env.example .env
# Edit .env with your values

# Run application
python main.py
```

##### **Option 2: Using requirements.txt (Alternative)**
```bash
# Clone repository
git clone <repository-url>
cd rebate-management-back-totpe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Configure environment variables
cp env.example .env
# Edit .env with your values

# Run application
python main.py
```

##### **Option 3: Install only core dependencies**
```bash
# Install only production dependencies
pip install -e .

# Install development dependencies separately
pip install -e ".[dev]"
```

### **Verification Commands**

After installation, verify that everything works correctly:

#### **Verify pyproject.toml Installation**
```bash
# Check if project is installed in editable mode
pip list | grep rebate-management-backend

# Verify imports work
python -c "import app; print('✅ App imported successfully')"
python -c "from app.infrastructure.config import settings; print(f'✅ Config: {settings.app_name}')"

# Run tests to verify all dependencies
python -m pytest --version
python -m pytest tests/ -v --tb=short
```

#### **Verify requirements.txt Installation**
```bash
# Check installed packages
pip list

# Verify imports work
python -c "import fastapi; print('✅ FastAPI imported successfully')"
python -c "import uvicorn; print('✅ Uvicorn imported successfully')"

# Run basic tests
python -c "import pytest; print('✅ Pytest available')"
```

#### **Quick Test Run**
```bash
# Test the application startup
python -c "
from main import app
print('✅ Application created successfully')
print(f'✅ App name: {app.title}')
print(f'✅ App version: {app.version}')
"
```

## 📡 API Endpoints

### **Base URL**
```
http://localhost:8000/api/v1
```

### **Available Endpoints**

#### **Health Check**
- `GET /` - Application status
- `GET /health` - System health verification

#### **Documentation**
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### **Active Middleware**
- **Request Logging** - Logging of all requests
- **Rate Limiting** - Speed limitation per IP/user
- **CORS** - Cross-origin configuration
- **Error Handling** - Standardized error handling

## 🔒 Security System

### **Advanced Rate Limiting**

#### **Implemented Strategies**
- **Per second** - Burst request control
- **Per minute** - Medium frequency control
- **Per hour** - Daily usage control
- **Per day** - Monthly usage control

#### **Risk Levels**
```python
class RiskLevel(Enum):
    LOW = "low"           # Read endpoints
    MEDIUM = "medium"     # Write endpoints
    HIGH = "high"         # Authentication endpoints
    CRITICAL = "critical" # Delete endpoints
```

#### **Reputation System**
- **IP Whitelist** - Trusted IPs
- **IP Blacklist** - Blocked IPs
- **Reputation Score** - Based on behavior
- **Pattern Detection** - Automatic attacks

### **Security Validation**

#### **Validation Layers**
1. **Input Layer** - Basic input validation
2. **Security Layer** - Injection detection
3. **Business Layer** - Business logic
4. **Integrity Layer** - Sanitization and normalization

#### **Implemented Protections**
- **SQL Injection** - Pattern detection
- **NoSQL Injection** - MongoDB validation
- **XSS Prevention** - HTML sanitization
- **Directory Traversal** - Path blocking
- **Timing Attacks** - Time normalization

## 📊 Logging System

### **Logging Configuration**

```python
# Configuration example
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(timestamp)s %(level)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}
```

### **Log Levels**
- **DEBUG** - Detailed development information
- **INFO** - General application information
- **WARNING** - Non-critical warnings
- **ERROR** - Errors requiring attention
- **CRITICAL** - Critical system errors

## 🧪 Testing

### **Estado Actual**
- **Cobertura de Tests:** 25% (mejorando constantemente)
- **Framework:** pytest 8.4.1 con soporte completo
- **Cobertura:** pytest-cov para reportes detallados
- **Tests Asíncronos:** pytest-asyncio para operaciones async

### **Comandos de Testing**

#### **Ejecutar Todos los Tests**
```bash
# Tests básicos
python -m pytest

# Tests con información detallada
python -m pytest -v

# Tests con reporte de cobertura
python -m pytest --cov=app --cov-report=term-missing

# Tests con reporte HTML
python -m pytest --cov=app --cov-report=html:htmlcov

# Tests con reporte XML (para CI/CD)
python -m pytest --cov=app --cov-report=xml:coverage.xml
```

#### **Ejecutar Tests Específicos**
```bash
# Tests de configuración
python -m pytest tests/test_config.py -v

# Tests de logging
python -m pytest tests/test_logging.py -v

# Tests de dependencias
python -m pytest tests/test_dependencies.py -v

# Tests de rate limiting
python -m pytest tests/test_advanced_rate_limiting.py -v

# Tests de middleware
python -m pytest tests/test_middleware.py -v
```

#### **Opciones de Testing**
```bash
# Tests con fallo rápido (útil para desarrollo)
python -m pytest --maxfail=3

# Tests con traceback corto
python -m pytest --tb=short

# Tests con marcadores específicos
python -m pytest -m "not slow"
python -m pytest -m "unit"
python -m pytest -m "integration"

# Tests paralelos (para CI/CD)
python -m pytest -n auto
```

### **Configuración de Tests**
El proyecto incluye configuración completa de pytest en `pyproject.toml`:
- **Cobertura mínima:** 90%
- **Reportes automáticos:** HTML, XML y terminal
- **Marcadores personalizados:** unit, integration, slow
- **Configuración asíncrona:** auto-detección de tests async

### **Estructura de Tests**
```
tests/
├── conftest.py                    # Configuración global de tests
├── fixtures.py                    # Fixtures compartidas
├── mock/                          # Mocks y stubs
├── test_*.py                      # Archivos de tests organizados por módulo
└── coverage/                      # Reportes de cobertura generados
```

### **Próximos Pasos de Testing**
1. **Aumentar cobertura** al objetivo del 90%
2. **Implementar tests de integración** para base de datos
3. **Agregar tests de performance** para rate limiting
4. **Completar tests de middleware** y validación
5. **Implementar tests de seguridad** para validaciones

## 🐳 Docker

### **Docker Files**

#### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

#### **docker-compose.yml (Production)**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
    depends_on:
      - postgres
      - redis
```

#### **docker-compose.dev.yml (Development)**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=true
    command: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Useful Docker Commands**
```bash
# Build image
docker build -t rebate-management-api .

# Run container
docker run -p 8000:8000 rebate-management-api

# View logs
docker logs <container_id>

# Execute commands in container
docker exec -it <container_id> bash
```

### **Docker and Dependencies**

The Dockerfile is configured to work with both dependency files:

- **Uses `requirements.txt`** for simple, fast builds
- **Can be modified** to use `pyproject.toml` for more complex setups
- **Both approaches** are supported in the container

To modify Dockerfile for pyproject.toml:
```dockerfile
# Instead of: COPY requirements.txt .
# Use: COPY pyproject.toml .
# And: RUN pip install -e ".[dev]"
```

## 🔧 Development

### **Linting and Formatting**

#### **Ruff Configuration**
```toml
[tool.ruff]
target-version = "py38"
line-length = 88

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
```

#### **Development Commands**

#### **Using pyproject.toml (Recommended)**
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Check code
ruff check .

# Format code
ruff format .

# Fix problems automatically
ruff check --fix .

# Run tests with coverage
python -m pytest --cov=app --cov-report=html
```

#### **Using requirements.txt (Alternative)**
```bash
# Install all dependencies
pip install -r requirements.txt

# Check code (if ruff is installed)
ruff check .

# Format code (if ruff is installed)
ruff format .

# Run tests
python -m pytest
```

#### **Synchronizing Dependencies**
```bash
# Update requirements.txt from pyproject.toml
pip install -e ".[dev]"
pip freeze > requirements.txt

# Or use pip-tools for better dependency resolution
pip install pip-tools
pip-compile pyproject.toml --output-file=requirements.txt --upgrade
```

### **Commit Structure**
```
feat: new functionality
fix: bug fix
docs: documentation
style: code formatting
refactor: refactoring
test: tests
chore: maintenance tasks
```

## 📈 Monitoring and Metrics

### **Rate Limiting Metrics**
- **Requests per second** per IP
- **Violations** per user/IP
- **Attack patterns** detected
- **Usage statistics** per endpoint

### **Health Checks**
- **Database** - PostgreSQL connection
- **Redis** - Cache availability
- **BigQuery** - Analytics connection
- **System** - Server resources

## 🚀 Deployment

### **Available Environments**
- **Development** - Local development
- **Staging** - Pre-production testing
- **Production** - Production

### **Variables by Environment**
```bash
# Development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=info

# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning
```

## 🤝 Contribution

### **Contribution Process**
1. **Fork** the project
2. **Create** feature branch (`feature/NewFeature`)
3. **Develop** changes following standards
4. **Run** tests and verify coverage
5. **Commit** with descriptive message
6. **Push** to branch
7. **Pull Request** with detailed description

### **Code Standards**
- **Type Hints** in all functions
- **Docstrings** in English for public functions
- **Tests** for new functionality
- **Minimum coverage** of 90%
- **Linting** without errors

## 📚 Additional Documentation

### **Configuration Files**
- `pyproject.toml` - Project configuration
- `pytest.ini` - Test configuration
- `requirements.txt` - Project dependencies
- `requirements-test.txt` - Testing dependencies

## 🔧 Troubleshooting

### **Common Installation Issues**

#### **pyproject.toml Issues**
```bash
# Error: "No module named 'setuptools'"
pip install --upgrade pip setuptools wheel

# Error: "Invalid project configuration"
# Verify pyproject.toml syntax with:
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Error: "Could not find a version that satisfies the requirement"
# Update pip and try again:
pip install --upgrade pip
pip install -e ".[dev]"
```

#### **requirements.txt Issues**
```bash
# Error: "Could not find a version that satisfies the requirement"
# Check if package exists:
pip index versions <package-name>

# Error: "Conflicting dependencies"
# Clear environment and reinstall:
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Error: "Permission denied"
# Use user installation:
pip install --user -r requirements.txt
```

#### **Dependency Conflicts**
```bash
# Check for conflicts
pip check

# View dependency tree
pip install pipdeptree
pipdeptree

# Resolve conflicts manually
pip install --upgrade <conflicting-package>
```

### **Environment Issues**
```bash
# Virtual environment not activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Wrong Python version
python --version  # Should be 3.11+
python3 --version  # Alternative command

# Path issues
echo $PATH  # Should include venv/bin
which python  # Should point to venv
```

### **Useful Scripts**
- `main.py` - Application entry point
- `create_stores_table.sql` - Table creation script
- `env.example` - Environment variables example

## 📄 License

This project is under the **MIT** license. See the `LICENSE` file for more details.

## 📞 Support

### **Team Contact**
- **Developers:** Tottus Perú Backend Team
- **Repository:** Internal Tottus GitLab
- **Documentation:** README.md and source code

### **Report Issues**
1. Verify it's not a duplicate issue
2. Provide environment information
3. Include logs and stack traces
4. Describe steps to reproduce

---

**Developed with ❤️ by the Tottus Perú Backend Team**