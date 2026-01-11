"""FastAPI application for the Dragonfly Agent Framework.

Run with: uvicorn dragonfly.service.api.main:app --reload
"""

from fastapi import FastAPI

from dragonfly.service.api.routes import router

app = FastAPI(
    title="Dragonfly Agent Framework",
    description="Multi-perspective decision-making agent framework",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "name": "Dragonfly Agent Framework",
        "version": "0.1.0",
        "docs": "/docs",
    }
