import os

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.container import Container
from app.exceptions import StandardException
from app.modules.v1.organizations.router import router as org_router
from app.init_table import initialize_dynamodb_table


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI()

    # Ensure the 'uploads' directory exists
    local_storage_dir = "uploads"
    os.makedirs(local_storage_dir, exist_ok=True)

    # Mount the static files directory
    app.mount("/static/uploads", StaticFiles(directory=local_storage_dir), name="static")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    # Dependency Injection Container
    container = Container()
    container.config.region_name.from_env("AWS_REGION", default="us-east-1")
    container.config.table_name.from_env("DYNAMODB_TABLE", default="ManagerTable")
    container.wire(modules=[
        "app.modules.v1.organizations.router",
    ])
    app.container = container

    # Include Routers
    app.include_router(org_router, prefix="/organizations", tags=["Organizations"])

    # Initialize DynamoDB Table on Startup
    @app.on_event("startup")
    async def on_startup():
        """
        Event triggered when the application starts.
        Initializes the DynamoDB table with required structure and GSIs.
        """
        initialize_dynamodb_table(container.dynamodb_resource())

    return app


# Create an instance of the FastAPI app
app = create_app()

