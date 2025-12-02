"""FastAPI application entrypoint for the WarungGo AI service."""

from __future__ import annotations

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat

app = FastAPI(title="WarungGo AI Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize shared resources."""
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    # warmup_client removed


@app.on_event("shutdown")
def shutdown():
    pass

app.include_router(chat.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
