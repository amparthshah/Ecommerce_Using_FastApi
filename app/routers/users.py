from .. import models, utils, database, schemas, oauth2
from fastapi import status, Depends, APIRouter, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List


router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/customer", status_code=status.HTTP_201_CREATED, response_model=schemas.CustomerOut)
def create_customer(user: schemas.CustomerCreate, db: Session = Depends(get_db), current_user: Session = Depends(oauth2.get_current_user)):
    new_customer = models.Customer(user_id = current_user.id  ,**user.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer
    
@router.get("/customer", response_model=List[schemas.CustomerOut])
def get_customers(db: Session = Depends(get_db), current_user: Session = Depends(oauth2.get_current_user)):
    get_customer = db.query( models.Customer).filter(models.Customer.user_id == current_user.id).all()
    if not get_customer:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No customer's found for logged in user")
    return get_customer

@router.delete("/customer/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: int, db: Session = Depends(get_db), current_user: Session = Depends(oauth2.get_current_user)):
    customer_delete = db.query(models.Customer).filter(models.Customer.user_id == current_user.id, models.Customer.id == id)
    if not customer_delete.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with {id} as ID not found")
    customer_delete.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)