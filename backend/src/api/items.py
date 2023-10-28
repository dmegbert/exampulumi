import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import crud
from src.api.schemas.item import ItemResponse
from src.models import ItemCreate

from src.api import deps

router = APIRouter()


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(*, db: Session = Depends(deps.get_db), item_in: ItemCreate) -> ItemResponse:
    item = crud.item.create(db=db, obj_in=ItemCreate(**item_in.dict()))
    return item


@router.get("", response_model=list[ItemResponse])
def read_items(*, db: Session = Depends(deps.get_db)) -> list[ItemResponse]:
    items = crud.item.get_multi(db=db)
    return items


@router.get("/{item_id}", response_model=ItemResponse)
def read_item(*, db: Session = Depends(deps.get_db), item_id: uuid.UUID) -> ItemResponse:
    item = crud.item.get(db=db, id=item_id)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(*, db: Session = Depends(deps.get_db), item_id: uuid.UUID) -> None:
    crud.item.delete(db=db, id=item_id)
    return None
