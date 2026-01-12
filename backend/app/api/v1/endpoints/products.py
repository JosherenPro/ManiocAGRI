from typing import Any, List
import os
import uuid
import shutil
import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from api import deps
from core.db import get_session
from models.user import User
from models.product import Product, ProductCreate, ProductRead, ProductUpdate

router = APIRouter()

# Directory for storing product images
# From /backend/app/api/v1/endpoints/products.py -> go up to project root -> frontend/images/products
_current_file = os.path.abspath(__file__)  # /backend/app/api/v1/endpoints/products.py
_endpoints_dir = os.path.dirname(_current_file)  # /backend/app/api/v1/endpoints
_v1_dir = os.path.dirname(_endpoints_dir)  # /backend/app/api/v1
_api_dir = os.path.dirname(_v1_dir)  # /backend/app/api
_app_dir = os.path.dirname(_api_dir)  # /backend/app
_backend_dir = os.path.dirname(_app_dir)  # /backend
_project_root = os.path.dirname(_backend_dir)  # /projet tutoré
UPLOAD_DIR = os.path.join(_project_root, "frontend", "images", "products")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def download_image_from_url(url: str) -> str:
    """
    Download image from URL and save it to UPLOAD_DIR.
    Returns the relative path to the image.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            # Identify file extension from content-type or URL
            content_type = response.headers.get("content-type", "")
            if "image/jpeg" in content_type:
                ext = "jpg"
            elif "image/png" in content_type:
                ext = "png"
            elif "image/gif" in content_type:
                ext = "gif"
            elif "image/webp" in content_type:
                ext = "webp"
            else:
                ext = url.split(".")[-1].split("?")[0]
                if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                    ext = "jpg" # Default fallback
            
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(file_path, "wb") as f:
                f.write(response.content)
                
            return f"images/products/{unique_filename}"
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Impossible de télécharger l'image depuis l'URL: {str(e)}")

@router.get("/", response_model=List[ProductRead])
def read_products(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve products.
    """
    products = session.exec(select(Product).offset(skip).limit(limit)).all()
    return products

@router.get("/{id}", response_model=ProductRead)
def read_product(
    *,
    session: Session = Depends(get_session),
    id: int,
) -> Any:
    """
    Get product by ID.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductRead)
async def create_product(
    *,
    session: Session = Depends(get_session),
    product_in: ProductCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new product. Only for producers or admins.
    """
    if current_user.role not in ["producteur", "admin"]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check for duplicate product name
    existing_product = session.exec(select(Product).where(Product.name == product_in.name)).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Un produit avec ce nom existe déjà.")

    db_obj = Product.from_orm(product_in)
    
    # Handle image URL if provided as an external URL
    if db_obj.image_url and db_obj.image_url.startswith(("http://", "https://")):
        db_obj.image_url = await download_image_from_url(db_obj.image_url)
    
    db_obj.producer_id = current_user.id
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

@router.patch("/{id}", response_model=ProductRead)
async def update_product(
    *,
    session: Session = Depends(get_session),
    id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a product.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if current_user.role != "admin" and product.producer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    product_data = product_in.dict(exclude_unset=True)
    
    # Handle image URL if provided as an external URL
    if "image_url" in product_data and product_data["image_url"] and product_data["image_url"].startswith(("http://", "https://")):
        # Delete old image if it was local
        if product.image_url and not product.image_url.startswith(("http://", "https://")):
            old_image_name = product.image_url.split("/")[-1]
            old_image_path = os.path.join(UPLOAD_DIR, old_image_name)
            if os.path.exists(old_image_path):
                try:
                    os.remove(old_image_path)
                except:
                    pass
        
        product_data["image_url"] = await download_image_from_url(product_data["image_url"])
    
    for key, value in product_data.items():
        setattr(product, key, value)
    
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.delete("/{id}", response_model=ProductRead)
def delete_product(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a product.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if current_user.role != "admin" and product.producer_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    session.delete(product)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer ce produit car il est lié à des commandes."
        )
    return product


@router.post("/{id}/image", response_model=ProductRead)
async def upload_product_image(
    *,
    session: Session = Depends(get_session),
    id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload an image for a product.
    Admin, producteur, and gestionnaire can upload images.
    """
    # Check permissions - admin, producteur, gestionnaire
    if current_user.role not in ["admin", "gestionnaire", "producteur"]:
        raise HTTPException(
            status_code=403, 
            detail="Seuls les administrateurs, gestionnaires et producteurs peuvent ajouter des images"
        )
    
    # Get the product
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Validate file type
    allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp"]
    file_ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Type de fichier non autorisé. Extensions acceptées: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Delete old image if exists
    if product.image_url:
        old_image_name = product.image_url.split("/")[-1]
        old_image_path = os.path.join(UPLOAD_DIR, old_image_name)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
    
    # Save the new file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement: {str(e)}")
    finally:
        file.file.close()
    
    # Update product image_url
    product.image_url = f"images/products/{unique_filename}"
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product
