import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src import crud
from src.api.schemas.item import ItemResponse, ItemRequestCreate, ItemRequestUpdate

from src.api import deps

router = APIRouter()


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(
    *, db: Session = Depends(deps.get_session), item_in: ItemRequestCreate
) -> ItemResponse:
    item = crud.item.create(db=db, obj_in=ItemRequestCreate(**item_in.model_dump()))
    return item


@router.get("", response_model=list[ItemResponse])
def read_items(*, db: Session = Depends(deps.get_session)) -> list[ItemResponse]:
    items = crud.item.get_multi(db=db)
    return items


@router.get("/{item_id}", response_model=ItemResponse)
def read_item(
    *, db: Session = Depends(deps.get_session), item_id: uuid.UUID
) -> ItemResponse:
    item = crud.item.get(db=db, id=item_id)
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
def update_item(
    *,
    db: Session = Depends(deps.get_session),
    item_id: uuid.UUID,
    item_in: ItemRequestUpdate
) -> ItemResponse:
    item = crud.item.get(db=db, id=item_id)
    item = crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(*, db: Session = Depends(deps.get_session), item_id: uuid.UUID) -> None:
    crud.item.delete(db=db, id=item_id)
    return None
