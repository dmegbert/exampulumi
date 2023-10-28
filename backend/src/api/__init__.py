from fastapi import APIRouter

from src.api import items

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])


@api_router.get("/hello")
def read_hello():
    return {"Hello": "World"}
