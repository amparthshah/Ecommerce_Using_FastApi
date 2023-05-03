import shutil
from .. import models, utils, schemas, database, oauth2
from fastapi import status, Depends, APIRouter, HTTPException, Response, File, UploadFile, Form
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
import uuid
import os
from typing import Optional
from ..oauth2 import get_current_user


router = APIRouter(
    prefix='/cart',
    tags=['Cart']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Cart)
async def create_cart(cart: schemas.CartCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id==cart.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No such product with {cart.product_id} found in the database')
    
    if cart.quantity<1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Quantity for the product must be greater than 0')
    
    cart_item = db.query(models.Cart).filter(models.Cart.user_id==current_user.id, models.Cart.product_id==cart.product_id).first()
    if cart_item:
        cart_item.quantity += cart.quantity
        new_cart = cart_item
    else:
        new_cart = models.Cart(user_id=current_user.id, **cart.dict())
        db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    # Update the total field
    new_cart.total = new_cart.calculate_total
    db.commit()

    return new_cart

@router.get("/", response_model=List[schemas.Cart])
def get_user_cart(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    cart_query = db.query(models.Cart).filter(models.Cart.user_id==current_user.id).all()
    if not cart_query:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Cart Empty")
    return cart_query

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    cart_item = db.query(models.Cart).filter(models.Cart.id==id, models.Cart.user_id==current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Cart item with {id} as ID not found OR Cart is empty')
    db.delete(cart_item)
    db.commit()
