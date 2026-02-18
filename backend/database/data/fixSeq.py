"""Fixes index shift after manual id insertion."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

script_dir = Path(__file__).resolve().parent

env_path = None
for parent in [script_dir, *list(script_dir.parents)]:
    possible_path = parent / ".env"
    if possible_path.exists():
        env_path = possible_path
        break

if not env_path:
    print("Error: Could not find .env file in any parent directory.")
    sys.exit(1)

print(f"Loaded .env from: {env_path}")
load_dotenv(dotenv_path=env_path)
user = os.getenv("DATABASE_USERNAME")
pw = os.getenv("DATABASE_PASSWORD")
host = os.getenv("DATABASE_HOST")
port = os.getenv("DATABASE_PORT")
db = os.getenv("DATABASE_DATABASE")
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
