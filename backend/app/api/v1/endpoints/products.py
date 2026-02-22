import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.product import Product, ProductCreate, ProductRead, ProductUpdate
import os, uuid, shutil
import httpx

logger = logging.getLogger(__name__)
router = APIRouter()

# Directory for storing product images
_current_file = os.path.abspath(__file__)
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_file))))))
UPLOAD_DIR = os.path.join(_project_root, "frontend", "images", "products")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def download_image_from_url(url: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp"}
            ext = next((v for k, v in ext_map.items() if k in content_type), None)
            if not ext:
                ext = url.split(".")[-1].split("?")[0]
                if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                    ext = "jpg"
            filename = f"{uuid.uuid4().hex}.{ext}"
            with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
                f.write(response.content)
            return f"images/products/{filename}"
    except Exception as e:
        logger.error("Failed to download image from %s: %s", url, e)
        raise HTTPException(status_code=400, detail=f"Impossible de télécharger l'image: {e}")


@router.get("/search", response_model=List[ProductRead])
def search_products(
    session: Session = Depends(get_session),
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    in_stock: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """Full-text product search with filters — public."""
    statement = select(Product).where(Product.is_active == True)
    if q:
        statement = statement.where(
            Product.name.icontains(q) | Product.description.icontains(q)
        )
    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)
    if min_price is not None:
        statement = statement.where(Product.price >= min_price)
    if max_price is not None:
        statement = statement.where(Product.price <= max_price)
    if in_stock:
        statement = statement.where(Product.stock_quantity > 0)
    return session.exec(statement.offset(skip).limit(limit)).all()


@router.get("/", response_model=List[ProductRead])
def read_products(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> Any:
    """Retrieve products — public."""
    statement = select(Product)
    if active_only:
        statement = statement.where(Product.is_active == True)
    return session.exec(statement.offset(skip).limit(limit)).all()


@router.get("/{id}", response_model=ProductRead)
def read_product(*, session: Session = Depends(get_session), id: int) -> Any:
    """Get product by ID — public."""
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product


@router.post("/", response_model=ProductRead)
async def create_product(
    *,
    session: Session = Depends(get_session),
    product_in: ProductCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create new product. Producers or admins only."""
    if current_user.role not in ["producteur", "admin"]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")

    existing = session.exec(select(Product).where(Product.name == product_in.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un produit avec ce nom existe déjà")

    db_obj = Product.from_orm(product_in)
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
    """Update a product. Admin or owning producer."""
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    if current_user.role != "admin" and product.producer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")

    product_data = product_in.dict(exclude_unset=True)
    if "image_url" in product_data and product_data["image_url"] and product_data["image_url"].startswith(("http://", "https://")):
        if product.image_url and not product.image_url.startswith(("http://", "https://")):
            old_path = os.path.join(UPLOAD_DIR, product.image_url.split("/")[-1])
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
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
    """Delete a product. Admin or owning producer."""
    from sqlalchemy.exc import IntegrityError
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    if current_user.role != "admin" and product.producer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    session.delete(product)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Impossible de supprimer ce produit car il est lié à des commandes")
    return product


@router.post("/{id}/image", response_model=ProductRead)
async def upload_product_image(
    *,
    session: Session = Depends(get_session),
    id: int,
    file: Any = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Upload an image for a product. Admin, producteur, gestionnaire."""
    from fastapi import UploadFile, File
    if current_user.role not in ["admin", "gestionnaire", "producteur"]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    if not file:
        raise HTTPException(status_code=400, detail="Fichier requis")
    allowed = ["jpg", "jpeg", "png", "gif", "webp"]
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Extensions acceptées: {', '.join(allowed)}")
    filename = f"{uuid.uuid4().hex}.{ext}"
    if product.image_url:
        old_path = os.path.join(UPLOAD_DIR, product.image_url.split("/")[-1])
        if os.path.exists(old_path):
            os.remove(old_path)
    try:
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as buf:
            shutil.copyfileobj(file.file, buf)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'enregistrement: {e}")
    finally:
        file.file.close()
    product.image_url = f"images/products/{filename}"
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
