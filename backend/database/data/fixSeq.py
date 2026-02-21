"""Fixes index shift after manual id insertion."""

from internal.settings.env import database_settings
from sqlalchemy import create_engine, text

user = database_settings.username
pw = database_settings.password
host = database_settings.host
port = database_settings.port
db = database_settings.database
url = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
engine = create_engine(url)


def fix_sequences() -> None:
    """Fixes index shift after manual id insertion."""
    print("Fixing auto-increment sequences...")
    with engine.connect() as conn:
        tables = [
            ("users", "user_id"),
            ("bundles", "bundle_id"),
            ("reservations", "reservation_id"),
            ("seller_issue_reports", "report_id"),
            ("admin_issue_reports", "report_id"),
            ("inbox", "message_id"),
            ("token", "token_id"),
            ("allergens", "allergen_id"),
            ("category", "category_id"),
        ]

        for table, pk in tables:
            query = text(f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', '{pk}'),
                    COALESCE((SELECT MAX({pk}) FROM {table}), 1)
                );
            """)  # noqa: S608
            conn.execute(query)
            print(f"Fixed sequence for: {table}")
        conn.commit()


if __name__ == "__main__":
    fix_sequences()
