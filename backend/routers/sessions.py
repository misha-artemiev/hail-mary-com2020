"""Endpoint for sessions.

```mermaid
---
config:
  mirrorActors: false
---
sequenceDiagram
    title Session Creation
    actor User
    box ./routers
    participant sessions.py@{ "type" : "boundary" }
    end
    box ./internal/database
    participant database.py
    end
    box ./internal/auth
    participant middleware.py
    participant token.py
    participant security.py
    end
    box ./internal/queries
    participant tq as token.py
    participant uq as user.py
    end
    participant database@{ "type" : "database" }

    User->>sessions.py: create session
    activate sessions.py
    sessions.py->>middleware.py: basic_auth()
    activate middleware.py
    database.py->>middleware.py: yield connection
    activate database.py
    middleware.py->>uq: get_user_login()
    activate uq
    uq->>database: select user
    activate database
    database-->>uq: found user
    deactivate database
    uq-->>middleware.py: found user
    deactivate uq
    middleware.py-->>sessions.py: user and role
    middleware.py-->>database.py: return connection
    deactivate middleware.py
    deactivate database.py
    database.py->>sessions.py: yield connection
    activate database.py
    sessions.py->>token.py: create_token()
    activate token.py
    token.py->>security.py: generate_token()
    activate security.py
    security.py-->>token.py: generated token
    deactivate security.py
    token.py->>tq: Querier.create_token()
    activate tq
    tq->>database: insert token
    activate database
    database-->>tq: inserted token
    deactivate database
    tq-->>token.py: inserted token
    deactivate tq
    token.py-->>sessions.py: inserted token
    deactivate token.py
    sessions.py-->>User: 201 OK + token
    sessions.py-->>database.py: return connection
    deactivate database.py
    deactivate sessions.py
```

```mermaid
---
config:
  mirrorActors: false
---
sequenceDiagram
    title Session Deletion
    actor User
    box ./routers
    participant sessions.py@{ "type" : "boundary" }
    end
    box ./internal/database
    participant database.py
    end
    box ./internal/auth
    participant middleware.py
    participant token.py
    end
    box ./internal/queries
    participant tq as token.py
    end
    participant database@{ "type" : "database" }

    User->>sessions.py: delete session
    activate sessions.py
    sessions.py->>middleware.py: bearer_auth()
    activate middleware.py
    database.py->>middleware.py: yield connection
    activate database.py
    middleware.py->>tq: get_session_by_token()
    activate tq
    tq->>database: select token
    activate database
    database-->>tq: found token
    deactivate database
    tq-->>middleware.py: found token
    deactivate tq
    middleware.py-->>sessions.py: found token
    middleware.py-->>database.py: return connection
    deactivate middleware.py
    deactivate database.py
    database.py->>sessions.py: yield connection
    activate database.py
    sessions.py->>token.py: delete_token()
    activate token.py
    token.py->>tq: Querier.delete_token()
    activate tq
    tq->>database: delete token
    activate database
    database-->>tq: deleted token
    deactivate database
    tq-->>token.py: deleted token
    deactivate tq
    token.py-->>sessions.py: deleted token
    deactivate token.py
    sessions.py-->>User: 200 OK
    sessions.py-->>database.py: return connection
    deactivate sessions.py
    deactivate database.py
```
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Security, status
from internal.auth.middleware import BasicAuthResponse, basic_auth, bearer_auth
from internal.auth.token import create_token, delete_token
from internal.database.dependency import database_dependency
from internal.queries.models import UserRole
from internal.queries.token import GetSessionByTokenRow
from pydantic import BaseModel

router = APIRouter(prefix="/sessions", tags=["sessions"])


class TokenResponseModel(BaseModel):
    """Response on session creation."""

    token: str
    expires_at: datetime
    role: UserRole


@router.post(
    "",
    response_model=TokenResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create session",
    description="Authenticates a user and creates a new session token.",
)
def create_session(
    conn: database_dependency, user: Annotated[BasicAuthResponse, Security(basic_auth)]
) -> TokenResponseModel:
    """Create session if user exists.

    Args:
      conn: database connection
      user: user information if authorised

    Returns:
      user session information
    """
    token = create_token(user.user_id, conn)
    return TokenResponseModel(
        token=token.token, expires_at=token.expires_at, role=user.role
    )


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Delete session",
    description="Deletes the current authenticated session token.",
)
def delete_session(
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> None:
    """Delete session from database.

    Args:
      conn: database connection
      session: authorised users information
    """
    delete_token(session.token, conn)
