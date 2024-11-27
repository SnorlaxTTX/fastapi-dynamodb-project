from dependency_injector import containers, providers
import boto3
from dotenv import load_dotenv

from app.core.services.cloudwatch import CloudWatchService
from app.core.services.s3 import S3Service
from app.modules.v1.organizations.services import OrganizationService, ProjectService, TaskService, UserService

load_dotenv()


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Load configurations from environment variables
    config.enviroment.from_env("ENV", default="development")
    config.region_name.from_env("AWS_REGION", default="us-east-1")
    config.aws_access_key_id.from_env("AWS_ACCESS_KEY_ID", default="DUMMY")
    config.aws_secret_access_key.from_env("AWS_SECRET_ACCESS_KEY", default="DUMMY")
    config.endpoint_url.from_env("DYNAMODB_ENDPOINT_URL", default="http://dynamodb-local:8000")
    config.table_name.from_env("DYNAMODB_TABLE", default="ManagerTable")
    config.s3_bucket.from_env("AWS_S3_BUCKET", default=None)
    config.local_storage_dir.from_env("LOCAL_STORAGE_DIR", default="uploads")

    # S3 Client
    s3_client = providers.Singleton(
        boto3.client,
        service_name="s3",
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.region_name,
    ) if config.aws_access_key_id and config.aws_secret_access_key else None

    # File Service
    file_service = providers.Factory(
        S3Service,
        is_local=config.enviroment,
        s3_client=s3_client,
        bucket_name=config.s3_bucket,
        local_storage_dir=config.local_storage_dir,
    )
    # CloudWatch Service
    log_service = providers.Singleton(
        CloudWatchService,
        is_local=config.enviroment,
        region_name=config.region_name,
        log_group_name=config.cloudwatch_log_group_name,
        log_stream_name=config.cloudwatch_log_stream_name
    )

    # DynamoDB Resource
    dynamodb_resource = providers.Singleton(
        boto3.resource,
        service_name="dynamodb",
        region_name=config.region_name,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        endpoint_url=config.endpoint_url,
    )

    # DynamoDB Table
    dynamodb_table = providers.Factory(
        lambda dynamodb, table_name: dynamodb.Table(table_name),
        dynamodb=dynamodb_resource,
        table_name=config.table_name,
    )

    # Services
    user_service = providers.Factory(
        UserService,
        table=dynamodb_table,
        log_service=log_service,
    )
    task_service = providers.Factory(
        TaskService,
        table=dynamodb_table,
        file_service=file_service,
        user_service=user_service,
        log_service=log_service,
    )
    project_service = providers.Factory(
        ProjectService,
        table=dynamodb_table,
        file_service=file_service,
        task_service=task_service,
        log_service=log_service,
    )
    organization_service = providers.Factory(
        OrganizationService, table=dynamodb_table, file_service=file_service, project_service=project_service,
        log_service=log_service,
    )
