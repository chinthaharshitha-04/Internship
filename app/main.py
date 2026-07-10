"""Application entrypoint.

Wires together configuration, database initialization, middleware,
global exception handlers, and every API router into a single FastAPI
app instance.

Run locally with:

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import cart, customer, discount, product, promotion
from app.core.config import get_settings
from app.core.database import init_db
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import register_middleware
from app.utils.logger import configure_logging

settings = get_settings()
logger = configure_logging(debug=settings.debug)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan hook: creates database tables on startup.

    Using SQLAlchemy's ``create_all`` here (rather than a separate
    migration step) keeps the project simple for local/dev use with
    SQLite, per the assignment's tech stack.
    """

    logger.info("Starting %s...", settings.app_name)
    init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down %s.", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description=(
        "A production-quality Retail Discount Engine supporting percentage, "
        "flat, buy-X-get-Y, category, customer-tier, and coupon discounts, "
        "with priority-based and stackable promotion resolution."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

register_middleware(app)
register_exception_handlers(app)

app.include_router(customer.router, prefix=settings.api_v1_prefix)
app.include_router(product.router, prefix=settings.api_v1_prefix)
app.include_router(discount.router, prefix=settings.api_v1_prefix)
app.include_router(promotion.router, prefix=settings.api_v1_prefix)
app.include_router(cart.router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    """Simple liveness/health-check endpoint."""

    return {"status": "ok", "service": settings.app_name}
