from fastapi import APIRouter
from internal.auth import create_consumer, CreateConsumerForm
from internal.database import database_dependency

router = APIRouter(prefix="/consumer", tags=["consumer"])


@router.post("", status_code=201)
async def register_consumer(form: CreateConsumerForm, conn: database_dependency):
    _ = create_consumer(form, conn)
    return "Consumer was registered"
