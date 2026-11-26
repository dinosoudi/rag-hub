# app/modules/documents/schemas.py
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from .models import DocumentStatus

class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)

class DocumentUpdate(BaseModel):
    title: str = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)

class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    collection_id: uuid.UUID
    title: str
    content: str
    status: DocumentStatus
    created_at: datetime