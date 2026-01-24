from typing import Optional
from sqlalchemy import Connection
from .security import hash_password
from pydantic import BaseModel, EmailStr, SecretStr
from internal.queries.models import Consumer, Seller, UserRole
from internal.queries.consumer import Querier as ConsumerQuerier
from internal.queries.seller import CreateSellerParams, Querier as SellerQuerier
from internal.queries.user import Querier as UserQuery, CreateUserRow

def create_user(email: EmailStr, password: SecretStr, role: UserRole, conn: Connection) -> CreateUserRow:
    hash = hash_password(password.get_secret_value())
    user = UserQuery(conn).create_user(
        email=email,
        pw_hash=hash,
        role=role
    )
    if not user:
        raise ValueError("Failed to create user")
    return user

class RegisterConsumerForm(BaseModel):
    email: EmailStr
    password: SecretStr
    first_name: str
    last_name: str

def register_consumer(register_consumer_form: RegisterConsumerForm, conn: Connection) -> Consumer:
    user = create_user(register_consumer_form.email, register_consumer_form.password, UserRole.CONSUMER, conn)
    consumer = ConsumerQuerier(conn).create_consumer(
        user_id=user.user_id,
        fname=register_consumer_form.first_name,
        lname=register_consumer_form.last_name
    )
    if not consumer:
        raise ValueError("Failed to create consumer")
    return consumer

class RegisterSellerForm(BaseModel):
    email: EmailStr
    password: SecretStr
    seller_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    post_code: str
    region: Optional[str] = None
    country: str

def register_seller(register_seller_form: RegisterSellerForm, conn: Connection) -> Seller:
    user = create_user(register_seller_form.email, register_seller_form.password, UserRole.SELLER, conn)
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
        raise ValueError("Failed to create seller")
    return seller
