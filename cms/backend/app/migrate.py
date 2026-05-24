"""Lightweight schema migrations for SQLite/MySQL (add missing columns/tables)."""

from sqlalchemy import inspect, text

from app.database import Base, engine


def column_exists(table: str, column: str) -> bool:
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return False
    return column in {c["name"] for c in insp.get_columns(table)}


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)
    dialect = engine.dialect.name
    alters = [
        ("users", "totp_secret", "VARCHAR(64)"),
        ("users", "totp_enabled", "BOOLEAN DEFAULT 0"),
        ("pages", "locale", "VARCHAR(10) DEFAULT 'en'"),
        ("pages", "publish_path", "VARCHAR(500)"),
        ("posts", "locale", "VARCHAR(10) DEFAULT 'en'"),
        ("posts", "primary_keyword", "VARCHAR(200)"),
        ("posts", "intro_hook", "TEXT"),
    ]
    with engine.begin() as conn:
        for table, col, col_type in alters:
            if not column_exists(table, col):
                if dialect == "sqlite":
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                else:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
