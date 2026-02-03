"""Endpoints for sellers.

```mermaid
---
config:
  mirrorActors: false
---
sequenceDiagram
    title Seller Registration
    actor user
    box ./routers
    participant sellers.py@{ "type" : "boundary" }
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
    participant sq as seller.py
    end
    participant database@{ "type" : "database" }

    user->>sellers.py: register seller
    activate sellers.py
    dd->>sellers.py: yield connection
    activate dd
    sellers.py->>creation.py: create_seller()
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
    creation.py->>sq: Queries.create_seller()
    activate sq
    sq->>database: insert seller
    activate database
    database-->>sq: created seller
    deactivate database
    sq-->>creation.py: created seller
    deactivate sq
    creation.py-->>sellers.py: created seller
    deactivate creation.py
    sellers.py-->>user: 201 OK
    sellers.py-->>dd: return connection
    deactivate dd
    deactivate sellers.py
```
"""

from fastapi import APIRouter, Response
from internal.auth.creation import CreateSellerForm, create_seller
from internal.database.dependency import database_dependency

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.post("", status_code=201)
async def register_seller(
    form: CreateSellerForm, conn: database_dependency
) -> Response:
    """Creates seller and coressponding user.

    Args:
      form: signup form from user
      conn: database connection

    Returns:
      if seller was registered
    """
    _ = create_seller(form, conn)
    return Response("Seller was registered", 201)
