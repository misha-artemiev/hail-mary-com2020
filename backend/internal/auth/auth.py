from typing import Annotated
from .password import hash_password
from pydantic import BaseModel, EmailStr, StringConstraints
from internal.queries.models import Consumer, Seller
from internal.queries.consumer import Querier as ConsumerQuerier
from internal.queries.seller import CreateSellerParams, Querier as SellerQuerier
from internal.queries.models import UserRole
from internal.queries.user import Querier as UserQuery
from internal.database import database_manager

class RegisterConsumerForm(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=10)]
    first_name: Annotated[str, StringConstraints(min_length=1)]
    last_name: Annotated[str, StringConstraints(min_length=1)]

def register_consumer(register_consumer_form: RegisterConsumerForm) -> Consumer | Exception:
    hash = hash_password(register_consumer_form.password)
    engine = database_manager.get_engine()
    if isinstance(engine, Exception):
        return engine
    with engine.connect() as conn:
        user = UserQuery(conn).create_user(
            email=register_consumer_form.email,
            pw_hash=hash,
            role=UserRole.CONSUMER
        )
        if not user:
            return Exception("Internal user creation error")
        consumer = ConsumerQuerier(conn).create_consumer(
            user_id=user.user_id,
            fname=register_consumer_form.first_name,
            lname=register_consumer_form.last_name
        )
        if not consumer:
            return Exception("Internal consumer creation error")
        conn.commit()
        return consumer

class RegisterSellerForm(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=10)]
    seller_name: str
    address_line1: str
    address_line2: str
    city: str
    post_code: str
    region: str
    country: str

def register_seller(register_seller_form: RegisterSellerForm) -> Seller | Exception:
    hash = hash_password(register_seller_form.password)
    engine = database_manager.get_engine()
    if isinstance(engine, Exception):
        return engine
    with engine.connect() as conn:
        user = UserQuery(conn).create_user(
            email=register_seller_form.email,
            pw_hash=hash,
            role=UserRole.CONSUMER
        )
        if not user:
            return Exception("Internal user creation error")
        seller = SellerQuerier(conn).create_seller(CreateSellerParams(
                user_id=user.user_id,
                seller_name=register_seller_form.seller_name,
                address_line1=register_seller_form.address_line1,
                address_line2=register_seller_form.address_line2,
                city=register_seller_form.city,
                post_code=register_seller_form.post_code,
                region=register_seller_form.region,
                country=register_seller_form.country
        ))
        if not seller:
            return Exception("Internal seller creation error")
        conn.commit()
        return seller
