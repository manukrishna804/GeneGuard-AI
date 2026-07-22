from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router
from app.core.config import settings



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

app.include_router(
    router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}"
    }