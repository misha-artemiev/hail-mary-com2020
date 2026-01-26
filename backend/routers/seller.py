from fastapi import APIRouter, Response
from internal.auth import create_seller, CreateSellerForm
from internal.database import database_dependency

router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("", status_code=201)
async def register_seller(
    form: CreateSellerForm, conn: database_dependency
) -> Response:
    _ = create_seller(form, conn)
    return Response("Seller was registered", 201)
