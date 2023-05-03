from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

# -----------------------------------------User's Schema----------------------------------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    @validator('email')
    def email_to_lowercase(cls, v):
        return v.lower()
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    name: str
    email : EmailStr
    created_at : datetime
    
    class Config:
        orm_mode = True
        
# -----------------------------------------Products's Schema----------------------------------------------------

class ProductBase(BaseModel):
    title: str
    description: str
    price: float

class ProductCreate(ProductBase):
    image: str

class ProductOut(ProductBase):
    id: int
    image: str

    class Config:
        orm_mode = True

class ProductUpdate(BaseModel):
    title: str = None
    description: str = None
    price: float = None
    image: str = None

# -----------------------------------------Cart's Schema----------------------------------------------------

class CartBase(BaseModel):
    product_id: int
    quantity: int

class CartCreate(CartBase):
    pass

class Cart(CartBase):
    user_id: int
    total: float
    pass
    class Config:
        orm_mode = True

# -----------------------------------------Tokens's Schema----------------------------------------------------

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    contact: str
    address: str
    
    @validator('email','address')
    def email_to_lowercase(cls, v):
        return v.lower()

class CustomerCreate(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int
    user_id: int
    pass
    class Config:
        orm_mode = True

# -----------------------------------------Checkout's Schema----------------------------------------------------

class CheckoutBase(BaseModel):
    customer_id: int

class CheckoutCreate(CheckoutBase):
    pass

class CheckoutOut(CheckoutBase):
    id: int
    user_id: int
    customer_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# -----------------------------------------Tokens's Schema----------------------------------------------------

# Token Schema for validation if user is logged in or not or if valid user is performing opreation or not

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None