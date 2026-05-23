"""
Multi-Tenant AI Platform - Main Application Entry Point
"""
from fastapi import FastAPI
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import init_app_logging, get_logger

# Import routers from all modules
from app.modules.tenants.router import router as tenants_router
from app.modules.knowledge.router import router as knowledge_router
from app.modules.engine.router import router as engine_router

# Initialize logging
init_app_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Multi-Tenant AI Platform",
    version="2.0",
    description="RAG-powered multi-tenant chat application with document knowledge base"
)

# Register global exception handlers
register_exception_handlers(app)

# Register routers
app.include_router(tenants_router)
app.include_router(knowledge_router)
app.include_router(engine_router)


@app.on_event("startup")
def on_startup():
    """Initialize database on application startup."""
    logger.info("Starting Multi-Tenant AI Platform...")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
def root():
    """Root endpoint for health check."""
    return {
        "status": "healthy",
        "service": "Multi-Tenant AI Platform",
        "version": "2.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
