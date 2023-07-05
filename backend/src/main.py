import uuid
from typing import Union

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic.main import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.utils import service_logging

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Request-ID"],
)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": exc.__str__()})


@app.middleware("http")
async def log_aws_request(request: Request, call_next):
    service_logging.log_request(request)
    response = await call_next(request)
    return response


class Item(BaseModel):
    title: str
    description: str


class ItemResponse(Item):
    id: uuid.UUID


router = APIRouter()


@router.get("/hello")
def read_hello():
    return {"Hello": "World"}


@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@router.post("/items", response_model=ItemResponse, status_code=201)
def create_item(*, item: Item):
    return ItemResponse(
        **item.dict(),
        id=uuid.uuid4(),
    )


app.include_router(router=router, prefix="/api")
