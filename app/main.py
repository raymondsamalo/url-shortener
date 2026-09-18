from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import backend
from app.dependencies import repo

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize repository during startup
    """
    await repo.init_repo()
    yield

app = FastAPI(lifespan=lifespan)
# we use router here to allow modular backends for our api
app.include_router(backend.router)
