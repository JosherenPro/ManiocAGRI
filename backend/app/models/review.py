from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ProductReviewBase(SQLModel):
    product_id: int = Field(foreign_key="product.id", index=True)
    client_id: int = Field(foreign_key="user.id", index=True)
    rating: int = Field(ge=1, le=5)  # 1 to 5 stars
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProductReview(ProductReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductReviewCreate(SQLModel):
    product_id: int
    rating: int
    comment: Optional[str] = None


class ProductReviewRead(ProductReviewBase):
    id: int
