"""Endpoint for consumer.

```mermaid
---
config:
  mirrorActors: false
---
sequenceDiagram
    title Consumer Registration
    actor user
    box ./routers
    participant consumer.py@{ "type" : "boundary" }
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
    activate consumer.py
    dd->>consumer.py: yield connection
    activate dd
    consumer.py->>creation.py: create_consumer()
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
    creation.py-->>consumer.py: created consumer
    deactivate creation.py
    consumer.py-->>user: 201 OK
    consumer.py-->>dd: return connection
    deactivate dd
    deactivate consumer.py
```
"""

from fastapi import APIRouter, Response
from internal.auth.creation import CreateConsumerForm, create_consumer
from internal.database.dependency import database_dependency

router = APIRouter(prefix="/consumer", tags=["consumer"])


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
