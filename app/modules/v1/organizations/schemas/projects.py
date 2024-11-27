from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, model_validator


class ProjectCreate(BaseModel):
    title: str
    description: str
    status: str


class ProjectResponse(BaseModel):
    # Set model configuration here using model_config (instead of Config)
    model_config = ConfigDict(populate_by_name=True)

    uuid: UUID = Field(..., alivalidation_aliasas="SK")
    title: str = Field(..., validation_alias="Title")
    description: str = Field(..., validation_alias="Description")
    status: str = Field(..., validation_alias="Status")
    create_at: Optional[datetime] = Field(None, validation_alias="CreatedAt")

    @model_validator(mode='before')
    def extract_fields(cls, values):
        """
        Extracts the actual 'uuid' from 'SK' and 'organization_uuid' from 'PK'.
        - 'SK' format: 'PROJECT#<uuid>' => Extracts '<uuid>'
        - 'PK' format: 'ORG#<organization_uuid>' => Extracts '<organization_uuid>'
        """
        # Extract uuid from SK
        sk_value = values.get("SK")
        if sk_value and sk_value.startswith("PROJECT#"):
            values["uuid"] = sk_value.split("#", 1)[1]  # Extract the portion after "PROJECT#"

        return values


class AddProjectUser(BaseModel):
    uuid: UUID
