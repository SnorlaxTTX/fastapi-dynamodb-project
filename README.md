# 

## Overview
This project manages organizations, projects, tasks, and users with a robust set of API routes. It leverages FastAPI for the backend and supports file management via AWS S3 or local storage. The project also includes an integrated DynamoDB instance for local testing and cloud-based services.

### Requirements
    Python 3.7+
    Docker & Docker Compose
    AWS Services: S3, Cloudwatch
    DynamoDB Local (automatically started via Docker)

### Docker Compose
To get the project up and running with Docker Compose, follow these steps:

***Start the Services***

Run the following command to start the services (FastAPI, DynamoDB Local, etc.):
```
docker-compose up --build
```
    
This command will:
+ Build the Docker images.
+ Start the FastAPI application along with DynamoDB Local (using docker-compose).
+ Automatically set up the necessary local storage and services.
+ Once the containers are up, FastAPI will be available at http://localhost:8000.

***Stop the Services***

To stop the running services, press Ctrl + C or run:

```
docker-compose down
```


### Folder Structure
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
│   │   │   ├── cloudwatch.py      # LogService for Cloudwatch or local logging operations
│   │   │   └── s3.py              # FileService for S3 or local file operations
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

