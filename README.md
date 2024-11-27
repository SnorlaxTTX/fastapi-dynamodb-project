***Folder Structure***
````
.
├── app
│   ├── core
│   │   ├── __init__.py
│   │   ├── container.py           # Dependency injection container
│   │   ├── exceptions.py          # Custom error handling
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base service for shared functionality
│   │   │   └── files.py           # FileService for S3 or local file operations
│   ├── modules
│   │   ├── __init__.py
│   │   ├── v1                     # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── organizations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py      # API routes
│   │   │   │   ├── schemas     # Pydantic models for organizations, projects, tasks, users
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── organizations.py   
│   │   │   │   │   ├── projects.py        
│   │   │   │   │   ├── tasks.py           
│   │   │   │   │   └── users.py           
│   │   │   │   ├── services
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── organizations.py   # OrganizationService
│   │   │   │   │   ├── projects.py        # ProjectService
│   │   │   │   │   ├── tasks.py           # TaskService
│   │   │   │   │   └── users.py           # UserService
│   │   │   │   │
│   ├── main.py                  # Application entry point
│   ├── init_table.py            # Re-define table structure
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Dockerfile for FastAPI app
├── README.md                    # Documentation
└── .gitignore                   # Test folder for broader integration tests

