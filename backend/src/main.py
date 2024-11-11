from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from sqlalchemy.exc import IntegrityError

from src.api import api_router
from src.utils import service_logging
from src.utils.exception_handling import (
    validation_exception_handler,
    integrity_error_handler,
)

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Request-ID"],
)

# Register the custom exception handler
app.exception_handler(RequestValidationError)(validation_exception_handler)
app.exception_handler(ResponseValidationError)(validation_exception_handler)
app.exception_handler(IntegrityError)(integrity_error_handler)


@app.middleware("http")
async def log_aws_request(request: Request, call_next):
    service_logging.log_request(request)
    response = await call_next(request)
    return response


app.include_router(router=api_router, prefix="/api")
