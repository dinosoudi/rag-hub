# app/modules/documents/service.py
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.collections import service as collections_service
from .models import Document
from .schemas import DocumentCreate, DocumentUpdate

class DocumentNotFound(Exception): ...

async def create(session: AsyncSession, collection_id: uuid.UUID, data: DocumentCreate) -> Document:
    await collections_service.get(session, collection_id)  # lanza CollectionNotFound
    document = Document(collection_id=collection_id, **data.model_dump())
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document

async def list_by_collection(
    session: AsyncSession, collection_id: uuid.UUID, limit: int = 50, offset: int = 0
) -> list[Document]:
    await collections_service.get(session, collection_id)
    stmt = (
        select(Document)
        .where(Document.collection_id == collection_id)
        .order_by(Document.created_at)
        .limit(limit)
        .offset(offset)
    )
    result = await session.scalars(stmt)
    return list(result)

async def get(session: AsyncSession, document_id: uuid.UUID) -> Document:
    document = await session.get(Document, document_id)
    if document is None:
        raise DocumentNotFound(document_id)
    return document

async def update(session: AsyncSession, document_id: uuid.UUID, data: DocumentUpdate) -> Document:
    document = await get(session, document_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    await session.commit()
    await session.refresh(document)
    return document

async def delete(session: AsyncSession, document_id: uuid.UUID) -> None:
    document = await get(session, document_id)
    await session.delete(document)
    await session.commit()