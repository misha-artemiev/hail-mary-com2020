from fastapi import APIRouter, Response
from internal.auth import CreateConsumerForm, create_consumer
from internal.database import database_dependency

router = APIRouter(prefix="/consumer", tags=["consumer"])


@router.post("", status_code=201)
async def register_consumer(
    form: CreateConsumerForm, conn: database_dependency
) -> Response:
    _ = create_consumer(form, conn)
    return Response("Consumer was registered", 201)
