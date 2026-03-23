"""Creates seller and consumer entities."""

from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy.ext.asyncio import AsyncConnection

from internal.queries.admin import AsyncQuerier as AdminQuerier
from internal.queries.admin import CreateAdminParams
from internal.queries.consumer import AsyncQuerier as ConsumerQuerier
from internal.queries.consumer import CreateConsumerParams
from internal.queries.models import Admin, Consumer, Seller, UserRole
from internal.queries.seller import AsyncQuerier as SellerQuerier
from internal.queries.seller import CreateSellerParams
from internal.queries.user import AsyncQuerier as UserQuerier
from internal.queries.user import CreateUserParams, CreateUserRow

from .security import hash_password


async def create_user(
    username: str,
    email: EmailStr,
    password: SecretStr,
    role: UserRole,
    conn: AsyncConnection,
) -> CreateUserRow:
    """Create and insert base user entry.

    Args:
      username: username for user
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
    user = await UserQuerier(conn).create_user(
        CreateUserParams(username=username, email=email, pw_hash=pw_hash, role=role)
    )
    if not user:
        raise ValueError("Failed to create user")
    return user


class CreateConsumerForm(BaseModel):
    """Form with information to create consumer."""

    username: str
    email: EmailStr
    password: SecretStr
    first_name: str
    last_name: str


async def create_consumer(form: CreateConsumerForm, conn: AsyncConnection) -> Consumer:
    """Create and insert consumer and user entry.

    Args:
      form: form with consumers information
      conn: database connection

    Returns:
      row with created consumers information from the database

    Raises:
      ValueError: if database failed to create consumer
    """
    user = await create_user(
        form.username, form.email, form.password, UserRole.CONSUMER, conn
    )
    consumer = await ConsumerQuerier(conn).create_consumer(
        CreateConsumerParams(
            user_id=user.user_id, fname=form.first_name, lname=form.last_name
        )
    )
    if not consumer:
        raise ValueError("Failed to create consumer")
    return consumer


class CreateSellerForm(BaseModel):
    """Form with information to create seller."""

    username: str
    email: EmailStr
    password: SecretStr
    seller_name: str
    address_line1: str
    address_line2: str | None = None
    city: str
    post_code: str
    region: str | None = None
    country: str
    latitude: float
    longitude: float


async def create_seller(form: CreateSellerForm, conn: AsyncConnection) -> Seller:
    """Creates and inserts seller and user entry.

    Args:
      form: form with information for seller creation
      conn: database connection

    Returns:
     row with created sellers information from the database

    Raises:
      ValueError: database failed to create a seller
    """
    user = await create_user(
        form.username, form.email, form.password, UserRole.SELLER, conn
    )
    seller = await SellerQuerier(conn).create_seller(
        CreateSellerParams(
            user_id=user.user_id,
            seller_name=form.seller_name,
            address_line1=form.address_line1,
            address_line2=form.address_line2,
            city=form.city,
            post_code=form.post_code,
            region=form.region,
            country=form.country,
            latitude=form.latitude,
            longitude=form.longitude,
        )
    )
    if not seller:
        raise ValueError("Failed to create seller")
    return seller


class CreateAdminForm(BaseModel):
    """Form with information to create admin."""

    username: str
    email: EmailStr
    password: SecretStr
    first_name: str
    last_name: str


async def create_admin(form: CreateAdminForm, conn: AsyncConnection) -> Admin:
    """Create and insert admin and user entry.

    Args:
      form: form with admin information
      conn: database connection

    Returns:
      row with created admin information from the database

    Raises:
      ValueError: if database failed to create admin
    """
    user = await create_user(
        form.username, form.email, form.password, UserRole.ADMIN, conn
    )
    admin = await AdminQuerier(conn).create_admin(
        CreateAdminParams(
            user_id=user.user_id, fname=form.first_name, lname=form.last_name
        )
    )
    if not admin:
        raise ValueError("Failed to create admin")
    return admin
