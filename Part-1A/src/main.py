from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.errors import setup_exception_handlers
from src.api.v1.expenses import router as expenses_router
from src.config import settings
from src.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables created
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

setup_exception_handlers(app)
app.include_router(expenses_router)
