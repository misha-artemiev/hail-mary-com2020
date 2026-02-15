"""Creates seller and consumer entities."""

from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import Connection

from internal.geolocation.location import get_location
from internal.queries.consumer import CreateConsumerParams
from internal.queries.consumer import Querier as ConsumerQuerier
from internal.queries.models import Consumer, Seller, UserRole
from internal.queries.seller import CreateSellerParams
from internal.queries.seller import Querier as SellerQuerier
from internal.queries.user import CreateUserParams, CreateUserRow
from internal.queries.user import Querier as UserQuery

from .security import hash_password


def create_user(
    email: EmailStr, password: SecretStr, role: UserRole, conn: Connection
) -> CreateUserRow:
    """Create and insert base user entiry.

    Args:
      email: users email
      password: users plain text password
      role: users role, seller or consumer
      conn: database connection

    Returns:
      row from database with created users information

    Raises:
      ValueError: if database failed to create user
    """
    pw_hash = hash_password(password.get_secret_value())
    user = UserQuery(conn).create_user(
        CreateUserParams(email=email, pw_hash=pw_hash, role=role)
    )
    if not user:
        raise ValueError("Failed to create user")
    return user


class CreateConsumerForm(BaseModel):
    """Form with information to create consumer."""

    email: EmailStr
    password: SecretStr
    first_name: str
    last_name: str


def create_consumer(form: CreateConsumerForm, conn: Connection) -> Consumer:
    """Create and insert consumer and user entiry.

    Args:
      form: form with consumers information
      conn: database connection

    Returns:
      row with created consumers information from the database

    Raises:
      ValueError: if database failed to create consumer
    """
    user = create_user(form.email, form.password, UserRole.CONSUMER, conn)
    consumer = ConsumerQuerier(conn).create_consumer(
        CreateConsumerParams(
            user_id=user.user_id, fname=form.first_name, lname=form.last_name
        )
    )
    if not consumer:
        raise ValueError("Failed to create consumer")
    return consumer


class CreateSellerForm(BaseModel):
    """Form with information to create seller."""

    email: EmailStr
    password: SecretStr
    seller_name: str
    address_line1: str
    address_line2: str | None = None
    city: str
    post_code: str
    region: str | None = None
    country: str


def create_seller(form: CreateSellerForm, conn: Connection) -> Seller:
    """Creates and inserts seller and user entiry.

    Args:
      form: form with information for seller creation
      conn: database connection

    Returns:
     row with created sellers information from the database

    Raises:
      ValueError: database failed to create a seller
    """
    user = create_user(form.email, form.password, UserRole.SELLER, conn)
    address: str = ""
    address += f"{form.address_line1}"
    if form.address_line2:
        address += f", {form.address_line2}"
    address += f", {form.city}"
    address += f", {form.post_code}"
    if form.region:
        address += f", {form.region}"
    address += f", {form.country}"
    loc = get_location(address)
    seller = SellerQuerier(conn).create_seller(
        CreateSellerParams(
            user_id=user.user_id,
            seller_name=form.seller_name,
            address_line1=form.address_line1,
            address_line2=form.address_line2,
            city=form.city,
            post_code=form.post_code,
            region=form.region,
            country=form.country,
            latitude=loc.lat,
            longitude=loc.lon,
        )
    )
    if not seller:
        raise ValueError("Failed to create seller")
    return seller
