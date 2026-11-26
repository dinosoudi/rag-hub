# app/modules/documents/router.py
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.modules.collections.service import CollectionNotFound
from . import service
from .schemas import DocumentCreate, DocumentRead, DocumentUpdate

router = APIRouter(tags=["documents"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post(
    "/collections/{collection_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(collection_id: uuid.UUID, data: DocumentCreate, session: SessionDep):
    try:
        return await service.create(session, collection_id, data)
    except CollectionNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found")

@router.get("/collections/{collection_id}/documents", response_model=list[DocumentRead])
async def list_documents(
    collection_id: uuid.UUID, session: SessionDep, limit: int = 50, offset: int = 0
):
    try:
        return await service.list_by_collection(session, collection_id, limit, offset)
    except CollectionNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found")

@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(document_id: uuid.UUID, session: SessionDep):
    try:
        return await service.get(session, document_id)
    except service.DocumentNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

@router.patch("/documents/{document_id}", response_model=DocumentRead)
async def update_document(document_id: uuid.UUID, data: DocumentUpdate, session: SessionDep):
    try:
        return await service.update(session, document_id, data)
    except service.DocumentNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: uuid.UUID, session: SessionDep):
    try:
        await service.delete(session, document_id)
    except service.DocumentNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)