from fastapi import APIRouter, Response
from internal.auth import register_seller, RegisterSellerForm
from internal.database import database_dependency

router = APIRouter(prefix="/sellers", tags=["sellers"])

@router.post("")
async def register(register_seller_form: RegisterSellerForm, conn: database_dependency):
    _ = register_seller(register_seller_form, conn)
    return Response("Seller was registered", 200)
