from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, model_validator


class UserCreate(BaseModel):
    name: str
    email: str
    role: str


class UserResponse(BaseModel):
    # Set model configuration here using model_config (instead of Config)
    model_config = ConfigDict(populate_by_name=True)

    uuid: UUID = Field(..., alivalidation_aliasas="SK")
    name: str = Field(..., validation_alias="Name")
    email: str = Field(..., validation_alias="Email")
    role: str = Field(..., validation_alias="Role")
    create_at: Optional[datetime] = Field(None, validation_alias="CreatedAt")

    @model_validator(mode='before')
    def extract_fields(cls, values):
        """
        Extracts the actual 'user_uuid' from 'SK' and 'organization_uuid' from 'PK'.
        - 'SK' format: 'USER#<user_uuid>' => Extracts '<user_uuid>'
        - 'PK' format: 'ORG#<organization_uuid>' => Extracts '<organization_uuid>'
        """
        # Extract user_uuid from SK
        sk_value = values.get("SK")
        if sk_value and sk_value.startswith("USER#"):
            values["uuid"] = sk_value.split("#", 1)[1]  # Extract the portion after "USER#"

        return values
