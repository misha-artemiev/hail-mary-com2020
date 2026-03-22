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
    consumers.py->>creation.py: await create_consumer()
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

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from internal.auth.creation import CreateConsumerForm, create_consumer
from internal.auth.middleware import ConsumerAuthDep
from internal.database.dependency import database_dependency
from internal.queries.badge import AsyncQuerier as BadgeQuerier
from internal.queries.inbox import AsyncQuerier as InboxQuerier
from internal.queries.inbox import CreateInboxMessageParams
from internal.queries.badge import GetConsumerBadgesRow
from internal.queries.bundle import AsyncQuerier as BundleQuerier
from internal.queries.consumer import AsyncQuerier as ConsumerQuerier
from internal.queries.consumer import (
    GetConsumerRow,
    GetConsumersRow,
    UpdateConsumerParams,
)
from internal.queries.models import Reservation
from internal.queries.reservations import AsyncQuerier as ReservationsQuerier
from internal.queries.reservations import GetConsumersReservationsFullRow
from pydantic import BaseModel

router = APIRouter(prefix="/consumers", tags=["consumers"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get all consumers",
    description="Retrieves a list of all registered consumers.",
)
async def get_consumers(conn: database_dependency) -> list[GetConsumersRow]:
    """Get all consumers.

    Args:
      conn: database connection

    Returns:
      list of all consumers
    """
    return [c async for c in ConsumerQuerier(conn).get_consumers()]


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get authenticated consumer",
    description="Retrieves the profile of the authenticated consumer.",
)
async def get_consumer_me(
    conn: database_dependency, consumer: ConsumerAuthDep
) -> GetConsumerRow:
    """Get authenticated consumer profile.

    Args:
      conn: database connection
      consumer: consumers session

    Returns:
      consumer profile

    Raises:
      HTTPException: if consumer not found
    """
    consumer_profile = await ConsumerQuerier(conn).get_consumer(
        user_id=consumer.user_id
    )
    if not consumer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Consumer profile not found"
        )
    return consumer_profile


@router.get(
    "/{consumer_id}",
    status_code=status.HTTP_200_OK,
    summary="Get consumer by ID",
    description="Retrieves the profile of a consumer by their unique ID.",
)
async def get_consumer_by_id(
    consumer_id: int, conn: database_dependency
) -> GetConsumerRow:
    """Get consumer profile by ID.

    Args:
      consumer_id: unique identifier of the consumer
      conn: database connection

    Returns:
      consumer profile

    Raises:
      HTTPException: if consumer not found
    """
    consumer_profile = await ConsumerQuerier(conn).get_consumer(user_id=consumer_id)
    if not consumer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Consumer not found"
        )
    return consumer_profile


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Register consumer",
    description="Registers a new consumer and their corresponding user entity.",
)
async def register_consumer(
    form: CreateConsumerForm, conn: database_dependency
) -> None:
    """Register consumer and corresponding user.

    Args:
      form: signup information for the user
      conn: database connection
    """
    _ = await create_consumer(form, conn)


@router.get(
    "/me/reservations",
    tags=["reservations"],
    status_code=status.HTTP_200_OK,
    summary="Get consumer reservations",
    description="Retrieves all reservations made by the authenticated consumer.",
)
async def get_reservations(
    conn: database_dependency, consumer: ConsumerAuthDep
) -> list[Reservation]:
    """Get consumers reservations.

    Args:
      conn: database connection
      consumer: consumer session

    Returns:
        list of consumer reservations

    Raises:
        HTTPException: if failed to get reservations
    """
    reservations = [
        item
        async for item in ReservationsQuerier(conn).get_consumers_reservations(
            consumer_id=consumer.user_id
        )
    ]
    if reservations is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reservations",
        )

    now = datetime.now(tz=UTC)
    bundle_querier = BundleQuerier(conn)
    for reservation in reservations:
        if reservation.collected_at is not None:
            continue
        bundle = await bundle_querier.get_bundle(bundle_id=reservation.bundle_id)
        if bundle is None:
            continue
        if bundle.window_end <= now:
            await InboxQuerier(conn).create_inbox_message(
                CreateInboxMessageParams(
                    user_id=consumer.user_id,
                    sender_id=consumer.user_id,
                    message_subject="Reservation timed out",
                    message_text=(
                        f"Your reservation for '{bundle.bundle_name}' has timed out because"
                        "the pickup window ended at "
                        f"{bundle.window_end.strftime('%Y-%m-%d %H:%M UTC')}."
                    ),
                )
            )

    return list(reservations)


@router.get(
    "/me/rescued",
    tags=["reservations"],
    status_code=status.HTTP_200_OK,
    summary="Get number of consumer rescued reservations",
    description="Retrieves number of rescued (collected) reservations.",
)
async def get_rescued(conn: database_dependency, consumer: ConsumerAuthDep) -> int:
    """Get count of rescued (collected) reservations for the authenticated consumer.

    Args:
      conn: database connection
      consumer: consumer session

    Returns:
        number of rescued (collected) reservations
    """
    result = await ReservationsQuerier(conn).count_consumer_collected_reservations(
        consumer_id=consumer.user_id
    )
    return result.collected_count if result else 0


class UpdateConsumerForm(BaseModel):
    """Consumer name update form."""

    first_name: str
    last_name: str


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Update consumer profile",
    description=(
        "Updates the profile information (first and last name) "
        "for the authenticated consumer."
    ),
)
async def update_consumer(
    form: UpdateConsumerForm, conn: database_dependency, consumer: ConsumerAuthDep
) -> None:
    """Consumer name update.

    Args:
        form: consumer update form
        conn: database connection
        consumer: consumer session

    Raises:
        HTTPException: if failed to update consumer
    """
    updated_consumer = await ConsumerQuerier(conn).update_consumer(
        UpdateConsumerParams(
            user_id=consumer.user_id, fname=form.first_name, lname=form.last_name
        )
    )
    if not updated_consumer:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update consumer",
        )


@router.get(
    "/me/badges",
    status_code=status.HTTP_200_OK,
    summary="Consumer badges",
    description="Get all acquired badges by consumer",
    tags=["badges"],
)
async def get_consumer_badges(
    conn: database_dependency, consumer: ConsumerAuthDep
) -> list[GetConsumerBadgesRow]:
    """Get badges acquired by consumer.

    Args:
      conn: database connection
      consumer: consumer session

    Returns:
      list of acquired badges
    """
    return [
        badge
        async for badge in BadgeQuerier(conn).get_consumer_badges(
            user_id=consumer.user_id
        )
    ]


@router.get(
    "/me/streaks",
    status_code=status.HTTP_200_OK,
    summary="Consumer streak",
    description="Get consumer streak in number of weeks",
    tags=["analytics"],
)
async def get_streaks(conn: database_dependency, consumer: ConsumerAuthDep) -> int:
    """Get consumer collection streak in number of weeks.

    Args:
        conn: database connection
        consumer: consumer session

    Returns:
        number of weeks
    """
    reservations: list[GetConsumersReservationsFullRow] = [
        reservation
        async for reservation in ReservationsQuerier(
            conn
        ).get_consumers_reservations_full(consumer_id=consumer.user_id)
    ]
    if len(reservations) == 0:
        return 0
    reservations.sort(key=lambda reservation: reservation.window_end, reverse=True)
    streak_count = 0
    last_counted_week = None
    today = datetime.now(tz=UTC)
    last_week = (today - timedelta(weeks=1)).isocalendar()[:2]
    anchor_date = today
    for reservation in reservations:
        if reservation.window_end > today:
            continue
        if reservation.collected_at is None:
            break
        check_week = reservation.window_start.date().isocalendar()[:2]
        if check_week == last_counted_week:
            continue
        if last_counted_week is None and check_week == last_week:
            anchor_date = today - timedelta(weeks=1)
        expected_week = (anchor_date - timedelta(weeks=streak_count)).isocalendar()[:2]
        if check_week == expected_week:
            streak_count += 1
            last_counted_week = check_week
        else:
            break

    return streak_count
