"""Endpoint for consumers.

```mermaid
---
config:
  mirrorActors: false
---
sequenceDiagram
    title Consumer Registration
    actor user
    box ./routers
    participant consumers.py@{ "type" : "boundary" }
    end
    box ./internal/database
    participant dd as database.py
    end
    box ./internal/auth
    participant creation.py
    participant security.py
    end
    box ./internal/queries
    participant user.py
    participant cq as consumer.py
    end
    participant database@{ "type" : "database" }

    user->>consumer.py: register consumer
    activate consumers.py
    dd->>consumers.py: yield connection
    activate dd
    consumers.py->>creation.py: create_consumer()
    activate creation.py
    creation.py->>creation.py: create_user()
    creation.py->>security.py: hash_password()
    activate security.py
    security.py-->>creation.py: password hash
    deactivate security.py
    creation.py->>user.py: Queries.create_user()
    activate user.py
    user.py->>database: insert user
    activate database
    database-->>user.py: created user
    deactivate database
    user.py-->>creation.py: created user
    deactivate user.py
    creation.py-->>creation.py: created user
    creation.py->>cq: Queries.create_consumer()
    activate cq
    cq->>database: insert consumer
    activate database
    database-->>cq: created consumer
    deactivate database
    cq-->>creation.py: created consumer
    deactivate cq
    creation.py-->>consumers.py: created consumer
    deactivate creation.py
    consumers.py-->>user: 201 OK
    consumers.py-->>dd: return connection
    deactivate dd
    deactivate consumers.py
```
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Response
from internal.auth.creation import CreateConsumerForm, create_consumer
from internal.auth.middleware import consumer_auth
from internal.auth.security import UpdatePasswordForm, update_pw
from internal.database.dependency import database_dependency
from internal.queries.token import GetSessionByTokenRow
from internal.queries.user import Querier as UserQuerier
from internal.queries.user import UpdateUserEmailParams
from pydantic import EmailStr

router = APIRouter(prefix="/consumers", tags=["consumers"])


@router.post("", status_code=201)
async def register_consumer(
    form: CreateConsumerForm, conn: database_dependency
) -> Response:
    """Register consumer and corresponding user.

    Args:
      form: signup information for the user
      conn: database connection

    Returns:
      if consumer was registered
    """
    _ = create_consumer(form, conn)
    return Response("Consumer was registered", 201)


@router.put("/me/password", status_code=202)
async def update_password(
    form: UpdatePasswordForm,
    conn: database_dependency,
    consumer: Annotated[GetSessionByTokenRow, consumer_auth],
) -> Response:
    """Update users password.

    Args:
      form: form for password change
      conn: database connection
      consumer: consumers session

    Returns:
      if password was changed
    """
    _ = update_pw(consumer.email, form, conn)
    return Response("Password was updated", 202)


@router.put("/me/email", status_code=202)
async def update_email(
    email: EmailStr,
    conn: database_dependency,
    consumer: Annotated[GetSessionByTokenRow, consumer_auth],
) -> Response:
    """Update users email.

    Args:
      email: new users email
      conn: database connection
      consumer: consumers session

    Returns:
      if consumer email was updated

    Raises:
      HTTPException: failed to update user email
    """
    user = UserQuerier(conn).update_user_email(
        UpdateUserEmailParams(user_id=consumer.user_id, email=email)
    )
    if not user:
        raise HTTPException(500, "failed to update users email")
    return Response("user email was updated", 201)
