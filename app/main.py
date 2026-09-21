from contextlib import asynccontextmanager
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from nicegui import ui

from app import backend, frontend
from app.dependencies import repo


app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)


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
