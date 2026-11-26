# app/main.py
from fastapi import FastAPI
from app.modules.collections.router import router as collections_router
from app.modules.documents.router import router as documents_router

app = FastAPI(title="RAG Hub")
app.include_router(collections_router)
app.include_router(documents_router)