from fastapi import Request, APIRouter, Response
from internal.auth import register_seller, RegisterSellerForm
from internal.database import database_manager
from sqlalchemy.exc import IntegrityError, OperationalError

router = APIRouter(prefix="/sellers", tags=["sellers"])

@router.post("")
async def register(request: Request, register_seller_form: RegisterSellerForm):
    try:
        with database_manager.get_engine().begin() as conn: 
            register_seller(register_seller_form, conn)
    except OperationalError:
        return Response("Service unavailable", 503)
    except IntegrityError:
        return Response("Conflict", 409)
    except ValueError:
        return Response("Validation Error", 400)
    except Exception:
        return Response("Internal Error", 500)
    return Response("Seller was registered", 200)
