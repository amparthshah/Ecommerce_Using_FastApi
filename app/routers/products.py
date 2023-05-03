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
    prefix='/products',
    tags=['Products']
)

def save_uploaded_file(uploaded_file: UploadFile) -> str:
    # Check if image is valid
    if uploaded_file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Invalid image file type. Only JPEG and PNG are supported.")
        
    # Save the image to disk
    unique_id = uuid.uuid4()
    extension = os.path.splitext(uploaded_file.filename)[1]
    file_name = f"{unique_id}{extension}"
    file_path = os.path.join("static/images", file_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    return file_path

@router.get("/", response_model=List[schemas.ProductOut])
async def get_all_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    product_list = []
    for product in products:
        product_dict = product.__dict__
        product_dict["image"] = "http://localhost:8000/{}".format(product_dict['image'].replace('\\', '/'))
        product_list.append(product_dict)
    return product_list

# Define route to get list of all products
@router.get("/{product_id}", response_model=schemas.ProductOut)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_dict = product.__dict__
    product_dict["image"] = "http://localhost:8000/{}".format(product_dict['image'].replace('\\', '/'))
    return product_dict

async def create_product_form():
    return """
        <html>
            <body>
                <form method="post" enctype="multipart/form-data">
                    <label>Title:</label><input type="text" name="title" required><br>
                    <label>Description:</label><input type="text" name="description" required><br>
                    <label>Price:</label><input type="number" step="0.01" name="price" required><br>
                    <label>Image:</label><input type="file" name="image" required><br>
                    <button type="submit">Create Product</button>
                </form>
            </body>
        </html>
    """

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductOut)
async def create_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    print(current_user.id)
    # Check if user has permission to create a product
    user_role = db.query(models.UserRoles).filter(models.UserRoles.id == current_user.user_role).first()
    if user_role is None or user_role.id not in [1, 2]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have permission to create a product")

    # Save the uploaded image to the server
    file_path = save_uploaded_file(image)

    # Create product in the database
    product = schemas.ProductCreate(
        title=title,
        description=description,
        price=price,
        image=file_path,
    )
    db_product = models.Product(user_id=current_user.id, **product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

@router.patch("/{product_id}", response_model=schemas.ProductOut)
async def update_product(
    product_id: int, 
    title: Optional[str] = Form(None), 
    description: Optional[str] = Form(None), 
    price: Optional[float] = Form(None), 
    image: Optional[UploadFile] = File(None), 
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    # Check if the current user is authorized to update products
    user_role = db.query(models.UserRoles).filter(models.UserRoles.id == current_user.user_role).first()
    if user_role is None or user_role.id not in [1, 2]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have permission to create a product")
        
    # Find the product in the database
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Update the product with any provided fields
    if title:
        product.title = title
    if description:
        product.description = description
    if price:
        product.price = price
    if image:
        # Save the uploaded image to the server
        file_path = save_uploaded_file(image)
        # Update the image path in the database
        product.image = file_path
        
    # Commit the changes to the database and refresh the product object
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prooduct(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Check if user has rights to delete or not
    user_role = db.query(models.UserRoles).filter(models.UserRoles.id == current_user.user_role).first()
    if user_role is None or user_role.id not in [1, 2]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have permission to delete a product")
    product_delete = db.query(models.Product).filter(models.Product.id == id)
    product = product_delete.first()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id as {id} does not exist")
    product_delete.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)