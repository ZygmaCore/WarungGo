"""FastAPI application entrypoint for the WarungGo AI service."""

from __future__ import annotations

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, faq, invoice, order, promo
from utils.llm_client import reset_client, warmup_client

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
    warmup_client()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Gracefully close shared resources."""

    http_client: httpx.AsyncClient | None = getattr(app.state, "http_client", None)
    if http_client:
        await http_client.aclose()
    reset_client()


app.include_router(order.router)
app.include_router(faq.router)
app.include_router(invoice.router)
app.include_router(promo.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check() -> dict:
    """Simple health check endpoint."""

    return {"status": "ok"}
