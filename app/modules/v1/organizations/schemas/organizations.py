from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class OrganizationCreate(BaseModel):
    name: str
    description: str


class OrganizationResponse(BaseModel):
    # Set model configuration here using model_config (instead of Config)
    model_config = ConfigDict(populate_by_name=True)

    uuid: UUID = Field(..., alivalidation_aliasas="PK")
    name: str = Field(..., validation_alias="Name")
    description: str = Field(..., validation_alias="Description")
    create_at: Optional[datetime] = Field(None, validation_alias="CreatedAt")

    @model_validator(mode='before')
    def extract_id(cls, values):
        """
        Extracts the actual 'uuid' from the 'PK' field (e.g., 'ORG#12345' -> '12345').
        """
        pk_value = values.get("PK")
        if pk_value and pk_value.startswith("ORG#"):
            values["uuid"] = pk_value.split("#", 1)[1]
        return values
