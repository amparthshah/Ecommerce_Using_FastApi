from .. import models, schemas, oauth2
from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter(
    prefix='/checkout',
    tags=['Checkout']
)

@router.post("/")
def create_order(checkout_data: schemas.CheckoutCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Check if the customer belongs to the current user
    customer = db.query(models.Customer).filter_by(id=checkout_data.customer_id, user_id=current_user.id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found or does not belong to current user")

    # Check if the customer has any order in cart
    cart_items = db.query(models.Cart).filter_by(user_id=current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found in cart")

    # Create a new order with the user's ID and the given customer ID
    new_order = models.Order(user_id=current_user.id, **checkout_data.dict())
    new_order.customer_id = checkout_data.customer_id
    db.add(new_order)
    db.commit()

    # Loop through the cart items and create a new OrderItem for each item
    for cart_item in cart_items:
        product = cart_item.product
        order_item = models.OrderItem(order_id=new_order.id, product_id=product.id, quantity=cart_item.quantity, price=product.price)
        db.add(order_item)

    # Add each OrderItem to the new Order and commit the transaction
    db.commit()

    # Delete the Cart items for the logged-in user
    db.query(models.Cart).filter_by(user_id=current_user.id).delete()
    db.commit()

    return {"message": "Order created successfully"}