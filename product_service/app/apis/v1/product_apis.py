import json
import os
import sys
from typing import List

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

sys.path.append(f"{os.getcwd()}/fastapi_env/lib/python3.10/site-packages")

from fastapi import APIRouter, BackgroundTasks, Request, Depends
from pymongo.errors import PyMongoError

from app.db.database import db
from app.schemas.custom_response import CustomResponse
from app.schemas.product_schemas import ProductCreateSchema, ProductModel
from app.utils.auth_producer import ConnectUserService
from app.utils.utils import cache
from app.services.product_services import product_list, product_item


router = APIRouter()
connect_user_service = ConnectUserService()

security_scheme = HTTPBearer()

@router.post("/create")
@cache(timeout=300)
async def create_product(
    product: ProductCreateSchema,
    request: Request,
    background_tasks: BackgroundTasks,
    authenticated=Depends(connect_user_service.publish_token_to_queue),
):
    """
    Create a new product.

    Parameters:
    - `product`: The product data as per the `ProductCreateSchema` model.

    Returns:
    - JSON response with details of the created product.

    Example:
    ```json
    {
        "data": {"product_id": "1234567890"},
        "message": "Product Added",
        "status_code": 201
    }
    ```

    Possible Errors:
    - 500 Internal Server Error: If there's an issue with the server.
    - 404 Not Found: If the specified category doesn't exist.
    - 400 Bad Request: If there's an issue with the input data.

    """
    try:
        if not authenticated:
            return CustomResponse(status_code=401, message="Unauthenticated")

        product_data = product.model_dump()
        category = product_data["category"]

        category_obj = await db.category.find_one({"name": category})
        if category_obj is None:
            return CustomResponse(
                message=f"Category '{category}' not found.", status_code=404
            )

        product_data["category"] = {"name": category, "id": str(category_obj["_id"])}

        try:
            product_data["price"] = float(product_data["price"])
        except ValueError:
            return CustomResponse(message="Invalid price format", status_code=400)

        result = await db["products"].insert_one(product_data)

        return CustomResponse(
            data={"product_id": str(result.inserted_id)},
            message="Product Added",
            status_code=201,
        )
    except PyMongoError as e:
        return CustomResponse(
            message="MongoDB Error", status_code=500, exception=str(e)
        )
    except Exception as e:
        return CustomResponse(
            message="Internal Server Error", status_code=500, exception=str(e)
        )


@router.get("/list", response_model=List[ProductModel])
@cache(timeout=300)
async def get_product_list(
    request: Request,
    background_tasks: BackgroundTasks,
    token: HTTPAuthorizationCredentials = Depends(security_scheme),
    authenticated=Depends(connect_user_service.publish_token_to_queue),
):

    try:

        products = await product_list()
        for item in products:
            item["_id"] = str(item["_id"])

        return CustomResponse(data=products)
    except PyMongoError as mongo_error:
        return CustomResponse(
            status_code=500, message="MongoDB Error", exception=mongo_error
        )
    except Exception as e:
        return CustomResponse(
            status_code=500, message="Internal Server Error", exception=e
        )


@router.get("/get/{sku}", response_model=ProductModel)
@cache(timeout=200)
async def get_product(
    sku: str,
    request: Request,
    background_tasks: BackgroundTasks,
    authenticated=Depends(connect_user_service.publish_token_to_queue),
):
    try:
        if not authenticated:
            return CustomResponse(status_code=401, message="Unauthenticated")

        product = await product_item(sku)
        if not product:
            return CustomResponse(
                message="Product with provided sku not found", status_code=404
            )
        product["_id"] = str(product["_id"])
        return CustomResponse(data=product)
    except PyMongoError as mongo_error:
        return CustomResponse(
            status_code=500, message="MongoDB Error", exception=mongo_error
        )
    except Exception as e:
        return CustomResponse(
            status_code=500, message="Internal Server Error", exception=e
        )
