from typing import Optional
from sqlalchemy import Connection
from .security import hash_password
from pydantic import BaseModel, EmailStr, SecretStr
from internal.queries.models import Consumer, Seller, UserRole
from internal.queries.consumer import Querier as ConsumerQuerier
from internal.queries.seller import CreateSellerParams, Querier as SellerQuerier
from internal.queries.user import Querier as UserQuery, CreateUserRow

# insert user into db
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

# form to be passed into consumer creation api
class CreateConsumerForm(BaseModel):
    email: EmailStr
    password: SecretStr
    first_name: str
    last_name: str

# create consumer and user
def create_consumer(form: CreateConsumerForm, conn: Connection) -> Consumer:
    user = create_user(form.email, form.password, UserRole.CONSUMER, conn)
    consumer = ConsumerQuerier(conn).create_consumer(
        user_id=user.user_id,
        fname=form.first_name,
        lname=form.last_name
    )
    if not consumer:
        raise ValueError("Failed to create consumer")
    return consumer

# form to be passed into seller creation api
class CreateSellerForm(BaseModel):
    email: EmailStr
    password: SecretStr
    seller_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    post_code: str
    region: Optional[str] = None
    country: str

# register unverified seller and user
def create_seller(form: CreateSellerForm, conn: Connection) -> Seller:
    user = create_user(form.email, form.password, UserRole.SELLER, conn)
    seller = SellerQuerier(conn).create_seller(CreateSellerParams(
            user_id=user.user_id,
            seller_name=form.seller_name,
            address_line1=form.address_line1,
            address_line2=form.address_line2,
            city=form.city,
            post_code=form.post_code,
            region=form.region,
            country=form.country
    ))
    if not seller:
        raise ValueError("Failed to create seller")
    return seller
