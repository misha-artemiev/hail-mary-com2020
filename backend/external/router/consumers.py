from fastapi import Request, APIRouter, Response
from internal.auth import register_consumer, RegisterConsumerForm
from internal.logging import logger

router = APIRouter(prefix="/consumers", tags=["consumers"])

@router.post("")
async def register(request: Request, register_consumer_form: RegisterConsumerForm):
    result = register_consumer(register_consumer_form)
    if isinstance(result, Exception):
        logger.error(result.args)
        return Response("Internal Server Error (probably)", 500)
    return Response("Consumer was registered", 200)
