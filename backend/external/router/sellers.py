from fastapi import Request, APIRouter, Response
from internal.auth import register_seller, RegisterSellerForm
from internal.logging import logger

router = APIRouter(prefix="/sellers", tags=["sellers"])

@router.post("")
async def register(request: Request, register_seller_form: RegisterSellerForm):
    result = register_seller(register_seller_form)
    if isinstance(result, Exception):
        logger.error(result.args)
        return Response("Internal Server Error (probably)", 500)
    return Response("Seller was registered", 200)
