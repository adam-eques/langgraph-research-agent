"""Initialize the Postgres + pgvector database schema."""
from __future__ import annotations

import argparse
import os
import sys


def init_pgvector(dsn: str) -> None:
    try:
        import psycopg
    except ImportError:
        print("ERROR: psycopg not installed. Run: pip install psycopg[binary]")
        sys.exit(1)

    print(f"Connecting to: {dsn[:30]}...")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("pgvector extension: OK")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS langchain_pg_collection (
                    name VARCHAR NOT NULL,
                    cmetadata JSON,
                    uuid UUID NOT NULL,
                    PRIMARY KEY (uuid)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
                    collection_id UUID REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
                    embedding vector,
                    document VARCHAR,
                    cmetadata JSON,
                    custom_id VARCHAR,
                    uuid UUID NOT NULL,
                    PRIMARY KEY (uuid)
                );
            """)
            conn.commit()
            print("Tables: OK")
    print("Database initialization complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize pgvector schema")
    parser.add_argument("--dsn", default=os.getenv("DATABASE_URL"), help="Postgres DSN")
    args = parser.parse_args()
    if not args.dsn:
        print("ERROR: --dsn or DATABASE_URL is required")
        sys.exit(1)
    init_pgvector(args.dsn)


if __name__ == "__main__":
    main()
