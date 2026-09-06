
from fastapi import APIRouter, Depends
from pymongo.errors import PyMongoError

from app.schemas.category_schemas import CategoryCreateSchema, CategoryModel
from app.schemas.custom_response import CustomResponse
from app.services.category_service import category_create, get_category_list
from app.utils.auth_producer import ConnectUserService

router = APIRouter()
connect_user_service = ConnectUserService()


@router.post("/create")
async def create_category(
    category: CategoryCreateSchema,
    authenticated=Depends(connect_user_service.publish_token_to_queue),
):
    """
    Create a new category.

    Parameters:
    - `category`: The category data as per the `CategoryCreateSchema` model.

    Returns:
    - JSON response indicating the success or failure of the category creation.

    Example:
    ```json
    {
        "data": null,
        "message": "Success",
        "status_code": 200
    }
    ```

    Possible Errors:
    - 500 Internal Server Error: If there's an issue with the server.

    """
    try:
        if not authenticated:
            return CustomResponse(status_code=401, message="Unauthenticated")

        user_details = authenticated
        category_data = category.model_dump()
        category_data["created_by"] = {
            "id": user_details["identity"],
            "email": user_details["email"],
        }
        result = await category_create(category_data)
        return CustomResponse(
            message="Category Created",
            data={"category_id": str(result.inserted_id)},
            status_code=201,
        )
    except PyMongoError as mongo_error:
        return CustomResponse(message="MongoDB Error", exception=mongo_error)
    except Exception as e:
        return CustomResponse(
            message="Internal Server Error", exception=e, status_code=500
        )


@router.get("/list", response_model=list[CategoryModel])
async def category_list(
    authenticated=Depends(connect_user_service.publish_token_to_queue),
):
    """
    Fetch all documents from the 'category' collection.

    Returns:
    - List of category documents.

    Example Response:
    ```json
    [
        {
            "name": "Category1",
            "description": "Description1"
        },
        {
            "name": "Category2",
            "description": "Description2"
        },
        ...
    ]
    ```

    Possible Errors:
    - 500 Internal Server Error: If there's an issue with the server.
    """
    try:
        if not authenticated:
            return CustomResponse(status_code=401, message="Unauthenticated")

        categories = await get_category_list()
        return categories
    except PyMongoError as mongo_error:
        return CustomResponse(
            message="MongoDB Error", status_code=500, exception=mongo_error
        )
    except Exception as e:
        return CustomResponse(
            message="Internal Server Error", status_code=500, exception=e
        )
