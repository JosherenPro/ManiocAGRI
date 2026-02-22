from fastapi import APIRouter
from api.v1.endpoints import (
    auth, users, products, orders, field_data, dashboard, ai,
    categories, notifications, delivery_zones, reviews, transactions, harvests,
    payments, webhooks
)

api_router = APIRouter()

# Core auth & users
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Products & catalog
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])

# Orders & logistics
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(delivery_zones.router, prefix="/delivery-zones", tags=["delivery-zones"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Field & agriculture
api_router.include_router(field_data.router, prefix="/field-data", tags=["field-data"])
api_router.include_router(harvests.router, prefix="/harvests", tags=["harvests"])

# Platform
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
