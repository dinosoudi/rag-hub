# app/modules/collections/router.py
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from . import service
from .schemas import CollectionCreate, CollectionRead, CollectionUpdate

router = APIRouter(prefix="/collections", tags=["collections"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_collection(data: CollectionCreate, session: SessionDep):
    try:
        return await service.create(session, data)
    except service.CollectionNameTaken:
        raise HTTPException(status.HTTP_409_CONFLICT, "Collection name already exists")

@router.get("", response_model=list[CollectionRead])
async def list_collections(session: SessionDep, limit: int = 50, offset: int = 0):
    return await service.list_all(session, limit, offset)

@router.get("/{collection_id}", response_model=CollectionRead)
async def get_collection(collection_id: uuid.UUID, session: SessionDep):
    try:
        return await service.get(session, collection_id)
    except service.CollectionNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found")

@router.patch("/{collection_id}", response_model=CollectionRead)
async def update_collection(collection_id: uuid.UUID, data: CollectionUpdate, session: SessionDep):
    try:
        return await service.update(session, collection_id, data)
    except service.CollectionNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found")
    except service.CollectionNameTaken:
        raise HTTPException(status.HTTP_409_CONFLICT, "Collection name already exists")

@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(collection_id: uuid.UUID, session: SessionDep):
    try:
        await service.delete(session, collection_id)
    except service.CollectionNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)