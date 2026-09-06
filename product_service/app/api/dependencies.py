from fastapi import Depends

from app.db.session import get_db
from app.repositories.product_repository import ProductRepository
from app.services.category_service import CategoryRepository, CategoryService
from app.services.product_service import ProductService


def get_product_service(
    db=Depends(get_db),
) -> ProductService:
    repository: ProductRepository = ProductRepository(db)
    return ProductService(repository)


def get_category_service(
    db=Depends(get_db),
) -> CategoryService:
    repository: CategoryRepository = CategoryRepository(db)
    return CategoryService(repository)
