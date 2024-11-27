from pydantic import BaseModel, Field, ConfigDict, model_validator, HttpUrl
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import UploadFile, Form, File


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    deadline: datetime
    file: UploadFile | None

    @classmethod
    def as_form(
            cls,
            title: str = Form(...),
            description: str = Form(...),
            priority: str = Form(...),
            deadline: datetime = Form(...),
            file: Optional[UploadFile] = File(None),
    ):
        return cls(
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            file=file,
        )


class TaskResponse(BaseModel):
    # Set model configuration here using model_config (instead of Config)
    model_config = ConfigDict(populate_by_name=True)

    uuid: UUID = Field(..., alivalidation_aliasas="SK")
    title: str = Field(..., validation_alias="Description")
    description: str = Field(..., validation_alias="Description")
    deadline: Optional[datetime] = Field(None, validation_alias="Deadline")
    priority: Optional[str] = Field(None, validation_alias="Priority")
    file_url: Optional[str] = Field(None, validation_alias="FileUrl")

    # Use a model_validator to extract uuid and project_uuid if needed
    @model_validator(mode="before")
    def extract_fields(cls, values):
        """
        Extracts the actual uuid from 'SK' and project_uuid from 'PK'.
        - 'SK' format: 'TASK#<uuid>' => Extracts '<uuid>'
        - 'PK' format: 'PROJECT#<project_uuid>' => Extracts '<project_uuid>'
        """
        # Extract uuid from SK (e.g., TASK#<uuid> => <uuid>)
        sk_value = values.get("SK")
        if sk_value and sk_value.startswith("TASK#"):
            values["uuid"] = sk_value.split("#", 1)[1]  # Extract the portion after "TASK#"

        return values


class AddTaskUser(BaseModel):
    uuid: UUID
