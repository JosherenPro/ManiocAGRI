from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api import deps
from core.db import get_session
from models.user import User
from models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter()


@router.get("/", response_model=List[CategoryRead])
def read_categories(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all categories — public endpoint."""
    cats = session.exec(
        select(Category).where(Category.is_active == True).offset(skip).limit(limit)
    ).all()
    return cats


@router.get("/{id}", response_model=CategoryRead)
def read_category(*, session: Session = Depends(get_session), id: int) -> Any:
    """Get a single category by ID — public."""
    cat = session.get(Category, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return cat


@router.post("/", response_model=CategoryRead)
def create_category(
    *,
    session: Session = Depends(get_session),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Create a new category. Admin only."""
    existing = session.exec(
        select(Category).where(Category.slug == category_in.slug)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce slug existe déjà")
    db_cat = Category.from_orm(category_in)
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return db_cat


@router.patch("/{id}", response_model=CategoryRead)
def update_category(
    *,
    session: Session = Depends(get_session),
    id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Update a category. Admin only."""
    cat = session.get(Category, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    for key, value in category_in.dict(exclude_unset=True).items():
        setattr(cat, key, value)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.delete("/{id}", response_model=CategoryRead)
def delete_category(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Delete a category. Admin only."""
    cat = session.get(Category, id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    session.delete(cat)
    session.commit()
    return cat
