# app/modules/collections/service.py
import uuid
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Collection
from .schemas import CollectionCreate, CollectionUpdate

class CollectionNotFound(Exception): ...
class CollectionNameTaken(Exception): ...

async def create(session: AsyncSession, data: CollectionCreate) -> Collection:
    collection = Collection(**data.model_dump())
    session.add(collection)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CollectionNameTaken(data.name)
    await session.refresh(collection)  # trae created_at generado por la DB
    return collection

async def get(session: AsyncSession, collection_id: uuid.UUID) -> Collection:
    collection = await session.get(Collection, collection_id)
    if collection is None:
        raise CollectionNotFound(collection_id)
    return collection

async def list_all(session: AsyncSession, limit: int = 50, offset: int = 0) -> list[Collection]:
    stmt = select(Collection).order_by(Collection.created_at).limit(limit).offset(offset)
    result = await session.scalars(stmt)
    return list(result)

async def update(session: AsyncSession, collection_id: uuid.UUID, data: CollectionUpdate) -> Collection:
    collection = await get(session, collection_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(collection, field, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CollectionNameTaken(data.name)
    await session.refresh(collection)
    return collection

async def delete(session: AsyncSession, collection_id: uuid.UUID) -> None:
    collection = await get(session, collection_id)
    await session.delete(collection)
    await session.commit()