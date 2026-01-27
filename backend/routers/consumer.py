"""Endpointd for consumer."""

from fastapi import APIRouter, Response
from internal.auth import CreateConsumerForm, create_consumer
from internal.database import database_dependency

router = APIRouter(prefix="/consumer", tags=["consumer"])


@router.post("", status_code=201)
async def register_consumer(
    form: CreateConsumerForm, conn: database_dependency
) -> Response:
    """Register consumer and corresponding user.

    Args:
      form: signup information for the user
      conn: database connection

    Returns:
      if consumer was registered
    """
    _ = create_consumer(form, conn)
    return Response("Consumer was registered", 201)
