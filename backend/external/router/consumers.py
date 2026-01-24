from fastapi import Request, APIRouter, Response
from sqlalchemy.exc import IntegrityError, OperationalError
from internal.auth import register_consumer, RegisterConsumerForm
from internal.database import database_manager

router = APIRouter(prefix="/consumers", tags=["consumers"])

@router.post("")
async def register(request: Request, register_consumer_form: RegisterConsumerForm):
    try:
        with database_manager.get_engine().begin() as conn: 
            register_consumer(register_consumer_form, conn)
    except OperationalError:
        return Response("Service unavailable", 503)
    except IntegrityError:
        return Response("Conflict", 409)
    except ValueError:
        return Response("Validation Error", 400)
    except Exception:
        return Response("Internal Error", 500)
    return Response("Consumer was registered", 200)
