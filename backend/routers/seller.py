"""Endpoints for seller."""

from fastapi import APIRouter, Response
from internal.auth import CreateSellerForm, create_seller
from internal.database import database_dependency

router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("", status_code=201)
async def register_seller(
    form: CreateSellerForm, conn: database_dependency
) -> Response:
    """Creates seller and coressponding user.

    Args:
      form: signup form from user
      conn: database connection

    Returns:
      if seller was registered
    """
    _ = create_seller(form, conn)
    return Response("Seller was registered", 201)
