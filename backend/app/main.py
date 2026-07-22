from fastapi import FastAPI

from app.api.v1.router import router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
)

app.include_router(
    router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/")
def root():
    return {"message": "Welcome to GeneGuard API"}