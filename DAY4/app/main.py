import logging
from fastapi import FastAPI
from app.database import init_db
from app.routers import items

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="CRUD with Redis Cache")

# Initialize database
init_db()

# Include routers
app.include_router(items.router)

@app.on_event("startup")
def startup():
    logger.info("Starting up FastAPI application")

@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down FastAPI application")