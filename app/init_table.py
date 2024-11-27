import boto3
from botocore.exceptions import ClientError


def initialize_dynamodb_table(dynamodb_resource):
    """
    Initialize the DynamoDB table with the required schema.
    """
    table_name = "ManagerTable"
    try:
        # Check if the table already exists
        existing_tables = dynamodb_resource.meta.client.list_tables()["TableNames"]

        if table_name not in existing_tables:
            # Create the table
            dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "PK", "KeyType": "HASH"},  # Partition Key
                    {"AttributeName": "SK", "KeyType": "RANGE"},  # Sort Key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "PK", "AttributeType": "S"},
                    {"AttributeName": "SK", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",  # Use on-demand billing
            )
            print(f"Table '{table_name}' created successfully.")
        else:
            print(f"Table '{table_name}' already exists.")
    except ClientError as e:
        print(f"ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"Error initializing table: {e}")
