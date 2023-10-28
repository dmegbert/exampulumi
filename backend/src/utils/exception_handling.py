from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.__str__()})


def integrity_error_handler(reqeust: Request, exc: IntegrityError):
    key, value = parse_integrity_error(exc)
    if key and value:
        detail_msg = f"The {key} '{value}' already exists. Please create a unique {key}"
    else:
        detail_msg = "Unknown IntegrityError"
    return JSONResponse(status_code=400, content={"detail": detail_msg})


def parse_integrity_error(exc: IntegrityError):
    message = exc.orig.pgerror
    key = None
    value = None

    if 'duplicate key' in message:
        key = message.split('Key (', 1)[1].split(')=', 1)[0]
        value = message.split(')=(', 1)[1].split(') ', 1)[0]

    return key, value
