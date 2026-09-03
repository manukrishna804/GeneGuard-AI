from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.router import router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

# Allow the React/Vite frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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