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

from fastapi import APIRouter, HTTPException, Response, Security
from internal.auth.creation import CreateConsumerForm, create_consumer
from internal.auth.middleware import consumer_auth
from internal.database.dependency import database_dependency
from internal.queries.consumer import Querier as ConsumerQuerier
from internal.queries.consumer import UpdateConsumerParams
from internal.queries.models import Reservation
from internal.queries.reservations import Querier as ReservationsQuerier
from internal.queries.token import GetSessionByTokenRow
from pydantic import BaseModel

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


@router.get("/me/reservations", tags=["reservations"])
async def get_reservations(
    conn: database_dependency,
    consumer: Annotated[GetSessionByTokenRow, Security(consumer_auth)],
) -> list[Reservation]:
    """Get consumers reservations.

    Args:
      conn: database connection
      consumer: consumer session

    Returns:
        list of consumers reservations

    Raises:
        HTTPException: if failed to get reservations
    """
    reservations = ReservationsQuerier(conn).get_consumers_reservations(
        consumer_id=consumer.user_id
    )
    if not reservations:
        raise HTTPException(500, "failed to get reservations")
    return list(reservations)


class UpdateConsumerForm(BaseModel):
    """Consumer name update form."""

    first_name: str
    last_name: str


@router.patch("/me")
async def update_consumer(
    form: UpdateConsumerForm,
    conn: database_dependency,
    consumer: Annotated[GetSessionByTokenRow, Security(consumer_auth)],
) -> Response:
    """Consumer name update.

    Args:
        form: consumer update form
        conn: database connection
        consumer: consumer session

    Returns:
        if consumer was update

    Raises:
        HTTPException: if failed to update consumer
    """
    updated_consumer = ConsumerQuerier(conn).update_consumer(
        UpdateConsumerParams(
            user_id=consumer.user_id, fname=form.first_name, lname=form.last_name
        )
    )
    if not updated_consumer:
        raise HTTPException(500, "failed to update consumer")
    return Response("consumer was updated", 200)
