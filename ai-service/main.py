"""FastAPI application entrypoint for the WarungGo AI service."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import faq, invoice, order, promo

app = FastAPI(title="WarungGo AI Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(order.router)
app.include_router(faq.router)
app.include_router(invoice.router)
app.include_router(promo.router)


@app.get("/health")
async def health_check() -> dict:
    """Simple health check endpoint."""

    return {"status": "ok"}
