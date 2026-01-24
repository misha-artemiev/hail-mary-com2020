from fastapi import APIRouter, Response
from internal.auth import register_consumer, RegisterConsumerForm
from internal.database import database_dependency

router = APIRouter(prefix="/consumer", tags=["consumer"])

@router.post("")
async def register(register_consumer_form: RegisterConsumerForm, conn: database_dependency):
    _ = register_consumer(register_consumer_form, conn)
    return Response("Consumer was registered", 200)
