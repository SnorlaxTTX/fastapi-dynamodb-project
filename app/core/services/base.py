import uuid
from abc import ABC, abstractmethod
from fastapi import UploadFile

from boto3.dynamodb.conditions import Key
from app.core.exceptions import ErrorCode


class LogService(ABC):
    """
    Abstract base class for all logging services.
    Defines the interface for logging messages.
    """

    @abstractmethod
    def log(self, message: str):
        """
        Log a message.
        Should be implemented by concrete logging services.
        """
        pass


class FileService(ABC):
    """
    Abstract base class for FileService. This will define the interface
    for uploading and deleting files.
    """

    @abstractmethod
    def upload_file(self, file: UploadFile, key: str) -> str:
        """
        Upload a file to the respective storage (S3 or local).
        """
        pass

    @abstractmethod
    def delete_file(self, file_url: str):
        """
        Delete a file from the respective storage (S3 or local).
        """
        pass


class BaseService:
    def __init__(self, table, pk_prefix: str, service_name: str):
        self.table = table
        self.pk_prefix = pk_prefix
        self.service_name = service_name

    @staticmethod
    def generate_uuid() -> str:
        """
        Generate a unique UUID string.
        """
        return str(uuid.uuid4())

    @staticmethod
    def extract_uuid(key: str, prefix: str) -> str:
        """
        Extract UUID from a composite key with a given prefix.
        Example: "TASK#1234-5678" with prefix "TASK" => "1234-5678"
        """
        if key.startswith(prefix + "#"):
            return key.split("#", 1)[1]
        raise ValueError(f"Invalid key format: {key} does not start with prefix {prefix}#")

    async def create_item(self, identifier: str, sk: str, attributes: dict, pk_prefix=None):
        """
        Create a new item in the table.
        """
        if not pk_prefix:
            pk_prefix = self.pk_prefix
        item = {
            "PK": f"{pk_prefix}#{identifier}",
            "SK": sk,
            **attributes,
        }
        try:
            self.table.put_item(Item=item)
            return item
        except Exception as e:
            raise ErrorCode.BadRequest(str(e))

    async def get_items(self, identifier: str, sk_prefix: str, pk_prefix=None):
        """
        Query items by PK and SK prefix.
        """
        try:
            if not pk_prefix:
                pk_prefix = self.pk_prefix
            response = self.table.query(
                KeyConditionExpression=Key("PK").eq(f"{pk_prefix}#{identifier}")
                                       & Key("SK").begins_with(sk_prefix)
            )
            return response.get("Items", [])
        except Exception as e:
            raise ErrorCode.BadRequest(str(e))

    async def get_item(self, identifier: str, sk: str, pk_prefix=None, ignore_error=False):
        """
        Get an item by PK and SK.
        """
        if not pk_prefix:
            pk_prefix = self.pk_prefix

        key = {"PK": f"{pk_prefix}#{identifier}", "SK": sk}

        response = self.table.get_item(Key=key)

        if not ignore_error and "Item" not in response:
            raise ErrorCode.NotFound(self.service_name, identifier)
        return response.get("Item")

    async def get_all_meta(self):
        """
        Retrieve all meta records in the table where PK starts with the defined prefix
        and SK is 'META'.
        """
        try:
            response = self.table.scan(
                FilterExpression=Key("PK").begins_with(self.pk_prefix) & Key("SK").eq("META")
            )
            items = response.get("Items", [])
            return items
        except Exception as e:
            raise ErrorCode.BadRequest(str(e))

    async def update_item(self, identifier: str, sk: str, attributes: dict):
        """
        Update an existing item in the table.
        """
        key = {"PK": f"{self.pk_prefix}#{identifier}", "SK": sk}
        update_expression = "SET " + ", ".join(f"#{k}=:{k}" for k in attributes.keys())
        expression_attribute_names = {f"#{k}": k for k in attributes.keys()}
        expression_attribute_values = {f":{k}": v for k, v in attributes.items()}
        try:
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )
            return {"PK": key["PK"], "SK": key["SK"], **attributes}
        except Exception as e:
            raise ErrorCode.BadRequest(str(e))

    async def delete_item(self, identifier: str, sk: str, pk_prefix=None):
        """
        Delete an item by PK and SK.
        """
        if not pk_prefix:
            pk_prefix = self.pk_prefix

        key = {"PK": f"{pk_prefix}#{identifier}", "SK": sk}
        try:
            self.table.delete_item(Key=key)
        except Exception as e:
            raise ErrorCode.BadRequest(str(e))

    async def delete_items_by_sk_prefix(self, identifier: str, sk_prefix: str, pk_prefix=None):
        try:
            if not pk_prefix:
                pk_prefix = self.pk_prefix

            response = self.table.query(
                KeyConditionExpression=Key("PK").eq(f"{pk_prefix}#{identifier}")
                                       & Key("SK").begins_with(sk_prefix)
            )

            items = response.get("Items", [])
            if not items:
                return {"message": f"No items found with SK prefix '{sk_prefix}' for identifier '{identifier}'."}

            for item in items:
                self.table.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})

            return {"message": f"All items with SK prefix '{sk_prefix}' have been deleted."}
        except Exception as e:
            raise ErrorCode.BadRequest(f"Error deleting items: {str(e)}")
