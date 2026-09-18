from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import backend, repository

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize repository during startup
    """
    await repository.repo.init_repo()
    yield

app = FastAPI()
# we use router here to allow modular backends for our api
app.include_router(backend.router)
