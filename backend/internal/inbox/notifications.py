"""Helpers for creating user inbox notifications."""

from sqlalchemy.ext.asyncio import AsyncConnection

from internal.queries.inbox import AsyncQuerier as InboxQuerier
from internal.queries.inbox import CreateInboxMessageParams


async def send_notification(
    conn: AsyncConnection, *, user_id: int, sender_id: int, subject: str, text: str
) -> None:
    """Send an inbox notification."""
    await InboxQuerier(conn).create_inbox_message(
        CreateInboxMessageParams(
            user_id=user_id,
            sender_id=sender_id,
            message_subject=subject,
            message_text=text,
        )
    )
