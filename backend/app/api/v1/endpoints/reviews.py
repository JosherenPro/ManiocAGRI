from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from api import deps
from core.db import get_session
from models.user import User
from models.review import ProductReview, ProductReviewCreate, ProductReviewRead
from models.product import Product

router = APIRouter()


@router.get("/", response_model=List[ProductReviewRead])
def read_reviews(
    session: Session = Depends(get_session),
    product_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """List product reviews. Filter by product_id — public."""
    statement = select(ProductReview)
    if product_id:
        statement = statement.where(ProductReview.product_id == product_id)
    statement = statement.order_by(ProductReview.created_at.desc()).offset(skip).limit(limit)
    return session.exec(statement).all()


@router.get("/product/{product_id}/stats")
def get_product_review_stats(
    product_id: int,
    session: Session = Depends(get_session),
) -> Any:
    """Get average rating and count for a product — public."""
    count = session.exec(
        select(func.count(ProductReview.id)).where(ProductReview.product_id == product_id)
    ).one()
    avg = session.exec(
        select(func.avg(ProductReview.rating)).where(ProductReview.product_id == product_id)
    ).one()
    return {
        "product_id": product_id,
        "review_count": count,
        "average_rating": round(float(avg), 1) if avg else None,
    }


@router.post("/", response_model=ProductReviewRead)
def create_review(
    *,
    session: Session = Depends(get_session),
    review_in: ProductReviewCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Submit a product review. Clients only; one review per product per client."""
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Seuls les clients peuvent laisser un avis")

    # Check product exists
    product = session.get(Product, review_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # One review per product per client
    existing = session.exec(
        select(ProductReview)
        .where(ProductReview.product_id == review_in.product_id)
        .where(ProductReview.client_id == current_user.id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez déjà laissé un avis pour ce produit")

    db_review = ProductReview(
        product_id=review_in.product_id,
        client_id=current_user.id,
        rating=review_in.rating,
        comment=review_in.comment,
    )
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review


@router.delete("/{id}")
def delete_review(
    *,
    session: Session = Depends(get_session),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a review. Only the author or an admin can delete."""
    review = session.get(ProductReview, id)
    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    if review.client_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission insuffisante")
    session.delete(review)
    session.commit()
    return {"deleted": True}
