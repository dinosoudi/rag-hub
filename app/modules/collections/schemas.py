# app/modules/collections/schemas.py
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None

class CollectionUpdate(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=100)
    description: str | None = None

class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime