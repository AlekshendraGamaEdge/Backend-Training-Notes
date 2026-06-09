import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, cache
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=schemas.ItemResponse, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)

@router.get("/{item_id}", response_model=schemas.ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    cache_key = f"item:{item_id}"
    cached = cache.cache_get(cache_key)
    if cached:
        return cached

    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    item_dict = {"id": db_item.id, "name": db_item.name,
                 "description": db_item.description, "price": db_item.price}
    cache.cache_set(cache_key, item_dict)
    return db_item

@router.get("/", response_model=list[schemas.ItemResponse])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit)

@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(item_id: int, item_update: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db, item_id, item_update)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    cache.cache_delete(f"item:{item_id}")
    return db_item

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    cache.cache_delete(f"item:{item_id}")
    return None