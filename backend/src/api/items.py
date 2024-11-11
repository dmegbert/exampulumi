import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src import crud
from src.models import ItemCreate, ItemRead, ItemUpdate

from src.api import deps

router = APIRouter()


@router.post("", response_model=ItemRead, status_code=201)
def create_item(
    *, db: Session = Depends(deps.get_session), item_in: ItemCreate
) -> ItemRead:
    item = crud.item.create(db=db, obj_in=ItemCreate(**item_in.model_dump()))
    return item


@router.get("", response_model=list[ItemRead])
def read_items(*, db: Session = Depends(deps.get_session)) -> list[ItemRead]:
    items = crud.item.get_multi(db=db)
    return items


@router.get("/{item_id}", response_model=ItemRead)
def read_item(
    *, db: Session = Depends(deps.get_session), item_id: uuid.UUID
) -> ItemRead:
    item = crud.item.get(db=db, id=item_id)
    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    *, db: Session = Depends(deps.get_session), item_id: uuid.UUID, item_in: ItemUpdate
) -> ItemRead:
    item = crud.item.get(db=db, id=item_id)
    item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(*, db: Session = Depends(deps.get_session), item_id: uuid.UUID) -> None:
    crud.item.delete(db=db, id=item_id)
    return None
