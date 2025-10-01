project/
│
├── app/
│   ├── main.py                      # Punto de entrada
│   │
│   ├── application/                # Casos de uso (orquestación)
│   │   └── use_cases/
│   │       └── register_user.py
│   │
│   ├── domain/                      # Lógica de negocio pura
│   │   ├── models/                  # Entidad de negocio (sin SQLAlchemy / Pydantic)
│   │   │   └── user.py            
│   │   ├── repositories/           # Interfaces (abstractas)
│   │   │   └── user_repository.py
│   │   └── services/               #  Application layer
│   │       └── user_service.py
│   │
│   ├── infrastructure/             # Implementaciones técnicas
│   │   ├── db/                     # Configuración de base de datos
│   │   │   ├── models/             # Entidad ORM (SQLAlchemy)
│   │   │   │   ├── core/                 
│   │   │   │   └── tottus/              
│   │   │   │       └── user_model.py
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   ├── bigquery/
│   │   │   └── client.py
│   │   ├── repositories/           # Repositorios concretos
│   │   │   └── user_repository_impl.py
│   │   └── mappers/                # Si fuera Necesario para Entidad => Entidad ORM  (Ejemplo DataClass o asdict )
│   │       └── user_mapper.py
│   │
│   ├── interfaces/                # Adaptadores externos
│   │   ├── api/                         # Interfaces (controllers / routers) HTTP (FastAPI)
│   │   │   ├── controllers/             # controllers  
│   │   │   │   └── user_controller.py
│   │   │   └── routers/                 # routers 
│   │   │       │── router_config.py
│   │   │       └── router_factory.py 
│   │   └── schemas/                    # DTOs (Pydantic)
│   │       ├── requests/     # Datos que entran (UserCreate, LoginRequest)
│   │       └── responses/    # Datos que salen (UserResponse, TokenResponse)
│   │
│   ├── core/                       # Config global (settings, logging)
│   │   ├── middleware/             # Middlewares  (Por definir si es Global , Específico o técnico)
│   │   ├── dependencies/           # Si Maneja dependencias, sino excluir (*)
│   │   │   ├── db.py              # Sesión de base de datos
│   │   │   ├── auth.py            # Validación de usuario autenticado
│   │   │   └── config.py          # Acceso a settings globales
│   │   ├── config.py              # Variables de entorno y settings
│   │   ├── security.py            # Configuración de JWT  ( ejemplo )
│   │   ├── database.py            # Inicialización de SQLAlchemy
│   │   └── bigquery.py            # Cliente BigQuery 
│   │
│   └── utils/                      # Funciones auxiliares
│       └── hashing.py
│
├── tests/                          # Pruebas unitarias
│   └── test_user.py
│
├── requirements.txt
└── README.md