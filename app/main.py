from fastapi import FastAPI
from nicegui import app as nicegui_app
from nicegui import ui
from contextlib import asynccontextmanager
from app import backend, frontend
from app.dependencies import repo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize repository during startup
    """
    await repo.init_repo()
    yield

fastapi_app = FastAPI(lifespan=lifespan)
# we use router here to allow modular backends for our api

ui.run_with(fastapi_app, mount_path="/ui", root=frontend.main_page)
fastapi_app.include_router(backend.router)
